import csv
import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


def simple_tokenize(text: str) -> list[str]:
    return str(text).lower().split()


def minmax_norm(scores: list[float]) -> np.ndarray:
    values = np.array(scores, dtype=float)
    if len(values) == 0:
        return values
    minimum, maximum = values.min(), values.max()
    if maximum - minimum < 1e-9:
        return np.ones_like(values)
    return (values - minimum) / (maximum - minimum)


@dataclass
class RagRuntime:
    train_rows: list[dict[str, str]]
    faiss_index: Any
    bm25: BM25Okapi
    embedder: SentenceTransformer
    top_k: int
    faiss_weight: float
    bm25_weight: float
    candidate_pool: int = 50


def _load_train_rows(train_csv: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with train_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "input_clean": (row.get("input_clean") or row.get("input") or "").strip(),
                    "output_clean": (row.get("output_clean") or row.get("output") or "").strip(),
                    "category": (row.get("category") or "general_support").strip(),
                }
            )
    if not rows:
        raise RuntimeError(f"No training rows found in {train_csv}")
    return rows


def load_rag_runtime(
    artifacts_dir: Path,
    embed_model_path: str,
    top_k: int,
    faiss_weight: float,
    bm25_weight: float,
    candidate_pool: int,
    device: str,
    faiss_use_mmap: bool = True,
) -> RagRuntime:
    train_csv = artifacts_dir / "train_split.csv"
    faiss_path = artifacts_dir / "faiss_train.index"
    bm25_path = artifacts_dir / "bm25_tokenized_corpus.json"

    for path in (train_csv, faiss_path, bm25_path):
        if not path.exists():
            raise RuntimeError(f"Missing RAG artifact: {path}")

    logger.info("Loading RAG train corpus from %s", train_csv)
    train_rows = _load_train_rows(train_csv)

    logger.info("Loading FAISS index from %s (mmap=%s)", faiss_path, faiss_use_mmap)
    read_flags = faiss.IO_FLAG_MMAP if faiss_use_mmap else 0
    faiss_index = faiss.read_index(str(faiss_path), read_flags)

    logger.info("Loading BM25 corpus from %s", bm25_path)
    with bm25_path.open("r", encoding="utf-8") as handle:
        bm25_corpus = json.load(handle)
    bm25 = BM25Okapi(bm25_corpus)

    if faiss_index.ntotal != len(train_rows) or len(bm25_corpus) != len(train_rows):
        raise RuntimeError(
            "RAG artifact size mismatch: "
            f"faiss={faiss_index.ntotal}, bm25={len(bm25_corpus)}, train_rows={len(train_rows)}"
        )

    logger.info("Loading embedding model %s on %s", embed_model_path, device)
    embedder = SentenceTransformer(embed_model_path, device=device)

    logger.info("RAG runtime ready | train_rows=%s | top_k=%s", len(train_rows), top_k)
    return RagRuntime(
        train_rows=train_rows,
        faiss_index=faiss_index,
        bm25=bm25,
        embedder=embedder,
        top_k=top_k,
        faiss_weight=faiss_weight,
        bm25_weight=bm25_weight,
        candidate_pool=candidate_pool,
    )


def hybrid_retrieve(runtime: RagRuntime, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
    top_k = top_k or runtime.top_k
    query_clean = query.strip()

    query_embedding = runtime.embedder.encode(
        [query_clean],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")

    pool_size = min(runtime.candidate_pool, len(runtime.train_rows))
    faiss_scores, faiss_ids = runtime.faiss_index.search(query_embedding, pool_size)
    faiss_scores = faiss_scores[0]
    faiss_ids = faiss_ids[0]

    bm25_scores_all = runtime.bm25.get_scores(simple_tokenize(query_clean))
    bm25_top_ids = np.argsort(bm25_scores_all)[::-1][:pool_size]
    bm25_top_scores = bm25_scores_all[bm25_top_ids]

    candidate_ids = list(set(faiss_ids.tolist() + bm25_top_ids.tolist()))
    faiss_score_map = {int(index): float(score) for index, score in zip(faiss_ids, faiss_scores)}
    bm25_score_map = {int(index): float(score) for index, score in zip(bm25_top_ids, bm25_top_scores)}

    raw_faiss = [faiss_score_map.get(index, 0.0) for index in candidate_ids]
    raw_bm25 = [bm25_score_map.get(index, 0.0) for index in candidate_ids]
    norm_faiss = minmax_norm(raw_faiss)
    norm_bm25 = minmax_norm(raw_bm25)
    combined = runtime.faiss_weight * norm_faiss + runtime.bm25_weight * norm_bm25

    ranked = sorted(
        zip(candidate_ids, combined, raw_faiss, raw_bm25),
        key=lambda item: item[1],
        reverse=True,
    )[:top_k]

    results: list[dict[str, Any]] = []
    for index, score, faiss_score, bm25_score in ranked:
        row = runtime.train_rows[int(index)]
        results.append(
            {
                "train_index": int(index),
                "score": float(score),
                "faiss_score": float(faiss_score),
                "bm25_score": float(bm25_score),
                "input": row["input_clean"],
                "output": row["output_clean"],
                "category": row["category"],
            }
        )
    return results


def rag_classify(runtime: RagRuntime, query: str, top_k: int | None = None) -> str:
    results = hybrid_retrieve(runtime, query, top_k=top_k)
    scores: dict[str, float] = defaultdict(float)
    for rank, result in enumerate(results, start=1):
        scores[result["category"]] += result["score"] + (1.0 / rank)
    if not scores:
        return "general_support"
    return max(scores, key=scores.get)


def build_agent_solution(category: str, retrieved_examples: list[dict[str, Any]]) -> str:
    if not retrieved_examples:
        return f"Review the ticket details and follow the support playbook for '{category}'."

    lines = [f"Recommended playbook for '{category}' based on similar resolved tickets:"]
    for index, example in enumerate(retrieved_examples[:3], start=1):
        lines.append(
            f"{index}. Prior ticket: \"{example['input'][:120]}\" "
            f"→ Resolution pattern: \"{example['output'][:160]}\""
        )
    lines.append("Adapt the closest historical resolution to the customer's current details.")
    return "\n".join(lines)
