import os
import uuid
import json
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
    context: Optional[Source]= None


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

    client = QdrantClient(url="https://82a7b166-2b70-4aae-b0c3-9d9dc30376d2.europe-west3-0.gcp.cloud.qdrant.io:6333",api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.F4QWTFU99XqIaATjqwlSDBz-ENANbYs21BqLZ1cWooM", timeout=60.0)
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


import traceback
import time
import json

@app.post("/query", response_model=QueryResponse)
async def query_doc(req: QueryRequest):
    """Retrieves top chunks from Qdrant, generates answer, and logs evaluation metrics."""
    if req.doc_id not in DOC_STORE:
        raise HTTPException(status_code=404, detail="Document not found")

    failure_stage = "initialization"

    try:
        # ------------------------------------------------------------
        # LOAD DOCUMENT
        # ------------------------------------------------------------
        failure_stage = "loading doc store"
        doc_info = DOC_STORE[req.doc_id]
        client = doc_info["client"]
        collection = doc_info["collection"]

        # ------------------------------------------------------------
        # 1. EMBEDDING
        # ------------------------------------------------------------
        failure_stage = "embedding query"
        start_total = time.time()

        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_emb = model.encode(req.query)

        # ------------------------------------------------------------
        # 2. RETRIEVAL
        # ------------------------------------------------------------
        failure_stage = "retrieving from Qdrant"
        start_retrieval = time.time()

        qdrant_res = client.query_points(
            collection_name=collection,
            query=query_emb.tolist(),
            with_payload=True,
            limit=5
        )
        hits = qdrant_res.points

        retrieval_time = (time.time() - start_retrieval) * 1000

        # ------------------------------------------------------------
        # 3. PROCESS RETRIEVAL
        # ------------------------------------------------------------
        failure_stage = "processing qdrant payloads"
        context = []
        context_text = ""
        retrieved_ids = []
        best_hit = None

        for h in hits:
            if best_hit is None or h.score > best_hit.score:
                best_hit = h

            payload = h.payload or {}
            page = payload.get("page")
            text = payload.get("text")

            context.append({
                "page": page,
                "text": text,
                "score": h.score,
            })

            context_text += f"\n(Page {page}) {text}"

        # Extract single best source
        best_source = None
        if best_hit is not None:
            p = best_hit.payload
            full_text = p.get("text", "")
            best_source = {
                "page": p.get("page"),
                "text": full_text[:100] + "..." if len(full_text) > 100 else full_text
            }

        # ------------------------------------------------------------
        # 4. GENERATION (FLASH)
        # ------------------------------------------------------------
        failure_stage = "generating with Gemini FLASH"

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

        answer_text = response.text

        # ------------------------------------------------------------
        # 5. METRIC EVALUATION
        # ------------------------------------------------------------
        failure_stage = "evaluating answer"

        metrics = evaluate_answer(
            query=req.query,
            answer=answer_text,
            retrieved_docs=context,          # list of dicts with 'text'
            relevant_docs=[c['text'] for c in context[:3]]  # example ground truth
        )


        metrics["Retrieval(ms)"] = round(retrieval_time, 2)
        metrics["Generation(ms)"] = round(generation_time, 2)
        metrics["Total(ms)"] = round(total_time, 2)

        log_metrics(req.query, answer_text, metrics)

        print("\n===== QUERY EVALUATION METRICS =====")
        for k, v in metrics.items():
            print(f"{k}: {v}")
        print("=====================================\n")

        # ------------------------------------------------------------
        # 6. FINAL RETURN (Matches QueryResponse)
        # ------------------------------------------------------------
        return {
            "answer": answer_text,
            "source": best_source
        }

    except Exception as e:
        error_trace = traceback.format_exc()

        detailed_error = {
            "error": str(e),
            "error_type": type(e).__name__,
            "failed_at": failure_stage,
            "stack_trace": error_trace
        }

        print("\n========== QUERY ERROR DETAILS ==========")
        print(json.dumps(detailed_error, indent=4))
        print("==========================================\n")

        raise HTTPException(
            status_code=500,
            detail=f"Query failed at stage '{failure_stage}': {type(e).__name__} → {str(e)}"
        )
