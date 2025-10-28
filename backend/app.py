# import os
# import uuid
# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel
# from typing import List, Dict, Any, Union

# from dotenv import load_dotenv
# import fitz # PyMuPDF
# from PIL import Image
# from sentence_transformers import SentenceTransformer
# from qdrant_client import QdrantClient
# from qdrant_client.models import VectorParams, Distance, PointStruct
# import google.generativeai as genai
# import shutil
# import time 
# import pytesseract
# from metrics import calculate_recall_precision, calculate_semantic_similarity, calculate_faithfulness

# import numpy as np
# # 1. Configure Tesseract Path (MUST BE CORRECT for your system)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# # --- Configuration & Initialization ---
# # 2 gemini models used 1 for image 1 for text
# # 1. Load environment variables
# load_dotenv()

# # --- DUAL KEY SETUP ---
# # MODEL 1 (PRO): Used once for accurate Multimodal Extraction (Caching)
# IMAGE_MODEL_NAME = "gemini-2.5-flash" 
# IMAGE_API_KEY = os.getenv("GEMINI_API")

# # MODEL 2 (FLASH): Used for all text RAG and Final Synthesis (High RPM/RPD)
# TEXT_MODEL_NAME = "gemini-2.5-flash"
# TEXT_API_KEY = os.getenv("GEMINI_API_NEW")

# # Qdrant config
# QDRANT_URL = os.environ.get("QDRANT_URL")
# QDRANT_API_KEY = os.environ.get("QDRANT_API")

# # Global variables
# TEMP_DIR = "extracted_images"
# DOC_STORE = {} 

# try:
#     if not IMAGE_API_KEY or not TEXT_API_KEY:
#         raise ValueError("Both GEMINI_API_PRO and GEMINI_API_FLASH must be set.")
#     if not QDRANT_URL or not QDRANT_API_KEY:
#         raise ValueError("QDRANT_URL and QDRANT_API must be set.")

#     # Initialize Embedding Model (local and fast)
#     embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    
#     # Initialize a base configuration (will be swapped dynamically)
#     genai.configure(api_key=TEXT_API_KEY)

# except Exception as e:
#     print(f"🚨 Fatal Error during initial setup: {e}")
#     exit()

# # -------------------
# # FastAPI app config
# # -------------------
# app = FastAPI(title="Hybrid MRAG Backend", version="1.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Serve uploaded files (PDFs) so frontend can display them via iframe
# os.makedirs("uploads", exist_ok=True)
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# # -------------------
# # Pydantic Models
# # -------------------
# class QueryRequest(BaseModel):
#     doc_id: str
#     query: str

# class QueryResponse(BaseModel):
#     answer: str
#     context: List[Dict[str, Any]]

# # -------------------
# # RAG Utility Functions
# # -------------------

# # -----------------------
# # Step 1: Extract text and images from PDF
# # -----------------------
# def extract_pdf_content(pdf_path: str) -> tuple[List[str], List[str]]:
#     """Extracts text from PDF pages and saves pages as temporary images."""
#     if os.path.exists(TEMP_DIR):
#         shutil.rmtree(TEMP_DIR)
#     os.makedirs(TEMP_DIR)
    
#     doc = fitz.open(pdf_path)
#     texts = []
#     image_paths = []
    
#     for i, page in enumerate(doc):
#         texts.append(page.get_text())
#         # Use 150 DPI for a balance between detail and file size
#         pix = page.get_pixmap(dpi=150) 
#         img_path = os.path.join(TEMP_DIR, f"page_{i}.png")
#         pix.save(img_path)
#         image_paths.append(img_path)
    
#     return texts, image_paths

# # -----------------------
# # Step 2 & 3: OCR and Chunking 
# # -----------------------
# def ocr_images(image_paths: List[str]) -> List[str]:
#     """Performs OCR on the saved images to extract text."""
#     ocr_texts = []
#     for img_path in image_paths:
#         try:
#             img = Image.open(img_path)
#             text = pytesseract.image_to_string(img, lang='eng')
#             ocr_texts.append(text)
#         except:
#             ocr_texts.append("")
#     return ocr_texts

