# import os
# import json
# import time
# from typing import List, Dict, Any

# from dotenv import load_dotenv
# import google.generativeai as genai

# load_dotenv()

# JUDGE_API_KEY = os.getenv("GEMINI_API_NEW") or os.getenv("GEMINI_API")
# if not JUDGE_API_KEY:
#     raise ValueError("GEMINI_API_NEW or GEMINI_API must be set for the judge.")

# genai.configure(api_key=JUDGE_API_KEY)
# JUDGE_MODEL_NAME = os.getenv("JUDGE_MODEL_NAME", "gemini-2.5-flash")


# def _build_judge_prompt(query: str, answer: str, retrieved_docs: List[str]) -> str:
#     context_joined = "\n\n---\n\n".join(retrieved_docs[:10])
#     prompt = f"""
# You are an impartial evaluation model for a Multimodal RAG system.

# You are given:
# 1. A user query.
# 2. A set of retrieved context chunks (may include VISUAL CACHE entries).
# 3. A model's answer generated USING ONLY that context.

# Evaluate ONLY based on context and query.
# Return JSON with float scores 0.0–1.0:
# - grounding
# - relevance
# - completeness
# - coherence
# - hallucination
# - multimodal_usage (0.5 if no visuals)

# [USER QUERY]
# {query}

# [RETRIEVED CONTEXT]
# {context_joined}

# [MODEL ANSWER]
# {answer}

# Return JSON only.
# {{
#   "grounding": 0.5,
#   "relevance": 0.5,
#   "completeness": 0.5,
#   "coherence": 0.5,
#   "hallucination": 0.5,
#   "multimodal_usage": 0.5
# }}
# """
#     return prompt.strip()


# def _call_judge_model(prompt: str) -> Dict[str, Any]:
#     model = genai.GenerativeModel(model_name=JUDGE_MODEL_NAME)
#     resp = model.generate_content(prompt)
#     text = (resp.text or "").strip()

#     first_brace = text.find("{")
#     last_brace = text.rfind("}")
#     if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
#         text = text[first_brace:last_brace + 1]

#     try:
#         data = json.loads(text)
#     except json.JSONDecodeError:
#         data = {k: 0.5 for k in ["grounding", "relevance", "completeness", "coherence", "hallucination", "multimodal_usage"]}

#     default_metrics = {k: 0.5 for k in ["grounding", "relevance", "completeness", "coherence", "hallucination", "multimodal_usage"]}
#     default_metrics.update({k: float(v) for k, v in data.items() if k in default_metrics})
#     return default_metrics


# def evaluate_answer(query: str, answer: str, retrieved_docs: List[str]) -> Dict[str, Any]:
#     if not retrieved_docs:
#         retrieved_docs = ["(no context provided)"]

#     prompt = _build_judge_prompt(query=query, answer=answer, retrieved_docs=retrieved_docs)
#     start = time.time()
#     judge_scores = _call_judge_model(prompt)
#     latency_ms = (time.time() - start) * 1000

#     metrics = {
#         "Grounding": round(judge_scores["grounding"], 3),
#         "Relevance": round(judge_scores["relevance"], 3),
#         "Completeness": round(judge_scores["completeness"], 3),
#         "Coherence": round(judge_scores["coherence"], 3),
#         "Hallucination": round(judge_scores["hallucination"], 3),
#         "MultimodalUsage": round(judge_scores["multimodal_usage"], 3),
#         "JudgeLatency(ms)": round(latency_ms, 2),
#     }
#     return metrics


# def log_metrics(query: str, answer: str, metrics: Dict[str, Any], log_dir: str = "logs", log_file: str = "eval_log.jsonl") -> None:
#     os.makedirs(log_dir, exist_ok=True)
#     path = os.path.join(log_dir, log_file)

#     record = {
#         "query": query,
#         "answer": answer,
#         "metrics": metrics,
#         "timestamp": time.time(),
#     }

#     with open(path, "a", encoding="utf-8") as f:
#         f.write(json.dumps(record, ensure_ascii=False) + "\n")



# if __name__ == '__main__':  
#     print(f"Using Judge Model: {JUDGE_MODEL_NAME}")
    
#     sample_query = "What are the three main types of solar panels mentioned, and which one is the most efficient according to the text?"
#     sample_answer = "The three main types of solar panels are monocrystalline, andu gundu thanda pani upar baithe raja rani, and thin-film. Monocrystalline is the most efficient, achieving up to 22% efficiency. The text mentions that they are also the most expensive."
#     sample_docs = [
#         "Solar Panel Technology: Monocrystalline panels are known for their high efficiency, typically 18-22%, and have a distinctive dark color. They are made from a single crystal of silicon, making them the most expensive type.",
#         "Polycrystalline panels are cheaper to produce and less efficient (15-17%) as they are made from multiple silicon fragments.",
#         "Thin-film panels offer the lowest efficiency (10-14%) but are lightweight and flexible.",
#         "[Image Description: A diagram showing the internal structure of a monocrystalline cell with text stating 'Single, High Purity Silicon'].",
#         "The current market favors monocrystalline due to its performance benefits."
#     ]

