import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Union
from dotenv import load_dotenv
import fitz  # PyMuPDF
from PIL import Image
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import google.generativeai as genai
import shutil
import time
import pytesseract
import numpy as np

# ✅ Import new evaluation functions
from metrics import evaluate_answer, log_metrics

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
load_dotenv()

IMAGE_MODEL_NAME = "gemini-2.5-flash"
TEXT_MODEL_NAME = "gemini-2.5-flash"
# IMAGE_MODEL_NAME = "gemma-3-27b"
# TEXT_MODEL_NAME = "gemma-3-27b"

IMAGE_API_KEY = os.getenv("GEMINI_API")
TEXT_API_KEY = os.getenv("GEMINI_API_NEW")

QDRANT_URL = os.environ.get("QDRANT_URL")
QDRANT_API_KEY = os.environ.get("QDRANT_API")

TEMP_DIR = "extracted_images"
DOC_STORE = {}

if not IMAGE_API_KEY or not TEXT_API_KEY:
    raise ValueError("Both GEMINI_API and GEMINI_API_NEW must be set.")
if not QDRANT_URL or not QDRANT_API_KEY:
    raise ValueError("QDRANT_URL and QDRANT_API must be set.")

# Local embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Configure Gemini
genai.configure(api_key=TEXT_API_KEY)

