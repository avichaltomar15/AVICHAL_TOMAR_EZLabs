from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import PyPDF2
import pdfplumber
import openai
from openai import OpenAI

client = OpenAI(api_key="")  # This will use your OPENAI_API_KEY from env or you can pass it as api_key="..."

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Your prompt here"}
    ],
    max_tokens=300,
    temperature=0.5,
)
print(response.choices[0].message.content)

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

documents = {}  # session_id: { 'text': ..., 'filename': ... }

# Helper: Extract text from PDF

def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = "\n".join(page.extract_text() or '' for page in pdf.pages)
        return text
    except Exception:
        # fallback to PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join(page.extract_text() or '' for page in reader.pages)
        return text

# Helper: Extract text from TXT

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# Helper: Summarize document (≤150 words)
def summarize_text(text):
    prompt = (
        "Summarize the following document in no more than 150 words. "
        "Be concise and capture the main points.\n\nDocument:\n" + text
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.5,
        )
        print(response)  # Debug: see the structure
        if response.choices and hasattr(response.choices[0], "message") and hasattr(response.choices[0].message, "content"):
            content = response.choices[0].message.content
            if content is not None:
                return content.strip()
            else:
                return "[Error] OpenAI chat completion returned no content."
        else:
            return "[Error] Unexpected response format from OpenAI chat completion."
    except Exception as e:
        response = client.completions.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            temperature=0.5,
        )
        print(response)  # Debug: see the structure
        if response.choices and hasattr(response.choices[0], "text"):
            text = response.choices[0].text
            if text is not None:
                return text.strip()
            else:
                return "[Error] OpenAI completion returned no text."
        else:
            return f"[Error] Unexpected response format from OpenAI completion. Exception: {e}"

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        return JSONResponse(status_code=400, content={"error": "No filename provided."})
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".txt"]:
        return JSONResponse(status_code=400, content={"error": "Only PDF and TXT files are supported."})
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_txt(file_path)
    session_id = file.filename
    documents[session_id] = {"text": text, "filename": file.filename}
    summary = summarize_text(text[:4000])
    return {"session_id": session_id, "summary": summary}

@app.post("/ask")
async def ask_question(session_id: str = Form(...), question: str = Form(...)):
    doc = documents.get(session_id)
    if not doc:
        return JSONResponse(status_code=404, content={"error": "Session not found."})
    prompt = (
        f"You are an assistant. Answer the following question using ONLY the provided document. "
        f"Cite the section or paragraph where the answer is found.\n\nDocument:\n{doc['text'][:4000]}\n\nQuestion: {question}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.2,
        )
        print(response)  # Debug: see the structure
        if response.choices and hasattr(response.choices[0], "message") and hasattr(response.choices[0].message, "content"):
            content = response.choices[0].message.content
            if content is not None:
                return {"answer": content.strip()}
            else:
                return {"error": "[Error] OpenAI chat completion returned no content."}
        else:
            return {"error": "[Error] Unexpected response format from OpenAI chat completion."}
    except Exception as e:
        response = client.completions.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=400,
            temperature=0.2,
        )
        print(response)  # Debug: see the structure
        if response.choices and hasattr(response.choices[0], "text"):
            text = response.choices[0].text
            if text is not None:
                return {"answer": text.strip()}
            else:
                return {"error": "[Error] OpenAI completion returned no text."}
        else:
            return {"error": f"[Error] Unexpected response format from OpenAI completion. Exception: {e}"}

@app.post("/challenge")
async def challenge_me(session_id: str = Form(...)):
    doc = documents.get(session_id)
    if not doc:
        return JSONResponse(status_code=404, content={"error": "Session not found."})
    prompt = (
        "Generate three logic-based or comprehension-focused questions based on the following document. "
        "Each question should require reasoning or understanding, not just fact recall.\n\nDocument:\n" + doc['text'][:4000]
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        print(response)  # Debug: see the structure
        if response.choices and hasattr(response.choices[0], "message") and hasattr(response.choices[0].message, "content"):
            content = response.choices[0].message.content
            if content is not None:
                questions = content.strip()
                return {"questions": questions}
            else:
                return {"error": "[Error] OpenAI chat completion returned no content."}
        else:
            return {"error": "[Error] Unexpected response format from OpenAI chat completion."}
    except Exception as e:
        response = client.completions.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            temperature=0.7,
        )
        print(response)  # Debug: see the structure
        if response.choices and hasattr(response.choices[0], "text"):
            text = response.choices[0].text
            if text is not None:
                questions = text.strip()
                return {"questions": questions}
            else:
                return {"error": "[Error] OpenAI completion returned no text."}
        else:
            return {"error": f"[Error] Unexpected response format from OpenAI completion. Exception: {e}"}

@app.post("/evaluate")
async def evaluate_answer(session_id: str = Form(...), question: str = Form(...), user_answer: str = Form(...)):
    doc = documents.get(session_id)
    if not doc:
        return JSONResponse(status_code=404, content={"error": "Session not found."})
    prompt = (
        f"Given the document and the user's answer to the question, evaluate the answer. "
        f"Say if it's correct, partially correct, or incorrect, and justify referencing the document.\n\n"
        f"Document:\n{doc['text'][:4000]}\n\nQuestion: {question}\nUser Answer: {user_answer}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
        )
        print(response)  # Debug: see the structure
        if response.choices and hasattr(response.choices[0], "message") and hasattr(response.choices[0].message, "content"):
            content = response.choices[0].message.content
            if content is not None:
                return {"evaluation": content.strip()}
            else:
                return {"error": "[Error] OpenAI chat completion returned no content."}
        else:
            return {"error": "[Error] Unexpected response format from OpenAI chat completion."}
    except Exception as e:
        response = client.completions.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            temperature=0.3,
        )
        print(response)  # Debug: see the structure
        if response.choices and hasattr(response.choices[0], "text"):
            text = response.choices[0].text
            if text is not None:
                return {"evaluation": text.strip()}
            else:
                return {"error": "[Error] OpenAI completion returned no text."}
        else:
            return {"error": f"[Error] Unexpected response format from OpenAI completion. Exception: {e}"} 
