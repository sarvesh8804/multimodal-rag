import os
import uuid
import time
import shutil
import fitz
import pytesseract
import requests
from PIL import Image
from typing import Optional
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

# ------------------------------------------------------------
# CONFIGURATION (ENV SAME AS YOUR GEMINI CODE)
# ------------------------------------------------------------
load_dotenv()

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

QDRANT_URL = os.environ.get("QDRANT_URL")
QDRANT_API_KEY = os.environ.get("QDRANT_API")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise ValueError("QDRANT_URL and QDRANT_API must be set.")

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "mistral:7b-instruct"

UPLOAD_DIR = "uploads"
IMAGE_DIR = "page_images"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

DOC_STORE = {}

# ------------------------------------------------------------
# MODELS
# ------------------------------------------------------------
embed_model = SentenceTransformer("BAAI/bge-base-en-v1.5")

device = "cuda" if torch.cuda.is_available() else "cpu"
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to(device)

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=60.0
)

# ------------------------------------------------------------
# FASTAPI APP
# ------------------------------------------------------------
app = FastAPI(title="Local Multimodal RAG Backend", version="3.0")

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# DATA MODELS
# ------------------------------------------------------------

class Source(BaseModel):
    page: int
    text: str

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    source: Optional[Source]


DOC_STORE = {}
LATEST_DOC_ID = None


# ------------------------------------------------------------
# UTILS
# ------------------------------------------------------------
def extract_pdf(pdf_path: str):
    doc = fitz.open(pdf_path)
    pages, images = [], []

    for i, page in enumerate(doc):
        text = page.get_text().strip()
        pages.append({"page": i, "text": text})

        pix = page.get_pixmap(dpi=200)
        img_path = f"{IMAGE_DIR}/page_{i}.png"
        pix.save(img_path)
        images.append((i, img_path))

    return pages, images


def ocr_image(path: str) -> str:
    img = Image.open(path)
    return pytesseract.image_to_string(img).strip()


def caption_image(path: str) -> str:
    img = Image.open(path).convert("RGB")
    inputs = blip_processor(img, return_tensors="pt").to(device)
    out = blip_model.generate(**inputs, max_new_tokens=80)
    return blip_processor.decode(out[0], skip_special_tokens=True)


def chunk_text(text: str, size=400, overlap=80):
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i:i + size]))
        i += size - overlap
    return chunks


def embed_and_store(chunks, collection):
    if not qdrant.collection_exists(collection):
        qdrant.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(
                size=embed_model.get_sentence_embedding_dimension(),
                distance=Distance.COSINE
            )
        )

    points = []
    for idx, c in enumerate(chunks):
        emb = embed_model.encode(c["text"]).tolist()
        points.append(PointStruct(id=idx, vector=emb, payload=c))

    qdrant.upsert(collection, points)


def call_llm(prompt: str) -> str:
    res = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "mistral:7b-instruct",
            "prompt": prompt,
            "stream": False
        },
        timeout=180
    )

    if res.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Ollama error {res.status_code}: {res.text}"
        )

    data = res.json()
    return data.get("response", "").strip()


# ------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "backend": "local-rag"}


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        doc_id = str(uuid.uuid4())
        # pdf_path = f"{UPLOAD_DIR}/{doc_id}.pdf"
        safe_name = file.filename.replace(" ", "_")
        pdf_filename = f"{doc_id}_{safe_name}"
        pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)


        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        pages, images = extract_pdf(pdf_path)
        chunks = []

        for p in pages:
            if len(p["text"]) < 50:
                ocr = ocr_image(f"{IMAGE_DIR}/page_{p['page']}.png")
                p["text"] += "\n" + ocr

            for ch in chunk_text(p["text"]):
                chunks.append({
                    "page": p["page"],
                    "type": "text",
                    "text": ch
                })

        for page, img_path in images:
            caption = caption_image(img_path)
            chunks.append({
                "page": page,
                "type": "image",
                "text": f"Image description: {caption}"
            })

        collection = f"pdf_{doc_id}"
        embed_and_store(chunks, collection)

        global LATEST_DOC_ID
        DOC_STORE[doc_id] = {"collection": collection}
        LATEST_DOC_ID = doc_id

        return {"status": "success", "doc_id": doc_id}

    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/query", response_model=QueryResponse)
def query_doc(req: QueryRequest):
    try:
        if not LATEST_DOC_ID or LATEST_DOC_ID not in DOC_STORE:
            return {
                "answer": "No document uploaded yet.",
                "source": None
            }

        collection = DOC_STORE[LATEST_DOC_ID]["collection"]
        query_emb = embed_model.encode(req.query).tolist()

        hits = qdrant.search(
            collection_name=collection,
            query_vector=query_emb,
            limit=5
        )

        if not hits:
            return {
                "answer": "No relevant information found in the document.",
                "source": None
            }

        context = ""
        for h in hits:
            context += f"\n(Page {h.payload['page']}) {h.payload['text']}"

        prompt = f"""
Answer ONLY using the context.

Context:
{context}

Question:
{req.query}
"""

        answer = call_llm(prompt)

        best = hits[0]

        return {
            "answer": answer.strip(),
            "source": {
                "page": best.payload["page"],
                "text": best.payload["text"][:120]
            }
        }

    except Exception as e:
        # 🔥 CRITICAL: never return None
        return {
            "answer": f"Error while processing query: {str(e)}",
            "source": None
        }
