import os
from dotenv import load_dotenv

from langchain_classic.memory import ConversationSummaryMemory
from langchain_anthropic import ChatAnthropic

load_dotenv()

# Use a current model (claude-3-haiku-20240307 is deprecated; 3.5 retired Feb 2026)
llm = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.7,
)

memory = ConversationSummaryMemory(llm=llm, return_messages=True)

memory.save_context({"input": "Hi"}, {"output": "Hello"})
memory.save_context(
    {"input": "What is your stance regarding these wars?"},
    {"output": "I don't take political positions; my role is to provide balanced, factual information and help people think through issues thoughtfully."},
)
memory.save_context({"input":"conversation was about which topic?"},{"output":"conversation was about the wars in the middle east"})

print(memory.load_memory_variables({}))