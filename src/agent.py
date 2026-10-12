from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
load_dotenv()



model = init_chat_model(model="gemini-3.5-flash-lite", 
        model_provider="google_genai")

from langchain.agents import create_agent
from langchain.messages import HumanMessage


agent = create_agent(
    model=model,
    #tools=[search_handbook],
    system_prompt="You are a helpful agent."
    )

message = input()

result = agent.invoke(
    {"messages": [HumanMessage(content=message)]})
print(result["messages"][-1].content[0]["text"])