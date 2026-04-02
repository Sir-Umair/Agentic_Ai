import os
import time
from dotenv import load_dotenv

# LangChain imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_community.document_loaders import PDFMinerLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_anthropic import ChatAnthropic

# =========================
# 1. ENV SETUP
# =========================
load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")

print("🔍 DEBUG: API KEY LENGTH =", len(API_KEY) if API_KEY else "None")
print("🔍 DEBUG: API KEY START =", API_KEY[:15] if API_KEY else "None")

if not API_KEY:
    raise ValueError("❌ ANTHROPIC_API_KEY missing in .env")

# =========================
# 2. LOAD PDF & VECTOR STORE
# =========================
file_path = "products.pdf"
if not os.path.exists(file_path):
    raise FileNotFoundError(f"{file_path} not found")

print(f"📄 Loading: {file_path}")
loader = PDFMinerLoader(file_path)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(docs)
print(f"✅ Document split into {len(chunks)} chunks.")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})  # تھوڑا بڑھا دیا

print("✅ Vector store ready")

# =========================
# 3. LLM WITH RETRY (2026 MODELS)
# =========================
def get_llm():
    models = [
        "claude-haiku-4-5",      # سستا + تیز (تمہارے $4.76 بیلنس کے لیے بہترین)
        "claude-sonnet-4-6",     # balanced (اچھی کوالٹی)
        "claude-opus-4-6"        # طاقتور (اگر بیلنس ہو)
    ]

    for model_name in models:
        for attempt in range(3):  # 3 بار retry
            try:
                print(f"🔄 Trying model: {model_name} (attempt {attempt+1})")
                llm = ChatAnthropic(
                    model=model_name,
                    api_key=API_KEY,
                    temperature=0.1,
                    max_retries=3,
                    timeout=120,
                    max_tokens=1024
                )

                # Test call
                test = llm.invoke("Say 'Model ready' in one word.")
                print(f"✅ Using model: {model_name}")
                return llm

            except Exception as e:
                error_str = str(e).lower()
                print(f"❌ Attempt {attempt+1} failed: {model_name} -> {type(e).__name__}")

                if "high traffic" in error_str or "pause" in error_str or "rate limit" in error_str:
                    wait = 10 * (attempt + 1)
                    print(f"   🌐 High traffic detected. Waiting {wait} seconds...")
                    time.sleep(wait)
                elif "insufficient" in error_str or "balance" in error_str:
                    print("   💰 Balance too low. Add credits in Anthropic console.")
                    break
                else:
                    time.sleep(3)

    raise ValueError("❌ No working Anthropic model found after retries.\n"
                     "Check: 1) Billing & credits  2) Account Tier  3) Try after 5-10 min")

llm = get_llm()

# =========================
# 4. RAG CHAIN
# =========================
prompt = ChatPromptTemplate.from_template("""
You are a helpful AI shopping assistant for AuraStore.
Answer using ONLY the context below. Be friendly and concise.

Context:
{context}

Question: {question}
""")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

# =========================
# 5. TEST QUESTIONS
# =========================
questions = [
    "What are the main product categories?",
    "Does the document mention electronics?",
    "What is the summary of trending items?",
    "Recommend a good smartphone under $800"
]

print("\n🚀 Running Q&A...\n")

for q in questions:
    print(f"Q: {q}")
    try:
        response = rag_chain.invoke(q)
        print(f"A: {response}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")