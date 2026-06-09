
# Intelligent Support Ticket Classification with RAG

A end-to-end machine learning pipeline that classifies customer support tickets and generates context-aware responses using Retrieval-Augmented Generation (RAG). Built for the Kaggle Notebook environment.

---

## Overview

This project solves two interrelated problems in customer support automation:

1. **Ticket Classification** — automatically assign incoming tickets to one of seven predefined categories.
2. **Response Generation** — generate helpful, context-aware replies by retrieving similar historical tickets and prompting a language model.

Both a traditional baseline and a RAG-based approach are implemented and evaluated side by side.

---

## Pipeline

```
Customer Ticket
    └─► Text Cleaning
          └─► Weak Label Assignment (category)
                └─► Train / Test Split (leakage-free)
                      ├─► Traditional Classifier (TF-IDF + Logistic Regression)
                      └─► Hybrid RAG Pipeline
                            ├─► Embedding Generation (BAAI/bge-base-en-v1.5)
                            ├─► BM25 Keyword Retrieval
                            ├─► FAISS Semantic Retrieval
                            ├─► Hybrid Reranking
                            ├─► RAG Classifier (weighted category voting)
                            └─► RAG Generator (Qwen2.5-1.5B-Instruct)
```

---

## Dataset

**Source:** [`MohammadOthman/mo-customer-support-tweets-945k`](https://huggingface.co/datasets/MohammadOthman/mo-customer-support-tweets-945k) on Hugging Face

| Column   | Description                    |
|----------|--------------------------------|
| `input`  | Customer message / ticket text |
| `output` | Support agent response         |

You can also supply your own CSV with `input` and `output` columns via the `KAGGLE_INPUT_CSV` variable.

---

## Ticket Categories

Since the dataset has no official labels, **weak labels** are assigned using keyword matching rules:

| Category          | Example Keywords                                    |
|-------------------|-----------------------------------------------------|
| `account_login`   | login, password, reset, verify                      |
| `billing_payment` | payment, invoice, charged, credit card              |
| `order_shipping`  | order, delivery, tracking, package                  |
| `refund_return`   | refund, return, cancel, money back                  |
| `technical_app`   | app, bug, error, crash, not working                 |
| `product_service` | product, quality, stock, price, feature             |
| `general_support` | fallback for tickets that match no other category   |

> **Note:** These are weak labels for demonstration purposes. For production use, replace them with manually labeled data.

---

## Models

| Component                    | Model / Method                          |
|------------------------------|-----------------------------------------|
| Traditional Classifier       | TF-IDF + Logistic Regression            |
| Traditional Response Baseline| TF-IDF Nearest Neighbor (retrieves old response) |
| Embedding Model              | `BAAI/bge-base-en-v1.5`                 |
| Semantic Retrieval           | FAISS (IndexFlatIP, cosine similarity)  |
| Keyword Retrieval            | BM25 (Okapi BM25)                       |
| Hybrid Reranking             | FAISS weight 0.55 + BM25 weight 0.45   |
| RAG Classifier               | Hybrid retrieval + weighted voting      |
| RAG Generator                | `Qwen/Qwen2.5-1.5B-Instruct`           |

---

## Evaluation Metrics

**Classification:**
- Accuracy, Weighted Precision, Weighted Recall, Weighted F1

**Retrieval (using weak category labels as relevance proxies):**
- Precision@K, Hit@K, MRR@K

**Response Generation:**
- ROUGE-1, ROUGE-2, ROUGE-L, BLEU

---

## Project Structure

```
support_ticket_rag_runs/
└── run_<YYYYMMDD_HHMMSS>/
    ├── artifacts/
    │   ├── loaded_raw_dataset.csv
    │   ├── cleaned_labeled_dataset.csv
    │   ├── train_split.csv
    │   ├── test_split.csv
    │   ├── train_embeddings.npy
    │   ├── test_embeddings.npy
    │   ├── faiss_train.index
    │   ├── bm25_tokenized_corpus.json
    │   ├── traditional_tfidf_logreg_classifier.joblib
    │   ├── tfidf_response_vectorizer.joblib
    │   ├── tfidf_nearest_response_model.joblib
    │   └── rag_generation_examples.csv
    ├── figures/
    │   ├── input_word_length_distribution.png
    │   ├── output_word_length_distribution.png
    │   ├── input_output_length_boxplot.png
    │   ├── top_input_words.png
    │   ├── top_output_words.png
    │   ├── input_wordcloud.png
    │   ├── category_distribution.png
    │   ├── traditional_classifier_confusion_matrix.png
    │   ├── classification_comparison.png
    │   └── response_generation_comparison.png
    ├── metrics/
    │   ├── eda_summary_initial.json
    │   ├── top_input_words.csv
    │   ├── top_output_words.csv
    │   ├── traditional_classification_metrics.json
    │   ├── traditional_response_metrics.json
    │   ├── retrieval_metrics.json
    │   ├── rag_classification_metrics.json
    │   ├── rag_response_metrics.json
    │   ├── classification_comparison.csv
    │   └── response_generation_comparison.csv
    └── final_run_summary.json
```

---

## Setup (Kaggle)

1. Open the notebook in Kaggle.
2. Enable **Internet = On** in notebook settings (required to load the Hugging Face dataset and models).
3. Use a **GPU accelerator** for faster embedding generation and Qwen inference.
4. Run all cells sequentially.

All outputs are saved to `/kaggle/working/support_ticket_rag_runs/`.

### Key Configuration Variables

| Variable              | Default                              | Description                                      |
|-----------------------|--------------------------------------|--------------------------------------------------|
| `MAX_ROWS`            | `None` (full dataset)                | Limit rows for faster testing (e.g. `50_000`)    |
| `TEST_SIZE`           | `0.20`                               | Fraction of data held out for evaluation         |
| `TOP_K`               | `5`                                  | Number of retrieved examples per query           |
| `FAISS_WEIGHT`        | `0.55`                               | Weight of semantic score in hybrid retrieval     |
| `BM25_WEIGHT`         | `0.45`                               | Weight of keyword score in hybrid retrieval      |
| `EMBED_MODEL_NAME`    | `BAAI/bge-base-en-v1.5`              | Sentence embedding model                         |
| `GEN_MODEL_NAME`      | `Qwen/Qwen2.5-1.5B-Instruct`         | Generation model                                 |
| `RUN_GENERATION_EVAL` | `True`                               | Set to `False` to skip the generation step       |
| `RUN_MINHASH_DEDUP`   | `True`                               | Enable MinHash near-duplicate removal            |
| `MINHASH_THRESHOLD`   | `0.95`                               | Jaccard similarity threshold for deduplication  |
| `KAGGLE_INPUT_CSV`    | `None`                               | Path to a custom CSV with `input`/`output` cols  |

---

## Dependencies

```
datasets
transformers
sentence-transformers
accelerate
faiss-cpu
rank-bm25
evaluate
sacrebleu
rouge-score
datasketch
wordcloud
tqdm
joblib
scikit-learn
pandas
numpy
matplotlib
seaborn
torch
```

Install in Kaggle with:

```bash
pip -q install -U datasets transformers sentence-transformers accelerate faiss-cpu rank-bm25 evaluate sacrebleu rouge-score datasketch wordcloud tqdm joblib
```

---

## Limitations

- **Weak labels:** The ticket categories are rule-based approximations, not human-verified ground truth. Classification metrics reflect performance on these proxy labels, not real-world accuracy.
- **Retrieval evaluation:** Relevance is proxied by category match; no human relevance judgments are included.
- **Generation model size:** `Qwen2.5-1.5B-Instruct` is a compact model. A larger model would likely produce higher-quality responses.

---

## License

This project is provided for educational and research purposes.