# ------------------------------------------------------------
# FASTAPI APP
# ------------------------------------------------------------
app = FastAPI(title="Hybrid MRAG Backend", version="2.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ------------------------------------------------------------
# DATA MODELS

# ------------------------------------------------------------


from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Source(BaseModel):
    page: int
    text: str

class QueryRequest(BaseModel):
    doc_id: str
    query: str


class QueryResponse(BaseModel):
    answer: str
    source: Optional[Source]

# ------------------------------------------------------------
# UTILITY FUNCTIONS
# ------------------------------------------------------------
def extract_pdf_content(pdf_path: str):
    """Extracts text and saves page images."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)

    doc = fitz.open(pdf_path)
    texts, image_paths = [], []
    for i, page in enumerate(doc):
        texts.append(page.get_text())
        pix = page.get_pixmap(dpi=150)
        img_path = os.path.join(TEMP_DIR, f"page_{i}.png")
        pix.save(img_path)
        image_paths.append(img_path)
    return texts, image_paths


def ocr_images(image_paths: List[str]):
    """Extract text from images using OCR."""
    ocr_texts = []
    for img_path in image_paths:
        try:
            img = Image.open(img_path)
            text = pytesseract.image_to_string(img, lang="eng")
            ocr_texts.append(text)
        except Exception:
            ocr_texts.append("")
    return ocr_texts


def chunk_text(texts: List[str], chunk_size: int = 500, chunk_overlap: int = 50):
    """Splits text into overlapping chunks for embedding."""
    output_list = []
    for page_num, text in enumerate(texts):
        words = text.split()
        start, chunk_idx = 0, 1
        while start < len(words):
            chunk_words = words[start:start + chunk_size]
            chunk_text = " ".join(chunk_words)
            output_list.append({
                "page": page_num,
                "text": f"Page {page_num} chunk {chunk_idx}: {chunk_text}"
            })
            start += (chunk_size - chunk_overlap)
            chunk_idx += 1
    return output_list


def automated_multimodal_extractor(image_paths: List[str]):
    """Uses PRO model to extract visual info (only once)."""
    genai.configure(api_key=IMAGE_API_KEY)
    pro_model = genai.GenerativeModel(model_name=IMAGE_MODEL_NAME)
    graph_data = {}

    for i, img_path in enumerate(image_paths):
        try:
            img = Image.open(img_path)
            filter_prompt = "Does this image contain a chart or diagram? Reply YES or NO."
            resp = pro_model.generate_content([filter_prompt, img]).text.strip().upper()
            time.sleep(8)

            if "YES" in resp:
                desc_prompt = (
                    f"Describe this figure from Page {i} in detail — steps, labels, and data."
                )
                data = pro_model.generate_content([desc_prompt, img]).text
                graph_data[f"Page {i}"] = data
                time.sleep(8)
        except Exception:
            time.sleep(5)

    return graph_data


def embed_and_store(output_list, collection: str):
    """Embeds text chunks and stores in Qdrant."""
    data = []
    for idx, item in enumerate(output_list):
        emb = embed_model.encode(item["text"])
        data.append({"id": idx, "vector": emb.tolist(), "payload": item})

    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60.0)
    if not client.collection_exists(collection):
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=len(data[0]["vector"]), distance=Distance.COSINE)
        )

    points = [PointStruct(id=d["id"], vector=d["vector"], payload=d["payload"]) for d in data]
    client.upsert(collection_name=collection, points=points, wait=True)
    return client

# ------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "backend": "running"}


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Uploads PDF, extracts data, builds multimodal cache, embeds into Qdrant."""
    try:
        doc_id = str(uuid.uuid4())
        filename = f"uploads/{doc_id}_{file.filename}"

        with open(filename, "wb") as f:
            f.write(await file.read())

        raw_texts, image_paths = extract_pdf_content(filename)
        ocr_texts = ocr_images(image_paths)
        graph_cache = automated_multimodal_extractor(image_paths)

        output_list = []
        for text in raw_texts + ocr_texts:
            output_list.extend(chunk_text([text]))

        for page_key, desc in graph_cache.items():
            output_list.append({
                "page": int(page_key.split()[-1]),
                "text": f"VISUAL CACHE: {desc}"
            })

        collection_name = f"pdf_{doc_id}"
        client = embed_and_store(output_list, collection_name)

        DOC_STORE[doc_id] = {
            "filename": file.filename,
            "client": client,
            "collection": collection_name,
            "graph_cache": graph_cache
        }

        return {
            "status": "success",
            "message": "PDF processed successfully.",
            "doc_id": doc_id,
            "filename": file.filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/docs_list")
async def list_docs():
    return [{"doc_id": doc_id, "filename": info["filename"]} for doc_id, info in DOC_STORE.items()]


@app.post("/query", response_model=QueryResponse)
async def query_doc(req: QueryRequest):
    """Retrieves context from Qdrant, generates answer, and logs accurate metrics."""
    if req.doc_id not in DOC_STORE:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        doc_info = DOC_STORE[req.doc_id]
        client = doc_info["client"]
        collection = doc_info["collection"]

        start_total = time.time()
        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_emb = model.encode(req.query)

        # Retrieve top-5 chunks
        start_retrieval = time.time()
        hits = client.search(collection_name=collection, query_vector=query_emb.tolist(), limit=5)
        retrieval_time = (time.time() - start_retrieval) * 1000

        context, context_text, retrieved_ids = [], "", []
        best_hit = None  # 🌟 NEW: To store the highest scoring chunk
        
        for i, h in enumerate(hits):
            # 🌟 NEW: Track the best hit based on score (Qdrant results are often sorted by score already)
            if best_hit is None or h.score > best_hit.score:
                best_hit = h
            
            pid = getattr(h, "id", len(retrieved_ids))
            payload = h.payload
            # Note: keeping the full context list for logging/evaluation, but only using best_hit for frontend
            context.append({"id": pid, "page": payload.get("page"), "text": payload.get("text"), "score": h.score})
            context_text += f"\n(Page {payload.get('page')}) {payload.get('text')}"
            retrieved_ids.append(pid)
        
        # 🌟 NEW: Format the single best source object for the frontend
        best_source_payload = None
        if best_hit:
            best_source_payload = best_hit.payload
            # Extract only page and a snippet of text for the frontend
            best_source = {
                "page": best_source_payload.get("page"),
                # Truncate text to a reasonable length for the source snippet in the UI
                "text": best_source_payload.get("text")[:100].strip() + "..." if best_source_payload.get("text") and len(best_source_payload.get("text")) > 100 else best_source_payload.get("text")
            }


        # Generate response
        # ... (rest of the generation code is unchanged) ...
        genai.configure(api_key=TEXT_API_KEY)
        flash_model = genai.GenerativeModel(model_name=TEXT_MODEL_NAME)

        gemini_prompt = f"""
You are a helpful assistant. Use ONLY the context to answer the query.

Context:
{context_text}

Query:
{req.query}
"""
        start_gen = time.time()
        response = flash_model.generate_content(gemini_prompt)
        generation_time = (time.time() - start_gen) * 1000
        total_time = (time.time() - start_total) * 1000


       
        return {
            "answer": response.text, 
            "source": best_source if best_source_payload else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")