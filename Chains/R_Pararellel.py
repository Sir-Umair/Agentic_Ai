import os
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()


model = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    temperature=0.7,  
)
def plus(x: int):
    return x + 1
def times(x: int):
    return x * 2
def minus(x: int):
    return x - 1
def divide(x: int):
    return x / 2
plus_runnable = RunnableLambda(plus)
times_runnable = RunnableLambda(times)
minus_runnable = RunnableLambda(minus)
divide_runnable = RunnableLambda(divide)
parellel_runnable = RunnableParallel(
    plus=plus_runnable,
    times=times_runnable,
    minus=minus_runnable,
    divide=divide_runnable
)

prompt = ChatPromptTemplate.from_template(
    "I performed some math on a number. Results: {results}. "
    "Give me a fun fact about one of these numbers."
)
chain = parellel_runnable | prompt | model | StrOutputParser()

# Step 5: Run
response = chain.invoke(10)
print(response)            

