import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

# api_key = os.getenv("GEMINI_API_KEY")
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0,
)

def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"It's always snowy in {city}!"

agent = create_agent(
    model=model,
    tools=[get_weather], 
    system_prompt="You are a helpful assistant",
)

# Run the agent 

response = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "What is the weather in Ottawa?"}
        ]
    }
)

print(response["messages"][-1].content)