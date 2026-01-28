import os
import uuid
import time
import shutil
import base64
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

import fitz  # PyMuPDF
from PIL import Image
import pytesseract

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from openai import OpenAI

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API")

if not OPENROUTER_API_KEY or not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError("Missing environment variables.")

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

TEMP_DIR = "extracted_images"
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

VISION_MODEL = "google/gemma-3-12b-it:free"
TEXT_MODEL = "google/gemma-3-4b-it:free"

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Hybrid-MRAG"
    }
)

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

DOC_STORE = {}

# -------------------------------------------------
# FASTAPI
# -------------------------------------------------

app = FastAPI(title="OpenRouter MRAG Backend", version="3.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# -------------------------------------------------
# DATA MODELS
# -------------------------------------------------

class Source(BaseModel):
    page: int
    text: str

class QueryRequest(BaseModel):
    doc_id: str
    query: str

class QueryResponse(BaseModel):
    answer: str
    source: Optional[Source]

# -------------------------------------------------
# UTILITIES
# -------------------------------------------------

def extract_pdf_content(pdf_path: str):
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
    results = []
    for p in image_paths:
        try:
            img = Image.open(p)
            results.append(pytesseract.image_to_string(img))
        except:
            results.append("")
    return results


def chunk_text(texts: List[str], chunk_size=500, overlap=50):
    chunks = []
    for page_num, text in enumerate(texts):
        words = text.split()
        start, idx = 0, 1
        while start < len(words):
            part = words[start:start + chunk_size]
            chunks.append({
                "page": page_num,
                "text": f"Page {page_num} chunk {idx}: {' '.join(part)}"
            })
            start += chunk_size - overlap
            idx += 1
    return chunks


def describe_image_openrouter(image_path: str) -> str:
    with open(image_path, "rb") as f:
        img64 = base64.b64encode(f.read()).decode()

    prompt = """
Describe this image in extreme detail:
- Chart or diagram type
- Axis labels
- Approximate numeric values
- Trends
- Colors
- Background
- UI elements
- Visual emphasis
- Hidden or subtle insights
"""

    res = openrouter_client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/png;base64,{img64}"}
            ]
        }],
        temperature=0.2
    )

    return res.choices[0].message.content


def automated_multimodal_extractor(image_paths: List[str]):
    graph_data = {}
    print("Extracting images using OpenRouter...")

    for i, p in enumerate(image_paths):
        try:
            desc = describe_image_openrouter(p)
            if desc and len(desc) > 50:
                graph_data[f"Page {i}"] = desc
        except Exception as e:
            print("Image extraction failed:", e)

        time.sleep(1)

    return graph_data


def embed_and_store(chunks, collection):
    points = []

    for idx, item in enumerate(chunks):
        vec = embed_model.encode(item["text"]).tolist()
        points.append(PointStruct(id=idx, vector=vec, payload=item))

    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    if not client.collection_exists(collection):
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=len(points[0].vector), distance=Distance.COSINE)
        )

    client.upsert(collection_name=collection, points=points, wait=True)
    return client


def generate_answer_openrouter(context: str, query: str) -> str:
    user_prompt = f"""
You are a precise document analyst.
Answer strictly using the provided context.
If the answer is missing, say "Not found in document".

Context:
{context}

Question:
{query}
"""

    res = openrouter_client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": user_prompt}],
        temperature=0.2,
        max_tokens=2048
    )

    return res.choices[0].message.content


# -------------------------------------------------
# ROUTES
# -------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        doc_id = str(uuid.uuid4())
        path = f"{UPLOAD_DIR}/{doc_id}_{file.filename}"

        with open(path, "wb") as f:
            f.write(await file.read())

        texts, images = extract_pdf_content(path)
        ocr_texts = ocr_images(images)
        graph_cache = automated_multimodal_extractor(images)

        chunks = []
        for t in texts + ocr_texts:
            chunks.extend(chunk_text([t]))

        for page_key, desc in graph_cache.items():
            chunks.append({
                "page": int(page_key.split()[-1]),
                "text": f"VISUAL CACHE: {desc}"
            })

        collection = f"pdf_{doc_id}"
        client = embed_and_store(chunks, collection)

        DOC_STORE[doc_id] = {
            "filename": file.filename,
            "client": client,
            "collection": collection
        }

        return {"status": "success", "doc_id": doc_id}

    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/docs_list")
async def list_docs():
    return [{"doc_id": k, "filename": v["filename"]} for k, v in DOC_STORE.items()]


@app.post("/query", response_model=QueryResponse)
async def query_doc(req: QueryRequest):
    if req.doc_id not in DOC_STORE:
        raise HTTPException(404, "Document not found")

    try:
        info = DOC_STORE[req.doc_id]
        client = info["client"]

        qvec = embed_model.encode(req.query).tolist()

        hits = client.search(
            collection_name=info["collection"],
            query_vector=qvec,
            limit=5
        )

        context_text = ""
        best_hit = None

        for h in hits:
            context_text += f"\n(Page {h.payload.get('page')}) {h.payload.get('text')}"
            if not best_hit or h.score > best_hit.score:
                best_hit = h

        answer = generate_answer_openrouter(context_text, req.query)

        source = None
        if best_hit:
            t = best_hit.payload["text"]
            source = {
                "page": best_hit.payload["page"],
                "text": t[:120] + "..." if len(t) > 120 else t
            }

        return {"answer": answer, "source": source}

    except Exception as e:
        raise HTTPException(500, str(e))


# -------------------------------------------------
# RUN
# -------------------------------------------------
# uvicorn main:app --reload
