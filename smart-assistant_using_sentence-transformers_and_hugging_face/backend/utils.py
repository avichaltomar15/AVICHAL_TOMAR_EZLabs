from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

def load_and_embed(file_path):
    print(f"DEBUG: Received file: {file_path}")
    ext = os.path.splitext(file_path)[1].lower()
    print(f"DEBUG: Detected extension: {ext}")

    if ext == "":
        with open(file_path, "rb") as f:
            start = f.read(4)
        ext = ".pdf" if start.startswith(b"%PDF") else ".txt"

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8", autodetect_encoding=True)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    docs = loader.load()

    # Use free local HuggingFace model
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    db = FAISS.from_documents(docs, embeddings)
    return db, docs

