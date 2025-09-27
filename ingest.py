from flask import Flask, render_template, request, jsonify
import fitz
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import CharacterTextSplitter

app = Flask(__name__)

pdf_path = "data/doc_sarpo.pdf"
doc_text = ""

with fitz.open(pdf_path) as doc:
    for page in doc:
        doc_text += page.get_text()

splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = splitter.split_text(doc_text)

embeddings = OllamaEmbeddings(model="llama2:7b-chat")
vectorstore = Chroma.from_texts(texts, embeddings)

chat_model = Ollama(model="llama2:7b-chat")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question")
    if not question:
        return jsonify({"answer": "Pertanyaan kosong!"})

    #retrieve
    docs = vectorstore.similarity_search(question, k=3)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"Jawab pertanyaan berikut berdasarkan konteks ini:\n{context}\n\nPertanyaan: {question}\nJawaban:"
    answer = chat_model.invoke(prompt)

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
