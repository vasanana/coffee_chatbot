from flask import Flask, render_template, request, jsonify
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings

app = Flask(__name__)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="chroma_db", 
                     embedding_function=embeddings)

chat_model = Ollama(model="llama2:7b-chat")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question")
    if not question:
        return jsonify({"answer": "Pertanyaan kosong!"})

    docs = vectorstore.similarity_search(question, k=3)
    context = "\n".join([doc.page_content for doc in docs])

    #prompt
    prompt = f"Jawab pertanyaan berikut berdasarkan konteks ini:\n{context}\n\nPertanyaan: {question}\nJawaban:"
    answer = chat_model.invoke(prompt)

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
