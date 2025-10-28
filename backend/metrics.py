# """Evaluation metrics for the MRAG backend.

# Provides standard IR metrics (Precision@k, Recall@k, MRR, MAP@k, nDCG@k),
# semantic similarity (sentence-transformer cosine), ROUGE-L (LCS-based)
# and a faithfulness proxy combining ROUGE-L and semantic similarity. If
# an LLM grader (Gemini) is available via the GEMINI_API env var, it will be
# used as an optional faithfulness scorer.
# """

# import time
# import csv
# import math
# import os
# from typing import List, Dict, Any, Optional
# import numpy as np
# from sentence_transformers import SentenceTransformer, util

# try:
#     import google.generativeai as genai
#     GENAI_AVAILABLE = True
# except Exception:
#     GENAI_AVAILABLE = False

# # Initialize embedding model
# embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# # Optional LLM grader (Gemini). Only configured if environment variable is present.
# llm_grader = None
# if GENAI_AVAILABLE and os.getenv("GEMINI_API"):
#     try:
#         genai.configure(api_key=os.getenv("GEMINI_API"))
#         llm_grader = genai.GenerativeModel(model_name="gemini-2.5-flash")
#     except Exception:
#         llm_grader = None

# # CSV logging
# LOG_FILE = "rag_metrics_log.csv"
# CSV_HEADERS = [
#     "timestamp",
#     "query",
#     "ground_truth",
#     "retrieved_count",
#     "answer",
#     "k",
#     "recall@k",
#     "precision@k",
#     "mrr",
#     "map@k",
#     "ndcg@k",
#     "semantic_similarity",
#     "rouge_l",
#     "faithfulness_score",
#     "retrieval_time_ms",
#     "generation_time_ms",
#     "total_time_ms",
# ]

# if not os.path.exists(LOG_FILE):
#     with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(CSV_HEADERS)


# def precision_at_k(retrieved: List[int], ground_truth: List[int], k: int) -> float:
#     if k <= 0:
#         return 0.0
#     topk = retrieved[:k]
#     if not topk:
#         return 0.0
#     rel = sum(1 for r in topk if r in set(ground_truth))
#     return rel / len(topk)


# def recall_at_k(retrieved: List[int], ground_truth: List[int], k: Optional[int] = None) -> float:
#     if not ground_truth:
#         return 0.0
#     if k is None:
#         k = len(retrieved)
#     topk = retrieved[:k]
#     rel = sum(1 for r in topk if r in set(ground_truth))
#     return rel / len(ground_truth)


# def average_precision_at_k(retrieved: List[int], ground_truth: List[int], k: int) -> float:
#     if not ground_truth:
#         return 0.0
#     ap = 0.0
#     hit_count = 0
#     for i in range(1, k + 1):
#         if i > len(retrieved):
#             break
#         if retrieved[i - 1] in ground_truth:
#             hit_count += 1
#             ap += hit_count / i
#     return ap / min(len(ground_truth), k) if hit_count > 0 else 0.0


# def mean_reciprocal_rank(retrieved: List[int], ground_truth: List[int]) -> float:
#     for idx, r in enumerate(retrieved, start=1):
#         if r in ground_truth:
#             return 1.0 / idx
#     return 0.0


# def dcg_at_k(relevance: List[int], k: int) -> float:
#     dcg = 0.0
#     for i in range(min(len(relevance), k)):
#         rel = relevance[i]
#         denom = math.log2(i + 2)
#         dcg += (2 ** rel - 1) / denom
#     return dcg


# def ndcg_at_k(retrieved: List[int], ground_truth: List[int], k: int) -> float:
#     relevance = [1 if r in set(ground_truth) else 0 for r in retrieved[:k]]
#     dcg = dcg_at_k(relevance, k)
#     ideal_relevance = sorted(relevance, reverse=True)
#     idcg = dcg_at_k(ideal_relevance, k)
#     return dcg / idcg if idcg > 0 else 0.0


# # Compatibility wrapper (keeps older API used elsewhere in repo)
# def calculate_recall_precision(retrieved_ids: List[int], ground_truth_ids: List[int], k: int = 5) -> Dict[str, float]:
#     """Return a dict with recall@k and precision@k to match older callers."""
#     return {"recall@k": recall_at_k(retrieved_ids, ground_truth_ids, k), "precision@k": precision_at_k(retrieved_ids, ground_truth_ids, k)}


# def calculate_semantic_similarity(a: str, b: str) -> float:
#     try:
#         emb1 = embed_model.encode(a, convert_to_tensor=True)
#         emb2 = embed_model.encode(b, convert_to_tensor=True)
#         sim = util.pytorch_cos_sim(emb1, emb2).item()
#         return float(np.clip(sim, -1.0, 1.0))
#     except Exception:
#         return 0.0


