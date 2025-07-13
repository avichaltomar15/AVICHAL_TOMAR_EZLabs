---

## Model With OpenAI and without OpenAI

This project does **not use OpenAI API by default**. Instead, it uses `sentence-transformers`, a free and open-source alternative for generating embeddings locally. This makes it suitable for students, researchers, and developers who do not have access to OpenAI API keys or want to avoid additional costs.
Although, I have created 2 separate projects and folders which use the above mentioned APIs

---

## Optional: Using OpenAI Embeddings

If you prefer to use OpenAI's `text-embedding-3-small` or other models for higher accuracy, you can switch back to OpenAI by updating the `utils.py` file and installing the OpenAI client.
You can add your OenAI API key in the backend code section and then use that model.

Insturctions to setup
### 1. Clone the repository
git clone https://github.com/your-username/smart-assistant.git
cd smart-assistant


### Next steps of the openAI model are provided in a readme file of the OpenAI folder.


2. Create virtual env
python3 -m venv venv
source venv/bin/activate

3. Install all dependencies

pip install -r requirements.txt

### Next steps of the openAI model are provided in a readme file of the OpenAI folder.

4. Run the backend server(for the sentence-transformers and not for the openAI one)

uvicorn backend.main:app --reload

5. Start the frontend

streamlit run frontend/app.py

(run these in the smart-assistant folder)