# def chunk_text(texts: List[str], chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict[str, Any]]:
#     """Splits text into manageable chunks and formats for Qdrant payload."""
#     output_list = []
#     for page_num, text in enumerate(texts):
#         words = text.split()
#         start = 0
#         chunk_idx = 1
#         while start < len(words):
#             chunk_words = words[start:start+chunk_size]
#             chunk_text = " ".join(chunk_words)
#             output_list.append({
#                 "page": page_num,
#                 "text": f"Page {page_num} text chunk {chunk_idx}: {chunk_text}"
#             })
#             start += (chunk_size - chunk_overlap)
#             chunk_idx += 1
#     return output_list

# # -----------------------
# # Step 4: Multimodal Extractor (CACHING) - USES PRO KEY
# # -----------------------
# def automated_multimodal_extractor(image_paths: List[str]) -> Dict[str, str]:
#     """
#     Automates filtering and description generation using the PRO model (one-time high-accuracy caching).
#     Caches rich descriptive summaries.
#     """
#     print("Starting ONE-TIME PRO-MODEL image caching...")
    
#     # --- DYNAMIC KEY SWAP (PRO) ---
#     genai.configure(api_key=IMAGE_API_KEY)
#     pro_model = genai.GenerativeModel(model_name=IMAGE_MODEL_NAME)
    
#     graph_data: Dict[str, str] = {}
    
#     for i, image_path in enumerate(image_paths):
#         try:
#             page_image = Image.open(image_path)
            
#             # 1. Filtering Prompt
#             filter_prompt = "Does this image contain a data visualization, diagram, or process flow chart? Respond ONLY with 'YES' or 'NO'."
            
#             filter_response = pro_model.generate_content(
#                 contents=[filter_prompt, page_image]
#             ).text.strip().upper()
            
#             time.sleep(12) # Safe delay for Pro's 5 RPM limit

#             if "YES" in filter_response:
#                 # 2. Extraction Prompt: Request a comprehensive description
#                 description_query = (
#                     "Generate a concise, detailed, and comprehensive text description "
#                     "of the image content. Focus on any processes, steps, labels, or structured data found. "
#                     f"Start your response with 'Figure on Page {i}:'"
#                 )
                
#                 data_response = pro_model.generate_content(
#                     contents=[description_query, page_image]
#                 ).text
                
#                 graph_data[f"Page {i}"] = data_response
#                 time.sleep(12) # Another safe delay after successful extraction
            
#         except Exception as e:
#             # Silence specific error types but respect delay
#             time.sleep(5) 
            
#     print("Multimodal image extraction complete.")
#     return graph_data

# # -----------------------
# # Step 5: Embed and store into Qdrant
# # -----------------------
# def embed_and_store(output_list: List[Dict[str, Any]], collection: str) -> QdrantClient:
#     """Embeds chunks and stores them in Qdrant."""
#     data = []
    
#     for idx, item in enumerate(output_list):
#         emb = embed_model.encode(item["text"])
#         data.append({"id": idx, "vector": emb.tolist(), "payload": item})

#     client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60.0)

#     if not client.collection_exists(collection):
#         client.create_collection(
#             collection_name=collection,
#             vectors_config=VectorParams(size=len(data[0]["vector"]), distance=Distance.COSINE)
#         )

#     points = [PointStruct(id=d["id"], vector=d["vector"], payload=d["payload"]) for d in data]
#     client.upsert(collection_name=collection, points=points, wait=True)
    
#     return client

# # -------------------
# # API Endpoints
# # -------------------
# @app.get("/health")
# async def health():
#     return {"status": "ok", "backend": "running"}

# @app.post("/upload_pdf")
# async def upload_pdf(file: UploadFile = File(...)):
#     """Uploads, extracts, caches visual data, and embeds chunks into Qdrant."""
#     try:
#         doc_id = str(uuid.uuid4())
#         filename = f"uploads/{doc_id}_{file.filename}"
#         os.makedirs("uploads", exist_ok=True)

#         with open(filename, "wb") as f:
#             # Temporarily save the uploaded file
#             content = await file.read()
#             f.write(content)
            
#         # 1. Extract text, OCR, and get page image paths
#         raw_texts, image_paths = extract_pdf_content(filename)
#         ocr_texts = ocr_images(image_paths)
        
#         # 2. Multimodal Caching (Expensive step, run once using PRO KEY)
#         graph_cache = automated_multimodal_extractor(image_paths)
        
#         # 3. Consolidate ALL content for embedding
#         output_list = []
        
#         # 3a. Add original and OCR text chunks
#         for text in raw_texts + ocr_texts:
#             # Using chunk_text to break down the extracted and OCR text
#             output_list.extend(chunk_text([text])) 
            
