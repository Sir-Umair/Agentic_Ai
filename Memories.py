from langchain_classic.memory import ConversationBufferMemory

# Standard setup for most chatbots
memory = ConversationBufferMemory(return_messages=True)
memory.save_context({"input": "Hi"}, {"output": "Hello"})
memory.save_context({"input": "My name is Umair"}, {"output": "Nice to meet you"})
memory.save_context({"input": "What is my name?"}, {"output": "Your name is Umair"})
print(memory.load_memory_variables({}))