#     print("\n--- Running Evaluation ---")
#     results = evaluate_answer(
#         query=sample_query,
#         answer=sample_answer,
#         retrieved_docs=sample_docs
#     )
    
#     print("\n--- Evaluation Results ---")
#     for k, v in results.items():
#         print(f"🌟 {k}: {v}")

#     # Log the results
#     log_metrics(sample_query, sample_answer, results)
#     print(f"\nResults logged to logs/eval_log.jsonl")   


import os
import json
import time
from typing import List, Dict, Any

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

JUDGE_API_KEY = os.getenv("GEMINI_API_NEW") or os.getenv("GEMINI_API")
if not JUDGE_API_KEY:
    raise ValueError("GEMINI_API_NEW or GEMINI_API must be set for the judge.")

genai.configure(api_key=JUDGE_API_KEY)
JUDGE_MODEL_NAME = os.getenv("JUDGE_MODEL_NAME", "gemini-2.5-flash")


def _build_judge_prompt(query: str, answer: str, retrieved_docs: List[str]) -> str:
    context_joined = "\n\n---\n\n".join(retrieved_docs[:10])
    prompt = f"""
You are an impartial evaluation model for a Multimodal RAG system.

You are given:
1. A user query.
2. A set of retrieved context chunks (may include VISUAL CACHE entries).
3. A model's answer generated USING ONLY that context.

Evaluate ONLY based on context and query.
Return JSON with float scores 0.0–1.0:
- grounding
- relevance
- completeness
- coherence
- hallucination
- multimodal_usage (0.5 if no visuals)

[USER QUERY]
{query}

[RETRIEVED CONTEXT]
{context_joined}

[MODEL ANSWER]
{answer}

Return JSON only.
{{
  "grounding": 0.5,
  "relevance": 0.5,
  "completeness": 0.5,
  "coherence": 0.5,
  "hallucination": 0.5,
  "multimodal_usage": 0.5
}}
"""
    return prompt.strip()


def _call_judge_model(prompt: str) -> Dict[str, Any]:
    model = genai.GenerativeModel(model_name=JUDGE_MODEL_NAME)
    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()

    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace:last_brace + 1]

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {k: 0.5 for k in ["grounding", "relevance", "completeness", "coherence", "hallucination", "multimodal_usage"]}

    default_metrics = {k: 0.5 for k in ["grounding", "relevance", "completeness", "coherence", "hallucination", "multimodal_usage"]}
    default_metrics.update({k: float(v) for k, v in data.items() if k in default_metrics})
    return default_metrics


# -------------------------------
# IR METRICS: Precision@K, Recall@K, Accuracy@K, Hit@K
# -------------------------------
def compute_ir_metrics(retrieved_docs: List[Dict[str, Any]], relevant_docs: List[str], k: int = 5) -> Dict[str, float]:
    """
    retrieved_docs: List of dicts with 'text' or 'id' (top K retrieved docs)
    relevant_docs: List of strings (ground truth relevant doc texts or ids)
    """
    top_k = retrieved_docs[:k]
    retrieved_set = set([d.get("text") for d in top_k])

    relevant_set = set(relevant_docs)

    # True positives
    tp = len(retrieved_set & relevant_set)
    # Precision@K
    precision = tp / k if k > 0 else 0.0
    # Recall@K
    recall = tp / len(relevant_set) if relevant_set else 0.0
    # Accuracy@K
    accuracy = 1.0 if retrieved_set & relevant_set else 0.0
    # Hit@K
    hit = 1.0 if tp > 0 else 0.0

    return {
        "Precision@K": round(precision, 3),
        "Recall@K": round(recall, 3),
        "Accuracy@K": round(accuracy, 3),
        "Hit@K": round(hit, 3),
    }


def evaluate_answer(query: str, answer: str, retrieved_docs: List[Dict[str, Any]], relevant_docs: List[str] = None) -> Dict[str, Any]:
    if not retrieved_docs:
        retrieved_docs = [{"text": "(no context provided)"}]

    prompt = _build_judge_prompt(
        query=query,
        answer=answer,
        retrieved_docs=[d["text"] for d in retrieved_docs]
    )
    start = time.time()
    judge_scores = _call_judge_model(prompt)
    latency_ms = (time.time() - start) * 1000

    metrics = {
        "Grounding": round(judge_scores["grounding"], 3),
        "Relevance": round(judge_scores["relevance"], 3),
        "Completeness": round(judge_scores["completeness"], 3),
        "Coherence": round(judge_scores["coherence"], 3),
        "Hallucination": round(judge_scores["hallucination"], 3),
        "MultimodalUsage": round(judge_scores["multimodal_usage"], 3),
        "JudgeLatency(ms)": round(latency_ms, 2),
    }

    # Add IR metrics if relevant_docs provided
    if relevant_docs:
        ir_metrics = compute_ir_metrics(retrieved_docs, relevant_docs, k=5)
        metrics.update(ir_metrics)

    return metrics


def log_metrics(query: str, answer: str, metrics: Dict[str, Any], log_dir: str = "logs", log_file: str = "eval_log.jsonl") -> None:
    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, log_file)

    record = {
        "query": query,
        "answer": answer,
        "metrics": metrics,
        "timestamp": time.time(),
    }

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