# def _lcs_length(x_tokens: List[str], y_tokens: List[str]) -> int:
#     m, n = len(x_tokens), len(y_tokens)
#     if m == 0 or n == 0:
#         return 0
#     dp = [0] * (n + 1)
#     for i in range(1, m + 1):
#         prev = 0
#         xi = x_tokens[i - 1]
#         for j in range(1, n + 1):
#             temp = dp[j]
#             if xi == y_tokens[j - 1]:
#                 dp[j] = prev + 1
#             else:
#                 dp[j] = max(dp[j], dp[j - 1])
#             prev = temp
#     return dp[n]


# def rouge_l_score(reference: str, hypothesis: str) -> float:
#     ref_tokens = reference.split()
#     hyp_tokens = hypothesis.split()
#     if len(ref_tokens) == 0 or len(hyp_tokens) == 0:
#         return 0.0
#     lcs = _lcs_length(ref_tokens, hyp_tokens)
#     prec = lcs / len(hyp_tokens)
#     rec = lcs / len(ref_tokens)
#     if prec + rec == 0:
#         return 0.0
#     beta = 1.0
#     f1 = (1 + beta ** 2) * prec * rec / (rec + beta ** 2 * prec)
#     return float(f1)


# def calculate_faithfulness(context: str, answer: str) -> float:
#     rouge = rouge_l_score(context, answer)
#     sem = calculate_semantic_similarity(context, answer)
#     heuristic_score = 0.6 * rouge + 0.4 * ((sem + 1) / 2.0)

#     if llm_grader is not None:
#         prompt = f"""
# You are an evaluator. Given the CONTEXT and the MODEL ANSWER, return a concise numeric faithfulness score between 0 and 1 (1 = fully faithful, 0 = not faithful).

# Context:
# {context}

# Answer:
# {answer}

# Respond ONLY with a single number between 0 and 1.
# """
#         try:
#             resp = llm_grader.generate_content(prompt).text.strip()
#             score = float(resp)
#             return float(max(0.0, min(1.0, score)))
#         except Exception:
#             return float(np.clip(heuristic_score, 0.0, 1.0))

#     return float(np.clip(heuristic_score, 0.0, 1.0))


# def log_metrics(
#     query: str,
#     ground_truth: str,
#     retrieved_chunks: List[Dict[str, Any]],
#     answer: str,
#     ground_truth_ids: List[int],
#     retrieval_time_ms: float,
#     generation_time_ms: float,
#     total_time_ms: float,
#     k: int = 5,
# ):
#     retrieved_ids = [c.get("id", i) for i, c in enumerate(retrieved_chunks)]
#     retrieved_text = " ".join([c.get("text", "") for c in retrieved_chunks])

#     recall_k = recall_at_k(retrieved_ids, ground_truth_ids, k)
#     precision_k = precision_at_k(retrieved_ids, ground_truth_ids, k)
#     mrr = mean_reciprocal_rank(retrieved_ids, ground_truth_ids)
#     mapk = average_precision_at_k(retrieved_ids, ground_truth_ids, k)
#     ndcg = ndcg_at_k(retrieved_ids, ground_truth_ids, k)

#     sem_sim = calculate_semantic_similarity(answer, ground_truth)
#     rouge_l = rouge_l_score(ground_truth, answer)
#     faith = calculate_faithfulness(retrieved_text, answer)

#     row = [
#         int(time.time()),
#         query,
#         ground_truth,
#         len(retrieved_chunks),
#         answer,
#         k,
#         recall_k,
#         precision_k,
#         mrr,
#         mapk,
#         ndcg,
#         sem_sim,
#         rouge_l,
#         faith,
#         retrieval_time_ms,
#         generation_time_ms,
#         total_time_ms,
#     ]

#     with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(row)

#     print(f"✅ Metrics computed and logged for query: {query[:60]}...")

import numpy as np
import torch
import re
import string
import time
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from rouge import Rouge
from difflib import SequenceMatcher
from datetime import datetime
from transformers import pipeline

# -------------------------------------------------------------------
# Load better free models
# -------------------------------------------------------------------
# all-mpnet-base-v2 gives much stronger semantic matching
embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Optional lightweight open-source LLM for free evaluation (distilbart or t5)
# You can download once; runs locally via Hugging Face
faithfulness_grader = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    truncation=True,
    max_length=256
)

rouge = Rouge()

# -------------------------------------------------------------------
# Utility
# -------------------------------------------------------------------
def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()

