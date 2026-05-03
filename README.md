# Intelligent Support Ticket Classification with RAG

A full Retrieval-Augmented Generation (RAG) pipeline built on ~936k real customer support tweets, covering data preprocessing, embedding generation, vector search, response generation, and evaluation.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Google Drive Files](#google-drive-files)
- [Milestones](#milestones)
  - [Milestone 1 — Data Collection, Preprocessing & Embeddings](#milestone-1--data-collection-preprocessing--embeddings)
  - [Milestone 2 — Model Development & Evaluation](#milestone-2--model-development--evaluation)
- [Deployment Guide](#deployment-guide)
- [Tech Stack](#tech-stack)
- [Environment Requirements](#environment-requirements)

---

## Project Overview

This project builds an end-to-end RAG system for automating customer support responses. Given a new customer query, the system:

1. **Retrieves** the most semantically similar historical support cases from a corpus of ~936k tweets using FAISS vector search.
2. **Augments** the prompt with retrieved examples as few-shot context.
3. **Generates** a response using `google/flan-t5-base` as the generator model.

The system is benchmarked against a traditional TF-IDF baseline across BLEU, ROUGE, cosine similarity, and Recall@K metrics.

**Dataset:** [`MohammadOthman/mo-customer-support-tweets-945k`](https://huggingface.co/datasets/MohammadOthman/mo-customer-support-tweets-945k)  
**Embedding model:** `all-mpnet-base-v2` (768-dim sentence embeddings)  
**Generator model:** `google/flan-t5-base`  
**Environment:** Google Colab (T4 GPU)

---

## Architecture

```
Customer Query
      |
      v
+---------------------+
|  Sentence Embedder  |  all-mpnet-base-v2
|  (query -> vector)  |
+----------+----------+
           |
           v
+---------------------+
|    FAISS Index      |  ~936k pre-computed vectors
|  (cosine search)    |  IndexFlatIP (dot product on normalized vectors)
+----------+----------+
           |  top-k similar cases
           v
+---------------------+
|   Prompt Builder    |  Formats retrieved Q&A pairs as few-shot context
+----------+----------+
           |
           v
+---------------------+
|   flan-t5-base      |  Seq2Seq generation (bfloat16, GPU)
|   (RAG generator)   |  num_beams=4, max_new_tokens=128
+----------+----------+
           |
           v
    Generated Response
```

---

## Repository Structure

The `outputs/` folder is **not tracked in this repository** because the files are too large for GitHub. All generated artifacts live in the shared Google Drive folder (see [Google Drive Files](#google-drive-files) below). The structure shown here reflects what the notebooks produce in Drive.

```
support_rag_project/          <- this repository
|
+-- notebooks/
|   +-- Milestone1_Colab.ipynb        # Data collection, preprocessing, embeddings
|   +-- Milestone2_fixed.ipynb        # RAG pipeline, evaluation (bug-fixed version)
|
+-- README.md
|
+-- outputs/                          <- NOT in git — stored in Google Drive
    +-- cleaned_corpus.csv            # ~936k cleaned input/output pairs
    +-- embedding_texts.csv           # Text corpus aligned to FAISS index
    +-- embeddings.npy                # Pre-computed sentence embeddings (~936k x 768)
    +-- eda_summary.csv               # EDA statistics
    |
    +-- milestone2/
        +-- faiss_index.bin           # Built FAISS index (load directly, no rebuild needed)
        +-- tfidf_matrix.npz          # Sparse TF-IDF matrix (50k features, bigrams)
        +-- flan_t5_base/             # Saved generator model and tokenizer
        +-- evaluation_report.json    # Full metrics report
```

If you clone this repo, you will not have the `outputs/` folder locally. Download the required files from Drive before running any notebook.

---

## Google Drive Files

All large artifacts are stored in the shared Google Drive folder. You must have access to this folder to run either milestone notebook.

| File | Size | Description | Link |
|------|------|-------------|------|
| `cleaned_corpus.csv` | ~500 MB | Full cleaned dataset | [Open in Drive](https://drive.google.com/file/d/1Uhm4dVVF44Ry9d6BMM-l5EiIYsDJQEOH/view?usp=drive_link) |
| `embedding_texts.csv` | ~300 MB | Text corpus aligned to embeddings | [Open in Drive](https://drive.google.com/file/d/1aUzDauHS2jKnukvL5-i0tZVwjmul9Pf0/view?usp=drive_link) |
| `embeddings.npy` | ~2.7 GB | Pre-computed sentence vectors | [Open in Drive](https://drive.google.com/file/d/1brUtNpT5f9qG9mpONkHtKw3vOlW1xz5L/view?usp=drive_link) |
| `faiss_index.bin` | ~400 MB | FAISS index (ready to load) | [Open in Drive](https://drive.google.com/file/d/1dhTXpSsXBWH98cMEWeJPEzpygDGx4nPm/view?usp=drive_link) |
| `tfidf_matrix.npz` | ~150 MB | Sparse TF-IDF matrix | [Open in Drive](https://drive.google.com/file/d/15GyNCX9VEoFLJAZmcdin0bbfmGOeABMU/view?usp=drive_link) |
| `flan_t5_base/` | ~1 GB | Generator model folder | [Open in Drive](https://drive.google.com/your-link-here) |
| `evaluation_report.json` | < 1 MB | Metrics (BLEU, ROUGE, Recall@K) | [Open in Drive](https://drive.google.com/your-link-here) |

> The last two links still need to be filled in. Right-click each file/folder in Drive → Share → Copy link, and replace the placeholder.

To request access, contact the project owner and ask to be added to the `support_rag_project` Drive folder.

---

## Milestones

### Milestone 1 — Data Collection, Preprocessing & Embeddings

**Notebook:** `Milestone1_Colab.ipynb`  
**Runtime:** ~45–60 min on T4 GPU (embedding step dominates)

**What it does:**

1. Loads the full 945k dataset from HuggingFace.
2. Drops duplicates and empty rows, then applies `preprocess_text` — lowercasing, URL removal, mention and punctuation stripping.
3. Filters rows where either `input_clean` or `output_clean` has fewer than 3 characters after cleaning.
4. Generates EDA visualisations: length distributions, length ratio, top-30 words, word clouds.
5. Encodes all `input_clean` texts into 768-dim sentence embeddings using `all-mpnet-base-v2` with `normalize_embeddings=True`.
6. Saves `cleaned_corpus.csv`, `embedding_texts.csv`, and `embeddings.npy` to Google Drive.

**Key outputs saved to Drive:**

```
outputs/cleaned_corpus.csv
outputs/embedding_texts.csv
outputs/embeddings.npy
```

**Note on NaN values after CSV round-trip:**

The filter in Milestone 1 uses `str.len() > 2`, which does not strip whitespace before measuring length. A string consisting entirely of spaces passes the filter, gets written as an empty CSV cell, and is reloaded as `NaN` in Milestone 2. The fix is already applied in `Milestone2_fixed.ipynb`. For a permanent upstream fix in Milestone 1, change the filter to:

```python
df = df[
    (df['input_clean'].str.strip().str.len() > 2) &
    (df['output_clean'].str.strip().str.len() > 2)
].reset_index(drop=True)
```

---

### Milestone 2 — Model Development & Evaluation

**Notebook:** `Milestone2_fixed.ipynb` — use this version, not the original  
**Runtime:** ~15–25 min on T4 GPU

**Part A — Vector Search (FAISS)**
- Loads pre-computed embeddings from Drive.
- Builds a `faiss.IndexFlatIP` index over the full ~936k corpus. Dot product on pre-normalized vectors is equivalent to cosine similarity.
- Saves `faiss_index.bin` to Drive.

**Part B — TF-IDF Baseline**
- Fits a `TfidfVectorizer` (50k features, unigram + bigram, `min_df=3`) on all `input_clean` texts.
- Saves `tfidf_matrix.npz` to Drive.

**Part C — RAG Pipeline**
- Loads `google/flan-t5-base` in `bfloat16` on GPU.
- `rag_generate(query)` retrieves top-3 similar cases, builds a few-shot prompt, and generates a response.
- `rag_generate_batch(queries)` is the batched version used during evaluation.

**Part D — Evaluation**
- Recall@K (K = 1, 3, 5, 10) on 5,000 eval pairs, comparing FAISS against TF-IDF.
- BLEU and ROUGE on 1,000 generated responses, comparing RAG against TF-IDF top-1 retrieval.
- Cosine similarity between generated and reference responses.
- All metrics saved to `evaluation_report.json`.

**Scale config (Cell 8):**

```python
EMBED_SIZE     = len(df)    # full corpus (~936k)
RECALL_EVAL    = 5_000      # pairs used for Recall@K evaluation
GEN_EVAL_SIZE  = 1_000      # pairs used for BLEU/ROUGE evaluation
BATCH_EMBED    = 512        # sentence embedding batch size
BATCH_GEN      = 8          # generation batch size (keep <= 8 on T4 to avoid OOM)
```

---

## Deployment Guide

Follow these steps if you are setting up this project for deployment and do not need to retrain or re-embed. You only need the Drive files — the notebooks are not required for inference.

### Step 1 — Install dependencies

```bash
pip install sentence-transformers faiss-cpu transformers \
            scikit-learn torch scipy pandas tqdm
```

For GPU inference:
```bash
pip install faiss-gpu  # replaces faiss-cpu
```

### Step 2 — Access the Drive files

**Option A — Google Colab:**
```python
from google.colab import drive
drive.mount('/content/drive')
BASE = '/content/drive/MyDrive/support_rag_project/outputs'
```

**Option B — Local or cloud server:**  
Download the files from the Drive links in the table above and update the path:
```python
BASE = '/path/to/downloaded/outputs'
```

### Step 3 — Load all artifacts

```python
import numpy as np
import pandas as pd
import faiss
import scipy.sparse
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Corpus
embed_df = pd.read_csv(f'{BASE}/embedding_texts.csv').dropna().reset_index(drop=True)
print(f'Corpus loaded: {len(embed_df):,} rows')

# FAISS index — load directly, no rebuild required
index = faiss.read_index(f'{BASE}/milestone2/faiss_index.bin')
print(f'FAISS index: {index.ntotal:,} vectors')

# Sentence embedder — CPU is sufficient for query encoding
embedder = SentenceTransformer('all-mpnet-base-v2', device='cpu')

# TF-IDF matrix
tfidf_matrix = scipy.sparse.load_npz(f'{BASE}/milestone2/tfidf_matrix.npz')

# Generator model
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
model_path = f'{BASE}/milestone2/flan_t5_base'
tokenizer  = AutoTokenizer.from_pretrained(model_path)
gen_model  = AutoModelForSeq2SeqLM.from_pretrained(
    model_path, torch_dtype=torch.bfloat16
).to(DEVICE).eval()

print('All artifacts loaded. Ready for inference.')
```

### Step 4 — Run inference

```python
def retrieve(query: str, top_k: int = 5) -> pd.DataFrame:
    q_vec = embedder.encode([query], normalize_embeddings=True).astype('float32')
    scores, indices = index.search(q_vec, top_k)
    valid = indices[0][indices[0] >= 0]
    results = embed_df.iloc[valid].copy()
    results['similarity'] = scores[0][:len(valid)]
    return results[['input_clean', 'output_clean', 'similarity']].reset_index(drop=True)


def rag_generate(query: str, top_k: int = 3, max_new_tokens: int = 128) -> str:
    hits = retrieve(query, top_k=top_k)
    context = '\n\n'.join(
        f"Customer: {r.input_clean}\nAgent: {r.output_clean}"
        for _, r in hits.iterrows()
    )
    prompt = (
        "You are a customer support agent. Use the examples below to respond.\n\n"
        f"Examples:\n{context}\n\n"
        f"New Customer: {query}\nAgent Response:"
    )
    with torch.no_grad():
        enc = tokenizer(prompt, return_tensors='pt', truncation=True, max_length=512).to(DEVICE)
        out = gen_model.generate(
            **enc,
            max_new_tokens=max_new_tokens,
            num_beams=4,
            early_stopping=True,
            pad_token_id=tokenizer.pad_token_id
        )
    return tokenizer.decode(out[0], skip_special_tokens=True)


# Example
print(rag_generate("my order hasn't arrived and it's been 2 weeks"))
```

---

## Tech Stack

| Component | Library / Model |
|-----------|----------------|
| Dataset | HuggingFace Datasets |
| Text cleaning | Python `re`, NLTK |
| Sentence embeddings | `sentence-transformers` — `all-mpnet-base-v2` |
| Vector index | `faiss` — `IndexFlatIP` |
| TF-IDF baseline | `scikit-learn` — `TfidfVectorizer` |
| Generator | HuggingFace Transformers — `google/flan-t5-base` |
| Evaluation | `evaluate` — sacrebleu, rouge-score |
| Visualisation | `matplotlib`, `seaborn`, `wordcloud` |
| Storage | Google Drive (accessed via Colab) |

---

## Environment Requirements

- **Platform:** Google Colab with GPU runtime (T4 or better)
- **Python:** 3.10+
- **VRAM:** 8 GB minimum, 16 GB recommended (T4 = 16 GB)
- **Drive space:** ~5 GB for all artifacts

```bash
# Full install — run at the top of any Colab notebook
pip install -q datasets transformers sentence-transformers \
               faiss-cpu evaluate sacrebleu rouge-score \
               scikit-learn pandas matplotlib seaborn wordcloud \
               nltk tqdm scipy torch
```

---
