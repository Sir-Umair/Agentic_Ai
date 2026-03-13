from langchain_classic.memory import ConversationBufferWindowMemory
memory = ConversationBufferWindowMemory(k=1)
memory.save_context({"input": "Hi"}, {"output": "Hello"})
memory.save_context({"input":"My name is Umair"},{"output":"Nice to meet you Umair"})
print(memory.load_memory_variables({}))