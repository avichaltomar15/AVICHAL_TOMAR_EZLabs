import streamlit as st
import requests

st.set_page_config(page_title="Document-Aware AI Assistant", layout="centered")
st.title("📄 Document-Aware AI Assistant")

API_URL = "http://localhost:8000"

if "session_id" not in st.session_state:
    st.session_state.session_id = None
    st.session_state.summary = None
    st.session_state.questions = None
    st.session_state.challenge_mode = False

st.header("1. Upload a Document (PDF or TXT)")
uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])

if uploaded_file:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    with st.spinner("Uploading and processing document..."):
        res = requests.post(f"{API_URL}/upload", files=files)
    if res.status_code == 200:
        data = res.json()
        st.session_state.session_id = data["session_id"]
        st.session_state.summary = data["summary"]
        st.session_state.questions = None
        st.session_state.challenge_mode = False
        st.success("Document uploaded and summarized!")
    else:
        st.error(res.json().get("error", "Upload failed."))

if st.session_state.summary:
    st.subheader("Auto Summary (≤ 150 Words)")
    st.info(st.session_state.summary)

    st.header("2. Choose Interaction Mode")
    mode = st.radio("Select a mode:", ["Ask Anything", "Challenge Me"])

    if mode == "Ask Anything":
        st.session_state.challenge_mode = False
        st.subheader("Ask Anything")
        question = st.text_input("Type your question about the document:")
        if st.button("Ask") and question:
            with st.spinner("Thinking..."):
                res = requests.post(f"{API_URL}/ask", data={"session_id": st.session_state.session_id, "question": question})
            if res.status_code == 200:
                st.write(res.json()["answer"])
            else:
                st.error(res.json().get("error", "Failed to get answer."))

    elif mode == "Challenge Me":
        st.session_state.challenge_mode = True
        st.subheader("Challenge Me")
        if st.session_state.questions is None:
            if st.button("Generate Questions"):
                with st.spinner("Generating questions..."):
                    res = requests.post(f"{API_URL}/challenge", data={"session_id": st.session_state.session_id})
                if res.status_code == 200:
                    # Expecting a string with 3 questions
                    questions = res.json()["questions"].split("\n")
                    questions = [q.strip() for q in questions if q.strip()]
                    st.session_state.questions = questions
                else:
                    st.error(res.json().get("error", "Failed to generate questions."))
        if st.session_state.questions:
            for idx, q in enumerate(st.session_state.questions):
                st.markdown(f"**Q{idx+1}: {q}**")
                user_answer = st.text_input(f"Your answer to Q{idx+1}", key=f"answer_{idx}")
                if st.button(f"Submit Answer to Q{idx+1}", key=f"submit_{idx}") and user_answer:
                    with st.spinner("Evaluating answer..."):
                        res = requests.post(f"{API_URL}/evaluate", data={
                            "session_id": st.session_state.session_id,
                            "question": q,
                            "user_answer": user_answer
                        })
                    if res.status_code == 200:
                        st.success(res.json()["evaluation"])
                    else:
                        st.error(res.json().get("error", "Failed to evaluate answer.")) 