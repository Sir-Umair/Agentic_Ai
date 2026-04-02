import os
import json
import urllib.parse
import time
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# LangChain imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PDFMinerLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_anthropic import ChatAnthropic   # ← Changed to Anthropic
from langchain_core.messages import HumanMessage, SystemMessage

# =========================
# 1. SETUP
# =========================
load_dotenv()

app = Flask(__name__)
CORS(app)

print("⏳ Initializing RAG Backend (Claude Edition)...")

# Check API Key
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    print("❌ ERROR: ANTHROPIC_API_KEY not found in .env file.")
    exit(1)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2", 
    model_kwargs={"device": "cpu"}
)

vectorstore_path = "faiss_index"

def get_vectorstore():
    if os.path.exists(vectorstore_path):
        print("⏳ Loading existing FAISS index...")
        try:
            return FAISS.load_local(
                vectorstore_path, embeddings, allow_dangerous_deserialization=True
            )
        except Exception as e:
            print(f"⚠️ Error loading index: {e}. Rebuilding...")
            import shutil
            if os.path.exists(vectorstore_path):
                shutil.rmtree(vectorstore_path)

    print("⏳ Building FAISS index from PDF...")
    file_path = "products.pdf"
    if not os.path.exists(file_path):
        print(f"❌ ERROR: {file_path} not found.")
        return None

    loader = PDFMinerLoader(file_path)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    vs = FAISS.from_documents(chunks, embeddings)
    vs.save_local(vectorstore_path)
    return vs

vectorstore = get_vectorstore()
if not vectorstore:
    exit(1)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
print("✅ Vector store ready.")

# =========================
# 2. LLM - Claude Haiku-4-5 (2026 Working Model)
# =========================
llm = ChatAnthropic(
    model="claude-haiku-4-5",      # سستا، تیز اور تمہارے بیلنس کے لیے بہترین
    api_key=ANTHROPIC_API_KEY,
    temperature=0,
    max_tokens=1024,
    timeout=90,
    max_retries=3
)

print("✅ Using Claude Haiku-4-5 model")

# Read available images
pic_dir = os.path.join(os.getcwd(), "pic")
available_images = []
if os.path.exists(pic_dir):
    available_images = [f for f in os.listdir(pic_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg', '.webp'))]
images_list_str = ", ".join(available_images) if available_images else "None"

# =========================
# 3. PROMPT
# =========================
prompt = ChatPromptTemplate.from_template("""
You are an intelligent e-commerce assistant. Based ONLY on the following context, recommend items that match the user's question.

Context:
{context}

Question: {question}

You must return your response as a valid JSON array of objects. Do not include any markdown formatting or text outside the array.

Each object must follow this exact structure:
[
  {{
    "id": 1, 
    "name": "Product Name",
    "price": "$0.00",
    "category": "General",
    "image": "image_filename.jpg",
    "advantageTag": "Short Catchy Tag",
    "aiReason": "A 1-2 sentence explanation.",
    "description": "Additional details.",
    "advantages": ["Advantage 1", "Advantage 2"],
    "persuasivePitch": "A highly convincing pitch."
  }}
]

Images list: [{images_list}]
""")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, 
     "question": RunnablePassthrough(), 
     "images_list": lambda x: images_list_str}
    | prompt
    | llm
    | StrOutputParser()
)

# =========================
# 4. ROUTES
# =========================
@app.route("/api/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(pic_dir, filename)

@app.route("/api/chat", methods=["POST"])
def chat_negotiator():
    data = request.json or {}
    message = data.get("message", "")
    
    if not message:
        return jsonify({"reply": "I'm here to help! What are you looking for today?", "shouldSearch": False})

    chat_prompt = f"""
    You are an expert sales assistant. Find out what the customer wants.
    Initial request: "{message}"
    
    If they specified a product category (e.g. laptop, watch), respond helpfully and end with [SEARCH] plus a refined search query.
    If vague, ask clarifying questions.
    Give response very crispy  but to the point 
    """

    try:
        response = llm.invoke([SystemMessage(content=chat_prompt), HumanMessage(content=message)])
        reply_text = response.content
        should_search = "[SEARCH]" in reply_text
        
        search_query = ""
        clean_reply = reply_text
        if should_search:
            parts = reply_text.split("[SEARCH]")
            clean_reply = parts[0].strip()
            search_query = parts[1].strip() if len(parts) > 1 else message
        
        return jsonify({
            "reply": clean_reply,
            "shouldSearch": should_search,
            "searchQuery": search_query
        })
    except Exception as e:
        print(f"❌ Chat Error: {e}")
        return jsonify({"error": str(e), "reply": "I'm experiencing a brief pause. Try again in a moment!"}), 500

@app.route("/api/search", methods=["POST"])
def search_products():
    data = request.json
    query = data.get("query", "")
    if not query:
        return jsonify({"results": []})
    
    try:
        response_text = rag_chain.invoke(query)
        clean_text = response_text.strip()
        
        # Clean markdown if any
        if clean_text.startswith("```json"): 
            clean_text = clean_text[7:]
        if clean_text.startswith("```"): 
            clean_text = clean_text[3:]
        if clean_text.endswith("```"): 
            clean_text = clean_text[:-3]

        json_results = json.loads(clean_text)
        
        # Fix image URLs
        for item in json_results:
            if "image" in item and not item["image"].startswith("http"):
                encoded_name = urllib.parse.quote(item["image"])
                item["image"] = f"http://127.0.0.1:5000/api/images/{encoded_name}"
                
        return jsonify({"results": json_results})
    except Exception as e:
        print(f"❌ Search Error: {e}")
        return jsonify({"error": str(e), "results": []}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)