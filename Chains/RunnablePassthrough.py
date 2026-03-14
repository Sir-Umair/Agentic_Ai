import os
from langchain_core.runnables import RunnableLambda,RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()


def add_prefix(text):
    return f"Input received: {text}"

prefix_runnable = RunnableLambda(add_prefix)

chain = RunnablePassthrough() | prefix_runnable

print(chain.invoke("LangChain"))
