import os
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()

# Step 1: Create preprocessing function
def clean_text(text):
    return text.strip().lower()

# Step 2: Convert function into Runnable
clean_runnable = RunnableLambda(clean_text)
def add_emoji(text):
    return text + " 🤖"
emoji_runnable = RunnableLambda(add_emoji)
# Step 3: LLM
model = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    temperature=0.7,
   
)

# Step 4: Pipeline
chain = clean_runnable | emoji_runnable | model

# Step 5: Run
response = chain.invoke("   WHAT IS LANGCHAIN?   ")
print(response.content)
# print(response)
