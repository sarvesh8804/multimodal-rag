import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Union

from dotenv import load_dotenv
import fitz # PyMuPDF
from PIL import Image
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import google.generativeai as genai
import shutil
import time 
import pytesseract
from metrics import calculate_recall_precision, calculate_semantic_similarity, calculate_faithfulness

import numpy as np
# 1. Configure Tesseract Path (MUST BE CORRECT for your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# --- Configuration & Initialization ---
# 2 gemini models used 1 for image 1 for text
# 1. Load environment variables
load_dotenv()

# --- DUAL KEY SETUP ---
# MODEL 1 (PRO): Used once for accurate Multimodal Extraction (Caching)
IMAGE_MODEL_NAME = "gemini-2.5-flash" 
IMAGE_API_KEY = os.getenv("GEMINI_API")

# MODEL 2 (FLASH): Used for all text RAG and Final Synthesis (High RPM/RPD)
TEXT_MODEL_NAME = "gemini-2.5-flash"
TEXT_API_KEY = os.getenv("GEMINI_API_NEW")

# Qdrant config
QDRANT_URL = os.environ.get("QDRANT_URL")
QDRANT_API_KEY = os.environ.get("QDRANT_API")

# Global variables
TEMP_DIR = "extracted_images"
DOC_STORE = {} 

try:
    if not IMAGE_API_KEY or not TEXT_API_KEY:
        raise ValueError("Both GEMINI_API_PRO and GEMINI_API_FLASH must be set.")
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise ValueError("QDRANT_URL and QDRANT_API must be set.")

    # Initialize Embedding Model (local and fast)
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Initialize a base configuration (will be swapped dynamically)
    genai.configure(api_key=TEXT_API_KEY)

except Exception as e:
    print(f"🚨 Fatal Error during initial setup: {e}")
    exit()

