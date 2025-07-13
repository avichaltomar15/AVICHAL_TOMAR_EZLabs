def summarize(docs):
    text = " ".join([d.page_content for d in docs])
    return text[:150] + "..."  # Auto summary ≤150 characters

