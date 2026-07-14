# AI Support Ticket Intelligence Platform

A full-stack intelligent support system that classifies customer tickets, assigns priority, and generates agent solutions plus customer-ready replies using trained ML models.

| Layer | Stack |
|-------|--------|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion |
| **Backend** | FastAPI, scikit-learn, joblib, Pydantic |
| **ML** | TF-IDF + Logistic Regression (classification), TF-IDF Nearest Response (reply generation) |

---

## Features

- **Ticket classification** — category + confidence from `traditional_tfidf_logreg_classifier.joblib`
- **Priority inference** — rule-based priority from category and confidence
- **Response generation** — nearest-neighbor replies via `tfidf_nearest_response_model.joblib`
- **Dynamic model loading** — auto-discovers artifacts at startup; no hardcoded model names
- **Enterprise dashboard** — dark mode, health monitoring, prediction history, toast notifications
- **Production-ready API** — `/health`, `/model-info`, `/predict` with CORS and structured logging

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (Next.js)          http://localhost:3000        │
│  Landing · Dashboard · API status · Model info panel        │
└──────────────────────────────┬──────────────────────────────┘
                               │ Axios
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend (FastAPI)           http://localhost:8000          │
│  POST /predict  →  vectorize → classify → generate reply    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend/artifacts/  (models — download separately)         │
│  · traditional_tfidf_logreg_classifier.joblib               │
│  · tfidf_response_vectorizer.joblib                           │
│  · tfidf_nearest_response_model.joblib                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
DEPI Project/
├── Backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/          # health, predict, model-info
│   │   ├── services/        # model loading, inference, response
│   │   ├── schemas/
│   │   ├── core/
│   │   └── utils/
│   ├── artifacts/           # ML models (not in Git — see below)
│   ├── metrics/             # evaluation JSON / CSV
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/                 # landing + dashboard pages
│   ├── components/
│   ├── lib/                 # API client + types
│   ├── hooks/
│   └── package.json
├── intelligent-support-ticket-classification-with-rag.ipynb
├── render.yaml              # Backend deploy (Render)
└── vercel.json              # Frontend deploy (Vercel)
```

---

## Prerequisites

| Tool | Version |
|------|---------|
| **Python** | 3.10+ |
| **Node.js** | 18+ |
| **npm** | 9+ |

---

## Run In VS Code

These steps are the easiest way to run the project locally in **Visual Studio Code on Windows**.

### 1. Open the project folder

1. Open **VS Code**.
2. Click **File -> Open Folder...**
3. Select:

```text
d:\My Projects\DEPI Project
```

### 2. Open two terminals in VS Code

In VS Code:

1. Open **Terminal -> New Terminal**
2. Keep the first terminal for the **backend**
3. Open a second terminal for the **frontend**

You can also split the terminal with the split terminal button in VS Code.

### 3. Run the backend in terminal 1

```powershell
cd Backend
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Backend URLs:

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/health | Check backend status |
| http://127.0.0.1:8000/model-info | Check loaded model info |
| http://127.0.0.1:8000/docs | Open Swagger API docs |

### 4. Run the frontend in terminal 2

```powershell
cd frontend
npm install
```

Create `frontend/.env.local` with:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Then start the frontend:

```powershell
npm run dev
```

Frontend URLs:

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:3000 | Landing page |
| http://127.0.0.1:3000/dashboard | Dashboard |

### 5. Test inside the app

1. Open `http://127.0.0.1:3000/dashboard`
2. Enter a ticket title and description
3. Click **Classify Ticket**
4. Review:
   - predicted category
   - priority
   - confidence
   - resolution guide
   - draft reply

### 6. If VS Code cannot find npm

If VS Code says `npm is not recognized`, restart VS Code after installing Node.js.

If it still fails, run this in the frontend terminal before `npm install`:

```powershell
$env:Path += ";C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Microsoft\VisualStudio\NodeJs"
```

### 7. If prediction fails

Check these in order:

1. Backend terminal is still running on port `8000`
2. `frontend/.env.local` contains `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`
3. Artifacts exist inside `Backend/artifacts/`
4. Refresh the browser after restarting either server

---

## Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

---

## Step 2 — Download model artifacts

Large model files are **not stored in GitHub** (GitHub limits files to 100 MB).

Download the artifacts archive from Google Drive:

**[Download artifacts.zip]([https://drive.google.com/file/d/1rFphFsEmlPGHOX5OfzwtEj5OeSh-ykXU/view?usp=sharing](https://drive.google.com/file/d/1H-LAu7L4xwlrO1uiGErB6yys6uJ8alcA/view?usp=sharing))**

Then:

1. Extract the zip.
2. Copy the contents into `Backend/artifacts/`.

**Minimum files required to run the API:**

| File | Purpose |
|------|---------|
| `traditional_tfidf_logreg_classifier.joblib` | Ticket classification |
| `tfidf_response_vectorizer.joblib` | Response vectorization |
| `tfidf_nearest_response_model.joblib` | Customer reply generation |

Your folder should look like:

```
Backend/artifacts/
├── traditional_tfidf_logreg_classifier.joblib
├── tfidf_response_vectorizer.joblib
└── tfidf_nearest_response_model.joblib
```

---

## Step 3 — Backend setup

Open a terminal:

```bash
cd Backend
pip install -r requirements.txt
```

**Windows (recommended):**

To run the backend on the correct port (8000) and avoid port conflicts with the frontend:

```powershell
cd Backend
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

> [!TIP]
> If you see `WinError 10013` (access permissions forbidden), it means a backend server is already running in the background. Stop it first using:
> `Stop-Process -Name python, uvicorn -Force -ErrorAction SilentlyContinue`

Default values work for local development. API runs at **http://127.0.0.1:8000**.

Verify:

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/health | Service + model status |
| http://127.0.0.1:8000/model-info | Loaded models and metrics |
| http://127.0.0.1:8000/docs | Swagger API documentation |

---

## Step 4 — Frontend setup

Open a **second** terminal:

```powershell
cd frontend
```

**Windows Path Fix (If `npm` is not recognized):**
If your terminal cannot find `npm`, run this inside your PowerShell terminal to temporarily append Node.js/npm's installation folder:

```powershell
$env:Path += ";C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Microsoft\VisualStudio\NodeJs"
```

Then install dependencies:

```bash
npm install
```

Create `frontend/.env.local` to point to the backend's IPv4 loopback (this avoids Windows IPv6 localhost connection failures):

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Start the dev server:

```bash
npm run dev
```

App runs at **http://localhost:3000**

| Page | URL |
|------|-----|
| Landing | http://localhost:3000 |
| Dashboard | http://localhost:3000/dashboard |

---

## Step 5 — Use the application

1. Open the **Dashboard**.
2. Enter a **ticket title** and **description**.
3. Click **Classify Ticket**.
4. Review:
   - **Category** and **priority**
   - **Confidence** score
   - **Agent solution** (internal playbook)
   - **Customer reply** (message draft)
   - **Models used** (classifier + vectorizer)

---

## API Reference

### `GET /health`

Returns API and model load status.

### `GET /model-info`

Returns selected classifier, vectorizer, response model paths and metrics.

### `POST /predict`

**Request:**

```json
{
  "title": "Payment failed for my order",
  "description": "My card was charged but the order status is still pending."
}
```

**Response:**

```json
{
  "category": "billing_payment",
  "priority": "high",
  "confidence": 0.95,
  "agent_solution": "Verify transaction ID and payment gateway logs...",
  "customer_reply": "Thanks for reaching out. We're reviewing your payment...",
  "model_used": "traditional_tfidf_logreg_classifier",
  "vectorizer_used": "tfidf_response_vectorizer"
}
```

---

## Ticket Categories

| Category | Examples |
|----------|----------|
| `account_login` | login, password, verification |
| `billing_payment` | payment, invoice, charges |
| `order_shipping` | delivery, tracking, packages |
| `refund_return` | refunds, cancellations |
| `technical_app` | app bugs, crashes, errors |
| `product_service` | product quality, features |
| `general_support` | general inquiries |

---

## Deployment

| Service | Config | Folder |
|---------|--------|--------|
| **Frontend** | Vercel | `frontend/` |
| **Backend** | Render (Docker) | `Backend/` |

### Vercel frontend

1. Import the repository into Vercel.
2. Set the **Root Directory** to `frontend`.
3. Framework should detect as **Next.js** automatically.
4. Add this environment variable:

```env
NEXT_PUBLIC_API_URL=https://YOUR-RENDER-BACKEND.onrender.com
```

5. Deploy the project.

### Render backend

This repository includes `render.yaml`, and the backend service must point to the case-sensitive `Backend/` folder.

Before deploying on Render:

1. Confirm your Render service uses the repo root `render.yaml`.
2. Confirm the backend service root directory resolves to `Backend/`.
3. Add `CORS_ORIGINS` with your Vercel domain, for example:

```env
CORS_ORIGINS=https://YOUR-FRONTEND.vercel.app
```

4. Make sure the required files inside `Backend/artifacts/` are available to the Render build/runtime environment.

> [!IMPORTANT]
> The current backend artifacts are very large locally. If those files are not available in the Render environment, the backend may start without a usable prediction pipeline.

### Deployment order

1. Deploy the backend to Render first.
2. Copy the final Render backend URL.
3. Set `NEXT_PUBLIC_API_URL` in Vercel.
4. Deploy or redeploy the frontend in Vercel.

---

## ML Training (optional)

The Jupyter notebook `intelligent-support-ticket-classification-with-rag.ipynb` contains the full training pipeline (TF-IDF classifier, hybrid RAG retrieval, Qwen generation) on the [MohammadOthman/mo-customer-support-tweets-945k](https://huggingface.co/datasets/MohammadOthman/mo-customer-support-tweets-945k) dataset.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `app.main:app` not recognized (PowerShell) | Use `py -m uvicorn app.main:app --reload` from `Backend/` |
| Prediction failed | Confirm artifacts are in `Backend/artifacts/` and restart backend |
| Frontend offline | Check `NEXT_PUBLIC_API_URL` and that backend is running on port 8000 |
| Hydration warning | Hard refresh (`Ctrl + Shift + R`) after frontend restart |

---

## License

Educational and research use.