#         # 3b. Add cached visual descriptions as highly-valuable text chunks
#         for page_key, description in graph_cache.items():
#             output_list.append({
#                 "page": int(page_key.split()[-1]),
#                 "text": f"VISUAL CACHE: {description}"
#             })
            
#         # 4. Embed and store all chunks
#         collection_name = f"pdf_{doc_id}"
#         client = embed_and_store(output_list, collection=collection_name)

#         # Store document metadata and the rich graph cache
#         DOC_STORE[doc_id] = {
#             "filename": file.filename,
#             "client": client,
#             "collection": collection_name,
#             "graph_cache": graph_cache
#         }

#         return {
#             "status": "success", 
#             "message": "PDF processed and multimodal cache built successfully.", 
#             "doc_id": doc_id, 
#             "filename": file.filename
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


# # @app.post("/query", response_model=QueryResponse)
# # async def query_doc(req: QueryRequest):
# #     """Retrieves context from Qdrant and uses the high-RPM FLASH model for synthesis."""
# #     if req.doc_id not in DOC_STORE:
# #         raise HTTPException(status_code=404, detail="Document not found")

# #     try:
# #         doc_info = DOC_STORE[req.doc_id]
# #         client = doc_info["client"]
# #         collection = doc_info["collection"]

# #         # 1. Embed query locally
# #         model = SentenceTransformer("all-MiniLM-L6-v2")
# #         query_emb = model.encode(req.query)

# #         # 2. Retrieve relevant chunks (text and cached descriptions)
# #         hits = client.search(collection_name=collection, query_vector=query_emb.tolist(), limit=5)

# #         context = []
# #         context_text = ""
# #         for h in hits:
# #             payload = h.payload
# #             context.append({"page": payload['page'], "text": payload['text'], "score": h.score})
# #             context_text += f"\n(Page {payload['page']}) {payload['text']}"

# #         # 3. Use FLASH KEY for Synthesis (High-volume task)
# #         # --- DYNAMIC KEY SWAP (FLASH) ---
# #         genai.configure(api_key=TEXT_API_KEY)
# #         flash_model = genai.GenerativeModel(model_name=TEXT_MODEL_NAME)

# #         gemini_prompt = f"""You are a helpful assistant and expert document analyst.
# # Use ONLY the following context to answer the user's query.
# # The context includes standard text chunks and cached visual descriptions.
# # If the answer relies on numerical data or diagrams, prioritize the details from the 'VISUAL CACHE' entries.

# # Context:
# # {context_text}

# # Query:
# # {req.query}
# # """
# #         # Call the high-RPM model
# #         response = flash_model.generate_content(gemini_prompt)

# #         return {"answer": response.text, "context": context}

# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

# @app.get("/docs_list")
# async def list_docs():
#     return [{"doc_id": doc_id, "filename": info["filename"]} for doc_id, info in DOC_STORE.items()]



# @app.post("/query", response_model=QueryResponse)
# async def query_doc(req: QueryRequest):
#     """Retrieves context from Qdrant, uses FLASH model for synthesis, and evaluates performance."""
#     if req.doc_id not in DOC_STORE:
#         raise HTTPException(status_code=404, detail="Document not found")

#     try:
#         doc_info = DOC_STORE[req.doc_id]
#         client = doc_info["client"]
#         collection = doc_info["collection"]

#         start_total = time.time()

#         # 1. Embed query locally
#         model = SentenceTransformer("all-MiniLM-L6-v2")
#         query_emb = model.encode(req.query)

#         # 2. Retrieve relevant chunks
#         start_retrieval = time.time()
#         hits = client.search(collection_name=collection, query_vector=query_emb.tolist(), limit=5)
#         retrieval_time = (time.time() - start_retrieval) * 1000  # ms

#         context = []
#         context_text = ""
#         retrieved_ids = []
#         for h in hits:
#             payload = h.payload
#             # use the vector id returned by Qdrant (h.id) to track which stored chunk was retrieved
#             hit_id = getattr(h, 'id', None) if hasattr(h, 'id') else h.id if hasattr(h, 'id') else None
#             # some qdrant clients expose id as 'id' or 'id' attr; fall back to payload-based index if missing
#             if hit_id is None:
#                 # best-effort: try score index
#                 hit_id = len(retrieved_ids)