# -------------------
# FastAPI app config
# -------------------
app = FastAPI(title="Hybrid MRAG Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files (PDFs) so frontend can display them via iframe
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# -------------------
# Pydantic Models
# -------------------
class QueryRequest(BaseModel):
    doc_id: str
    query: str

class QueryResponse(BaseModel):
    answer: str
    context: List[Dict[str, Any]]

# -------------------
# RAG Utility Functions
# -------------------

# -----------------------
# Step 1: Extract text and images from PDF
# -----------------------
def extract_pdf_content(pdf_path: str) -> tuple[List[str], List[str]]:
    """Extracts text from PDF pages and saves pages as temporary images."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)
    
    doc = fitz.open(pdf_path)
    texts = []
    image_paths = []
    
    for i, page in enumerate(doc):
        texts.append(page.get_text())
        # Use 150 DPI for a balance between detail and file size
        pix = page.get_pixmap(dpi=150) 
        img_path = os.path.join(TEMP_DIR, f"page_{i}.png")
        pix.save(img_path)
        image_paths.append(img_path)
    
    return texts, image_paths

# -----------------------
# Step 2 & 3: OCR and Chunking 
# -----------------------
def ocr_images(image_paths: List[str]) -> List[str]:
    """Performs OCR on the saved images to extract text."""
    ocr_texts = []
    for img_path in image_paths:
        try:
            img = Image.open(img_path)
            text = pytesseract.image_to_string(img, lang='eng')
            ocr_texts.append(text)
        except:
            ocr_texts.append("")
    return ocr_texts

def chunk_text(texts: List[str], chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict[str, Any]]:
    """Splits text into manageable chunks and formats for Qdrant payload."""
    output_list = []
    for page_num, text in enumerate(texts):
        words = text.split()
        start = 0
        chunk_idx = 1
        while start < len(words):
            chunk_words = words[start:start+chunk_size]
            chunk_text = " ".join(chunk_words)
            output_list.append({
                "page": page_num,
                "text": f"Page {page_num} text chunk {chunk_idx}: {chunk_text}"
            })
            start += (chunk_size - chunk_overlap)
            chunk_idx += 1
    return output_list

# -----------------------
# Step 4: Multimodal Extractor (CACHING) - USES PRO KEY
# -----------------------
def automated_multimodal_extractor(image_paths: List[str]) -> Dict[str, str]:
    """
    Automates filtering and description generation using the PRO model (one-time high-accuracy caching).
    Caches rich descriptive summaries.
    """
    print("Starting ONE-TIME PRO-MODEL image caching...")
    
    # --- DYNAMIC KEY SWAP (PRO) ---
    genai.configure(api_key=IMAGE_API_KEY)
    pro_model = genai.GenerativeModel(model_name=IMAGE_MODEL_NAME)
    
    graph_data: Dict[str, str] = {}
    
    for i, image_path in enumerate(image_paths):
        try:
            page_image = Image.open(image_path)
            
            # 1. Filtering Prompt
            filter_prompt = "Does this image contain a data visualization, diagram, or process flow chart? Respond ONLY with 'YES' or 'NO'."
            
            filter_response = pro_model.generate_content(
                contents=[filter_prompt, page_image]
            ).text.strip().upper()
            
            time.sleep(12) # Safe delay for Pro's 5 RPM limit

            if "YES" in filter_response:
                # 2. Extraction Prompt: Request a comprehensive description
                description_query = (
                    "Generate a concise, detailed, and comprehensive text description "
                    "of the image content. Focus on any processes, steps, labels, or structured data found. "
                    f"Start your response with 'Figure on Page {i}:'"
                )
                
                data_response = pro_model.generate_content(
                    contents=[description_query, page_image]
                ).text
                
                graph_data[f"Page {i}"] = data_response
                time.sleep(12) # Another safe delay after successful extraction
            
        except Exception as e:
            # Silence specific error types but respect delay
            time.sleep(5) 
            
    print("Multimodal image extraction complete.")
    return graph_data

# -----------------------
# Step 5: Embed and store into Qdrant
# -----------------------
def embed_and_store(output_list: List[Dict[str, Any]], collection: str) -> QdrantClient:
    """Embeds chunks and stores them in Qdrant."""
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

# -------------------
# API Endpoints
# -------------------
@app.get("/health")
async def health():
    return {"status": "ok", "backend": "running"}

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Uploads, extracts, caches visual data, and embeds chunks into Qdrant."""
    try:
        doc_id = str(uuid.uuid4())
        filename = f"uploads/{doc_id}_{file.filename}"
        os.makedirs("uploads", exist_ok=True)

        with open(filename, "wb") as f:
            # Temporarily save the uploaded file
            content = await file.read()
            f.write(content)
            
        # 1. Extract text, OCR, and get page image paths
        raw_texts, image_paths = extract_pdf_content(filename)
        ocr_texts = ocr_images(image_paths)
        
        # 2. Multimodal Caching (Expensive step, run once using PRO KEY)
        graph_cache = automated_multimodal_extractor(image_paths)
        
        # 3. Consolidate ALL content for embedding
        output_list = []
        
        # 3a. Add original and OCR text chunks
        for text in raw_texts + ocr_texts:
            # Using chunk_text to break down the extracted and OCR text
            output_list.extend(chunk_text([text])) 
            
        # 3b. Add cached visual descriptions as highly-valuable text chunks
        for page_key, description in graph_cache.items():
            output_list.append({
                "page": int(page_key.split()[-1]),
                "text": f"VISUAL CACHE: {description}"
            })
            
        # 4. Embed and store all chunks
        collection_name = f"pdf_{doc_id}"
        client = embed_and_store(output_list, collection=collection_name)

        # Store document metadata and the rich graph cache
        DOC_STORE[doc_id] = {
            "filename": file.filename,
            "client": client,
            "collection": collection_name,
            "graph_cache": graph_cache
        }

        return {
            "status": "success", 
            "message": "PDF processed and multimodal cache built successfully.", 
            "doc_id": doc_id, 
            "filename": file.filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


# @app.post("/query", response_model=QueryResponse)
# async def query_doc(req: QueryRequest):
#     """Retrieves context from Qdrant and uses the high-RPM FLASH model for synthesis."""
#     if req.doc_id not in DOC_STORE:
#         raise HTTPException(status_code=404, detail="Document not found")

#     try:
#         doc_info = DOC_STORE[req.doc_id]
#         client = doc_info["client"]
#         collection = doc_info["collection"]

#         # 1. Embed query locally
#         model = SentenceTransformer("all-MiniLM-L6-v2")
#         query_emb = model.encode(req.query)

#         # 2. Retrieve relevant chunks (text and cached descriptions)
#         hits = client.search(collection_name=collection, query_vector=query_emb.tolist(), limit=5)

#         context = []
#         context_text = ""
#         for h in hits:
#             payload = h.payload
#             context.append({"page": payload['page'], "text": payload['text'], "score": h.score})
#             context_text += f"\n(Page {payload['page']}) {payload['text']}"

#         # 3. Use FLASH KEY for Synthesis (High-volume task)
#         # --- DYNAMIC KEY SWAP (FLASH) ---
#         genai.configure(api_key=TEXT_API_KEY)
#         flash_model = genai.GenerativeModel(model_name=TEXT_MODEL_NAME)

#         gemini_prompt = f"""You are a helpful assistant and expert document analyst.
# Use ONLY the following context to answer the user's query.
# The context includes standard text chunks and cached visual descriptions.
# If the answer relies on numerical data or diagrams, prioritize the details from the 'VISUAL CACHE' entries.

# Context:
# {context_text}

# Query:
# {req.query}
# """
#         # Call the high-RPM model
#         response = flash_model.generate_content(gemini_prompt)

#         return {"answer": response.text, "context": context}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/docs_list")
async def list_docs():
    return [{"doc_id": doc_id, "filename": info["filename"]} for doc_id, info in DOC_STORE.items()]



@app.post("/query", response_model=QueryResponse)
async def query_doc(req: QueryRequest):
    """Retrieves context from Qdrant, uses FLASH model for synthesis, and evaluates performance."""
    if req.doc_id not in DOC_STORE:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        doc_info = DOC_STORE[req.doc_id]
        client = doc_info["client"]
        collection = doc_info["collection"]

        start_total = time.time()

        # 1. Embed query locally
        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_emb = model.encode(req.query)

        # 2. Retrieve relevant chunks
        start_retrieval = time.time()
        hits = client.search(collection_name=collection, query_vector=query_emb.tolist(), limit=5)
        retrieval_time = (time.time() - start_retrieval) * 1000  # ms

        context = []
        context_text = ""
        retrieved_ids = []
        for idx, h in enumerate(hits):
            payload = h.payload
            context.append({"id": idx, "page": payload['page'], "text": payload['text'], "score": h.score})
            context_text += f"\n(Page {payload['page']}) {payload['text']}"
            retrieved_ids.append(idx)

        # 3. Use FLASH KEY for Synthesis
        genai.configure(api_key=TEXT_API_KEY)
        flash_model = genai.GenerativeModel(model_name=TEXT_MODEL_NAME)

        gemini_prompt = f"""You are a helpful assistant and expert document analyst.
Use ONLY the following context to answer the user's query.
The context includes standard text chunks and cached visual descriptions.
If the answer relies on numerical data or diagrams, prioritize the details from the 'VISUAL CACHE' entries.

Context:
{context_text}

Query:
{req.query}
"""
        start_gen = time.time()
        response = flash_model.generate_content(gemini_prompt)
        generation_time = (time.time() - start_gen) * 1000  # ms

        total_time = (time.time() - start_total) * 1000  # ms

        # ----------------------------
        # 4. Evaluate Metrics (Console Output)
        # ----------------------------
        # If you have a ground truth answer for testing, set it here:
        ground_truth = "Expected correct answer for testing"
        ground_truth_ids = [0, 1]  # example top-k relevant chunk IDs

        recall_precision = calculate_recall_precision(retrieved_ids, ground_truth_ids)
        semantic_similarity = calculate_semantic_similarity(response.text, ground_truth)
        faithfulness_score = calculate_faithfulness(context_text, response.text)

        print("\n===== QUERY EVALUATION METRICS =====")
        print(f"Query: {req.query}")
        print(f"Answer: {response.text}")
        print(f"Recall@k: {recall_precision['recall@k']:.2f}")
        print(f"Precision@k: {recall_precision['precision@k']:.2f}")
        print(f"Semantic Similarity: {semantic_similarity:.2f}")
        print(f"Faithfulness Score: {faithfulness_score:.2f}")
        print(f"Retrieval Time (ms): {retrieval_time:.2f}")
        print(f"Generation Time (ms): {generation_time:.2f}")
        print(f"Total Time (ms): {total_time:.2f}")
        print("====================================\n")

        # 5. Return normal API response
        return {"answer": response.text, "context": context}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
