import random
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain

def generate_questions():
    return random.sample([
        "What is the main hypothesis of the document?",
        "What methodology is used?",
        "What is the key conclusion?",
        "What is the central problem being solved?",
        "Which experiments or studies are referenced?"
    ], 3)

def evaluate(db, question, user_answer):
    docs = db.similarity_search(question)
    correct = load_qa_chain(OpenAI(temperature=0)).run(docs, question=question)
    ref = docs[0].page_content[:200] + "..." if docs else "Not found"
    return correct, ref

