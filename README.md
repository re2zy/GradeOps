# GradeOps

A Human-in-the-Loop (HITL) exam grading pipeline. Professors upload bulk handwritten exam scans and JSON rubrics. A vision model transcribes the answers, a LangGraph agentic pipeline grades them with partial credit and justifications, and TAs review/approve/override on a high-speed dashboard.

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI + SQLAlchemy + PostgreSQL |
| ML Pipeline | LangGraph + LangChain + Groq (OCR + Grading) |
| Storage | Local filesystem |
| Frontend | React + Vite + Redux Toolkit |

## Requirements

- Python 3.11
- Node.js 20+
- PostgreSQL 16+
- Groq API key (free at console.groq.com)

## Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/re2zy/GradeOps.git
cd GradeOps
```

### 2. Set up environment variables
```bash
cp .env.example .env
```

Fill in `.env`:
```env
DATABASE_URL=postgresql://gradeops:gradeops@localhost:5432/gradeops
SECRET_KEY=any-long-random-string-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
ENVIRONMENT=development
```

### 3. Set up PostgreSQL
Create the database and user:
```sql
CREATE USER gradeops WITH PASSWORD 'gradeops';
CREATE DATABASE gradeops OWNER gradeops;
GRANT ALL ON SCHEMA public TO gradeops;
ALTER DATABASE gradeops OWNER TO gradeops;
```

### 4. Set up Python venv and install dependencies
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
pip install pymupdf groq google-generativeai
```

### 5. Seed demo data
```bash
# Windows
set PYTHONPATH=backend
python scripts/seed_db.py

# macOS/Linux
PYTHONPATH=backend python scripts/seed_db.py
```

### 6. Start the backend
```bash
# Windows PowerShell
$env:GROQ_API_KEY="your-groq-key-here"
uvicorn main:app --reload --port 8000

# macOS/Linux
GROQ_API_KEY="your-groq-key-here" uvicorn main:app --reload --port 8000
```

### 7. Start the frontend
Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```

### 8. Open the app
Go to http://localhost:5173

Demo credentials:
- Instructor: `instructor@gradeops.com` / `password123`
- TA: `ta@gradeops.com` / `password123`

## Project Structure
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
ocr.py                  Groq vision PDF → text extraction
rubric_parser.py        Parse rubric JSON, build grading prompts
grader_agent.py         Groq LLM answer grader
plagiarism.py           TF-IDF cosine similarity detection
langgraph_workflow.py   Orchestration: extract → grade → plagiarism
utils/
jwt.py                  Auth helpers, route guards
cloud_storage.py        Local file storage (replaces GCS)
uploads/                  Locally stored PDFs and cropped images
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

## Rubric JSON Format

```json
{
  "questions": [
    {
      "number": 1,
      "text": "Explain the difference between a stack and a queue.",
      "max_score": 10,
      "criteria": [
        { "description": "Correct definition of stack (LIFO)", "points": 3 },
        { "description": "Correct definition of queue (FIFO)", "points": 3 },
        { "description": "Real-world example for stack", "points": 2 },
        { "description": "Real-world example for queue", "points": 2 }
      ]
    }
  ]
}
```

## Review Dashboard Keyboard Shortcuts

| Key | Action |
|---|---|
| `A` | Approve current grade |
| `O` | Open override modal |
| `← / P` | Previous grade |
| `→ / N` | Next grade |
| `Esc` | Close modal |