# -------------------------------------------------------------------
# Core Metrics
# -------------------------------------------------------------------
def semantic_similarity(a, b):
    """Compute semantic cosine similarity between two texts."""
    if not a or not b:
        return 0.0
    emb = embedding_model.encode([a, b], convert_to_tensor=True, normalize_embeddings=True)
    sim = torch.nn.functional.cosine_similarity(emb[0], emb[1], dim=0)
    return float(sim.item())

def rouge_l_score(a, b):
    """Compute ROUGE-L F1."""
    if not a or not b:
        return 0.0
    try:
        return rouge.get_scores(a, b)[0]["rouge-l"]["f"]
    except Exception:
        return SequenceMatcher(None, a, b).ratio()

def fuzzy_score(a, b):
    """Compute approximate fuzzy matching score."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, clean_text(a), clean_text(b)).ratio()

# -------------------------------------------------------------------
# Faithfulness Evaluation (LLM-based but free)
# -------------------------------------------------------------------
def faithfulness_score(answer, context):
    """
    Combines semantic, lexical and free LLM evaluation for Vertex-like accuracy.
    Returns a score between 0 and 1.
    """
    if not context or not answer:
        return 0.0

    # Step 1: Lexical + semantic overlap
    rouge_l = rouge_l_score(answer, context)
    sem_sim = semantic_similarity(answer, context)
    fuzzy_sim = fuzzy_score(answer, context)

    print(f"Debug Faithfulness - ROUGE-L: {rouge_l}, SemSim: {sem_sim}, FuzzySim: {fuzzy_sim}")

    # Step 2: Lightweight LLM judgment (optional, free offline model)
    try:
        prompt = (
            f"Rate factual alignment (0-1) between ANSWER and CONTEXT. "
            f"Output only a number.\n\n"
            f"CONTEXT:\n{context}\n\nANSWER:\n{answer}"
        )
        llm_output = faithfulness_grader(prompt)[0]["generated_text"]
        llm_val = float(re.findall(r"0\.\d+|1\.0|1", llm_output)[0]) if re.search(r"\d", llm_output) else 0.5
    except Exception:
        llm_val = 0.5  # fallback if model fails

    # Step 3: Weighted fusion (similar to Vertex AI Eval logic)
    combined = (0.4 * sem_sim) + (0.3 * rouge_l) + (0.2 * fuzzy_sim) + (0.1 * llm_val)
    return float(min(max(combined, 0.0), 1.0))

# -------------------------------------------------------------------
# Precision and Recall (if you have ground truth ids)
# -------------------------------------------------------------------
def precision_at_k(retrieved_ids, relevant_ids, k=5):
    if not relevant_ids:
        return 0.0  # neutral if no ground truth
    retrieved_k = retrieved_ids[:k]
    return len(set(retrieved_k) & set(relevant_ids)) / len(retrieved_k)

def recall_at_k(retrieved_ids, relevant_ids, k=5):
    if not relevant_ids:
        return 0.0
    retrieved_k = retrieved_ids[:k]
    return len(set(retrieved_k) & set(relevant_ids)) / len(relevant_ids)

# -------------------------------------------------------------------
# Main Evaluation Entry
# -------------------------------------------------------------------
def evaluate_answer(query, answer, ground_truth="", retrieved_docs=None, relevant_ids=None, retrieved_ids=None):
    """
    Comprehensive evaluation producing human-like scores.
    """
    start = time.time()
    retrieved_docs = retrieved_docs or []
    relevant_ids = relevant_ids or []
    retrieved_ids = retrieved_ids or []

    # Compute metrics
    recall = recall_at_k(retrieved_ids, relevant_ids)
    precision = precision_at_k(retrieved_ids, relevant_ids)
    sem_sim = semantic_similarity(answer, ground_truth or "")
    faith = faithfulness_score(answer, " ".join(retrieved_docs) or ground_truth)

    end = time.time()
    latency = round((end - start) * 1000, 2)

    result = {
        "Recall@5": round(recall, 3),
        "Precision@5": round(precision, 3),
        "Semantic Similarity": round(sem_sim, 3),
        "Faithfulness": round(faith, 3),
        "Latency(ms)": latency,
    }
    return result

# -------------------------------------------------------------------
# CSV Logging (same as before)
# -------------------------------------------------------------------
def log_metrics(query, answer, metrics, csv_path="rag_metrics_log.csv"):
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "answer": answer,
        **metrics
    }
    df = pd.DataFrame([record])
    df.to_csv(csv_path, mode="a", index=False, header=not pd.io.common.file_exists(csv_path))
