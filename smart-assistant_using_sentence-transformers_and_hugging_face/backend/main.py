from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from backend.utils import load_and_embed
from backend.summarizer import summarize
from backend.qa import answer_question
from backend.challenge import generate_questions, evaluate
from fastapi.responses import JSONResponse

import tempfile
from pathlib import Path  # <--- Add this

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

db = None
docs = None

@app.post("/upload")
async def upload_doc(file: UploadFile):
    global db, docs
    try:
        # ✅ Get original file extension (.pdf or .txt)
        suffix = Path(file.filename).suffix or ".txt"

        # ✅ Save to temp file with correct extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        db, docs = load_and_embed(tmp_path)
        summary = summarize(docs)
        return {"summary": summary}
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process file: {str(e)}"},
        )

@app.post("/ask")
async def ask_anything(q: dict):
    answer, justification = answer_question(db, q["question"])
    return {"answer": answer, "justification": justification}

@app.get("/challenge")
def challenge_me():
    return {"questions": generate_questions()}

@app.post("/evaluate")
async def evaluate_answer(data: dict):
    correct, ref = evaluate(db, data["question"], data["answer"])
    return {"correct_answer": correct, "reference": ref}

