from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

def answer_question(db, question):
    docs = db.similarity_search(question, k=3)
    llm = OpenAI(temperature=0)
    chain = load_qa_chain(llm, chain_type="stuff")
    answer = chain.run(input_documents=docs, question=question)
    justification = docs[0].page_content[:200] + "..." if docs else "Not found"
    return answer, justification