#             context.append({"id": hit_id, "page": payload.get('page'), "text": payload.get('text'), "score": getattr(h, 'score', None)})
#             context_text += f"\n(Page {payload.get('page')}) {payload.get('text')}"
#             retrieved_ids.append(hit_id)

#         # 3. Use FLASH KEY for Synthesis
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
#         start_gen = time.time()
#         response = flash_model.generate_content(gemini_prompt)
#         generation_time = (time.time() - start_gen) * 1000  # ms

#         total_time = (time.time() - start_total) * 1000  # ms

#         # ----------------------------
#         # 4. Evaluate Metrics (Console Output)
#         # ----------------------------
#         # If you have a ground truth answer for testing, set it here:
#         ground_truth = "Expected correct answer for testing"
#         ground_truth_ids = [0, 1]  # example top-k relevant chunk IDs

#         # Compute and log metrics (note: ground_truth and ground_truth_ids are placeholders for testing)
#         recall_precision = calculate_recall_precision(retrieved_ids, ground_truth_ids)
#         semantic_similarity = calculate_semantic_similarity(response.text, ground_truth)
#         faithfulness_score = calculate_faithfulness(context_text, response.text)

#         # Log to CSV (and print a short summary). Replace ground_truth variables with real data in production.
#         try:
#             from .metrics import log_metrics
#         except Exception:
#             # relative import fallback
#             from metrics import log_metrics

#         log_metrics(
#             query=req.query,
#             ground_truth=ground_truth,
#             retrieved_chunks=context,
#             answer=response.text,
#             ground_truth_ids=ground_truth_ids,
#             retrieval_time_ms=retrieval_time,
#             generation_time_ms=generation_time,
#             total_time_ms=total_time,
#             k=5,
#         )

#         print("===== QUERY EVALUATION METRICS (summary) =====")
#         print(f"Query: {req.query}")
#         print(f"Answer (truncated): {response.text[:200]}")
#         print(f"Recall@5: {recall_precision['recall@k']:.3f}")
#         print(f"Precision@5: {recall_precision['precision@k']:.3f}")
#         print(f"Semantic Similarity (answer vs. truth): {semantic_similarity:.3f}")
#         print(f"Faithfulness (heuristic/LLM): {faithfulness_score:.3f}")
#         print(f"Retrieval: {retrieval_time:.1f} ms | Generation: {generation_time:.1f} ms | Total: {total_time:.1f} ms")
#         print("============================================\n")

#         # 5. Return normal API response
#         return {"answer": response.text, "context": context}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

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
class QueryRequest(BaseModel):
    doc_id: str
    query: str


class QueryResponse(BaseModel):
    answer: str
    context: List[Dict[str, Any]]

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
        for h in hits:
            pid = getattr(h, "id", len(retrieved_ids))
            payload = h.payload
            context.append({"id": pid, "page": payload.get("page"), "text": payload.get("text"), "score": h.score})
            context_text += f"\n(Page {payload.get('page')}) {payload.get('text')}"
            retrieved_ids.append(pid)

        # Generate response
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

        # ✅ Accurate Evaluation using new metrics.py
        ground_truth = 'The company\'s performance overview details robust revenue growth from 1996 to 1999, led by Licenses (18 SEK m to 83 SEK m), with strong growth also in Service contracts and Hardware. Product-wise, "FORMS" generated substantially higher license revenues than "INVOICES." The majority of license income comes from Europe (61%) and Sweden (23%). Strategically, the company covers an estimated 70% of the world market, with US sales organizations and plans to expand to Japan and another Asian market, using direct sales and distributors for local control. The Automatic Data Capture Market is described as young, growing, and largely untapped; its key customer benefits include reduced costs, increased accuracy, and shorter entry times'  # If testing, you can provide expected answer here
        metrics = evaluate_answer(
            query=req.query,
            answer=response.text,
            ground_truth=ground_truth,
            retrieved_docs=[c["text"] for c in context],
            relevant_ids=[],  # If known
            retrieved_ids=retrieved_ids
        )

        # Add timing to logs
        metrics["Retrieval(ms)"] = round(retrieval_time, 2)
        metrics["Generation(ms)"] = round(generation_time, 2)
        metrics["Total(ms)"] = round(total_time, 2)

        log_metrics(req.query, response.text, metrics)

        print("\n===== QUERY EVALUATION METRICS =====")
        for k, v in metrics.items():
            print(f"{k}: {v}")
        print("=====================================\n")

        return {"answer": response.text, "context": context}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
