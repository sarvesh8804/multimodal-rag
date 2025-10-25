import time
import csv
import os
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai

# Initialize Embedding Model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Configure Gemini for Faithfulness Check
genai.configure(api_key=os.getenv("GEMINI_API"))
llm_grader = genai.GenerativeModel(model_name="gemini-2.5-flash")

# CSV File for Metrics Log
LOG_FILE = "rag_metrics_log.csv"

# Create file with headers if not present
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "query",
            "ground_truth",
            "retrieved_chunks",
            "answer",
            "recall@k",
            "precision@k",
            "semantic_similarity",
            "faithfulness_score",
            "retrieval_time_ms",
            "generation_time_ms",
            "total_time_ms"
        ])

# -------------------------------------------------
# 🔹 Utility Functions
# -------------------------------------------------

def calculate_recall_precision(retrieved_ids: List[int], ground_truth_ids: List[int]) -> Dict[str, float]:
    """Compute Recall@k and Precision@k."""
    intersection = set(retrieved_ids) & set(ground_truth_ids)
    recall = len(intersection) / len(ground_truth_ids) if ground_truth_ids else 0.0
    precision = len(intersection) / len(retrieved_ids) if retrieved_ids else 0.0
    return {"recall@k": recall, "precision@k": precision}


def calculate_semantic_similarity(answer: str, ground_truth: str) -> float:
    """Compute cosine similarity between model output and reference answer."""
    emb1 = embed_model.encode(answer, convert_to_tensor=True)
    emb2 = embed_model.encode(ground_truth, convert_to_tensor=True)
    return float(util.pytorch_cos_sim(emb1, emb2).item())


def calculate_faithfulness(context: str, answer: str) -> float:
    """
    Use Gemini model to score faithfulness: 
    'Does the answer stay consistent with the provided context?'
    Output: 0.0 - 1.0 (normalized)
    """
    prompt = f"""
    You are an evaluator. Given the context and the model's answer, rate how faithful the answer is.
    Faithfulness means that the answer should only use information from the context, without hallucinations.
    Give a numerical score between 0 and 1, where:
    1 = perfectly faithful, 0 = completely unfaithful.

    Context:
    {context}

    Answer:
    {answer}

    Respond ONLY with a number.
    """
    try:
        result = llm_grader.generate_content(prompt).text.strip()
        score = float(result)
        return min(max(score, 0.0), 1.0)
    except:
        return 0.0


def log_metrics(
    query: str,
    ground_truth: str,
    retrieved_chunks: List[Dict[str, Any]],
    answer: str,
    ground_truth_ids: List[int],
    retrieval_time_ms: float,
    generation_time_ms: float,
    total_time_ms: float
):
    """Compute metrics and append to CSV log."""
    retrieved_ids = [chunk.get("id", i) for i, chunk in enumerate(retrieved_chunks)]

    # Compute metrics
    recall_precision = calculate_recall_precision(retrieved_ids, ground_truth_ids)
    semantic_similarity = calculate_semantic_similarity(answer, ground_truth)
    faithfulness_score = calculate_faithfulness(" ".join([c["text"] for c in retrieved_chunks]), answer)

    # Log to CSV
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            query,
            ground_truth,
            len(retrieved_chunks),
            answer,
            recall_precision["recall@k"],
            recall_precision["precision@k"],
            semantic_similarity,
            faithfulness_score,
            retrieval_time_ms,
            generation_time_ms,
            total_time_ms
        ])

    print(f"✅ Metrics logged for query: {query[:50]}...")
