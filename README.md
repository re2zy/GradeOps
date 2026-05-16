# GradeOps

A Human-in-the-Loop (HITL) exam grading pipeline. Professors upload bulk handwritten exam scans and JSON rubrics. A VLM (Qwen-VL) transcribes the answers, a LangGraph agentic pipeline grades them with partial credit and justifications, and TAs review/approve/override on a high-speed dashboard.

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI + SQLAlchemy + PostgreSQL |
| ML Pipeline | LangGraph + LangChain + Qwen-VL (OCR) + Claude (grading) |
| Storage | Google Cloud Storage |
| Frontend | React + Vite + Redux Toolkit |
| Infra | Docker Compose, GitHub Actions → Cloud Run + Firebase |

## Quick Start

```bash
# 1. Copy and fill in env vars
cp .env.example .env

# 2. Start everything
docker compose up

# 3. Seed demo users & exam
PYTHONPATH=backend python scripts/seed_db.py

# 4. Open http://localhost:5173
#    instructor@gradeops.com / password123
#    ta@gradeops.com         / password123
```

## Project Structure

```
backend/
  main.py                   FastAPI app entry point
  config.py                 Pydantic settings (reads .env)
  database.py               SQLAlchemy engine + session
  models/                   SQLAlchemy ORM models
  schemas/                  Pydantic request/response schemas
  routers/                  API route handlers
    auth.py                 Register, login, /me
    upload.py               Create exams, upload PDFs
    grade.py                Fetch grades & summary
    review.py               TA approve/override endpoints
  pipeline/
    ocr.py                  Qwen-VL PDF → text extraction
    rubric_parser.py        Parse rubric JSON, build grading prompts
    grader_agent.py         Claude-based answer grader
    plagiarism.py           TF-IDF cosine similarity detection
    langgraph_workflow.py   Orchestration: extract → grade → plagiarism
  utils/
    jwt.py                  Auth helpers, route guards
    cloud_storage.py        GCS upload/download

frontend/
  src/
    pages/
      LoginPage.jsx
      DashboardPage.jsx     Exam list with status cards
      UploadPage.jsx        Create exam + bulk PDF upload
      ReviewPage.jsx        TA review dashboard (keyboard shortcuts)
    components/Navbar.jsx
    store/index.js          Redux Toolkit slices (auth, exams, grades)
    api/index.js            Axios instance with auth interceptor

scripts/
  seed_db.py                Insert demo data
  setup_cloud_storage.sh    Create GCS bucket with CORS + lifecycle rules
```

## Review Dashboard Keyboard Shortcuts

| Key | Action |
|---|---|
| `A` | Approve current grade |
| `O` | Open override modal |
| `← / P` | Previous grade |
| `→ / N` | Next grade |
| `Esc` | Close modal |

## Rubric JSON Format

```json
{
  "questions": [
    {
      "number": 1,
      "text": "Explain the difference between a stack and a queue.",
      "max_score": 10,
      "criteria": [
        { "description": "Correct definition of stack (LIFO)", "points": 4 },
        { "description": "Correct definition of queue (FIFO)", "points": 4 },
        { "description": "Real-world example for each", "points": 2 }
      ]
    }
  ]
}
```

## Deployment

Push to `main` to trigger GitHub Actions:
- Backend → Google Cloud Run (via `deploy.yml`)
- Frontend → Firebase Hosting

Required GitHub secrets: `GCP_SA_KEY`, `FIREBASE_SERVICE_ACCOUNT`, `FIREBASE_PROJECT_ID`
