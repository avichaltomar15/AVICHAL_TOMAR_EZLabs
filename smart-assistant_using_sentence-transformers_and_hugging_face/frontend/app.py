import streamlit as st
import requests

st.set_page_config(page_title="📚 Smart Research Assistant", layout="centered")
st.title("📄 Smart Assistant for Research Summarization")

# Persistent state
if "summary" not in st.session_state:
    st.session_state.summary = ""

# Upload Section
uploaded = st.file_uploader("📤 Upload PDF or TXT", type=["pdf", "txt"])
if uploaded:
    with st.spinner("Uploading and analyzing..."):
        res = requests.post("http://localhost:8000/upload", files={"file": uploaded})
        try:
            result = res.json()
            if "summary" in result:
                st.session_state.summary = result["summary"]
                st.success("✅ Document processed successfully!")
            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown backend issue.')}")
        except Exception as e:
            st.error("❌ Failed to decode backend response. Possibly a crash.")
            st.text(f"Raw response: {res.text[:500]}")

# Summary Section
if st.session_state.summary:
    st.subheader("🔍 Auto Summary (150 words)")
    st.info(st.session_state.summary)

    # Interaction Mode
    mode = st.radio("Choose an Interaction Mode", ["Ask Anything", "Challenge Me"])

    # ASK ANYTHING MODE
    if mode == "Ask Anything":
        question = st.text_input("💬 Ask a question from the document")
        if question:
            res = requests.post("http://localhost:8000/ask", json={"question": question})
            st.markdown(f"**🧠 Answer:** {res.json()['answer']}")
            st.caption("📌 Justified from: " + res.json()['justification'])

    # CHALLENGE MODE
    elif mode == "Challenge Me":
        res = requests.get("http://localhost:8000/challenge")
        questions = res.json()["questions"]
        answers = {}
        st.markdown("### 🧠 Try to answer the following:")
        for i, q in enumerate(questions):
            answers[q] = st.text_area(f"Q{i+1}: {q}")

        if st.button("🚀 Submit Answers"):
            for q, a in answers.items():
                if a.strip() == "":
                    st.warning(f"❗ You left Q: '{q}' unanswered.")
                    continue
                res = requests.post("http://localhost:8000/evaluate", json={"question": q, "answer": a})
                st.markdown(f"**Q:** {q}")
                st.markdown(f"**Your Answer:** {a}")
                st.markdown(f"✅ **Correct Answer:** {res.json()['correct_answer']}")
                st.caption("📌 Reference: " + res.json()['reference'])

