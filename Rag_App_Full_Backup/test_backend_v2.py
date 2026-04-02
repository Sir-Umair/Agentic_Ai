import os
import json
import traceback
from app import app, llm, rag_chain
from langchain_core.messages import HumanMessage, SystemMessage

def test_chat():
    print("Testing /api/chat...")
    try:
        message = "I want to buy a laptop"
        chat_prompt = f"""
        You are an expert, highly persuasive sales assistant. Your job is to find out exactly what the customer wants to buy.
        The customer says: "{message}"
        
        If their message already contains enough information to search for specific product categories (e.g. laptops, gym equipment, coffee machines), respond with something like: "Great! I'm searching our premium catalog for [their request] right now." and end with a special token [SEARCH].
        
        If their message is too vague, ask a clarifying question to narrow down their preferences (e.g., budget, specific features, brand preferences).
        
        Respond directly to the user in a friendly, helpful, and concise manner.
        """
        response = llm.invoke([SystemMessage(content=chat_prompt), HumanMessage(content=message)])
        print("Chat response:", response.content)
    except Exception as e:
        print("Chat failed:")
        traceback.print_exc()

def test_search():
    print("\nTesting rag_chain...")
    try:
        response = rag_chain.invoke("laptop")
        print("Search response:", response)
    except Exception as e:
        print("Search failed:")
        traceback.print_exc()

if __name__ == "__main__":
    test_chat()
    test_search()
