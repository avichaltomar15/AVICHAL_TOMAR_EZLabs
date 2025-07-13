# Document-Aware AI Assistant

## Overview
This project is an AI assistant that can read, understand, and reason through user-uploaded PDF or TXT documents. It supports free-form question answering and logic-based question generation, all grounded in the actual document content.

---

## Features
- **Document Upload:** Supports PDF and TXT files.
- **Auto Summary:** Generates a concise summary (≤150 words) after upload.
- **Ask Anything:** Free-form Q&A based on document content, with justifications.
- **Challenge Me:** Generates logic-based questions, evaluates user answers, and provides feedback with references to the document.
- **Web Interface:** Clean, local web UI using Streamlit.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2. (Optional) Create and Activate a Virtual Environment
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Your OpenAI API Key
- **Option 1:** Edit `backend.py` and set your API key in the code (already present by default).
- **Option 2 (Recommended):** Set as an environment variable:
  ```powershell
  $env:OPENAI_API_KEY="your-key-here"
  ```

### 5. Start the Backend
```bash
uvicorn backend:app --reload
```

### 6. Start the Frontend
Open a new terminal and run:
```bash
streamlit run frontend.py
```

### 7. Use the App
- Open the Streamlit URL (usually http://localhost:8501) in your browser.
- Upload a document and interact with the assistant!

---

## Architecture & Reasoning Flow

```mermaid
graph TD
    A[User uploads PDF/TXT] --> B[Backend parses & stores text]
    B --> C[Auto-summary generated (OpenAI)]
    C --> D[Frontend displays summary]
    D --> E{User selects mode}
    E -- Ask Anything --> F[User question sent to backend]
    F --> G[OpenAI Q&A with doc context]
    G --> H[Answer + justification returned]
    E -- Challenge Me --> I[Backend generates 3 logic-based questions (OpenAI)]
    I --> J[Frontend displays questions]
    J --> K[User submits answers]
    K --> L[Backend evaluates answer (OpenAI)]
    L --> M[Feedback + justification returned]
```

- **Backend:** FastAPI handles file upload, parsing, and all OpenAI API calls.
- **Frontend:** Streamlit provides a simple, interactive UI.
- **Reasoning:** All answers and feedback reference the actual document content, with justifications.

---

## Source Code Organization

```
project-root/
│
├── backend.py         # FastAPI backend (API, document parsing, OpenAI calls)
├── frontend.py        # Streamlit frontend (UI)
├── requirements.txt   # Python dependencies
├── README.md          # This file
└── uploaded_docs/     # Uploaded documents (auto-created)
```

---

## Demo Walkthrough (Optional)
- Record a 2–3 min Loom/YouTube video showing:
  1. Uploading a document
  2. Viewing the summary
  3. Using both "Ask Anything" and "Challenge Me" modes
- Add the video link here:

[Demo Video Link](#)

---

## Notes
- If you see quota errors, check your OpenAI account usage and billing.
- For any issues, please open an issue or contact the maintainer. 