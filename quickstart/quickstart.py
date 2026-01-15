import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from dataclasses import dataclass 
from langchain.tools import tool, ToolRuntime

# api_key = os.getenv("GEMINI_API_KEY")
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0,
)

# def get_weather(city: str) -> str:
#     """Get the weather for a given city."""
#     return f"It's always snowy in {city}!"

# agent = create_agent(
#     model=model,
#     tools=[get_weather], 
#     system_prompt="You are a helpful assistant",
# )

# # Run the agent 

# response = agent.invoke(
#     {
#         "messages": [
#             {"role": "user", "content": "What is the weather in Ottawa?"}
#         ]
#     }
# )

# print(response["messages"][-1].content)

## Building a real-world agent 
SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns.

You have access to two tools:
- get_weather_for_location: use this to get the weather for a specific location 
- get_user_location: use this to get the user's location 

If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean
wherever they are, use the get_user_location tool to find the location. """ 

@tool
def get_weather_for_location(city: str) -> str:
    """Get the weather for a specific location."""
    return f"It's always snowy in {city}!"

@dataclass 
class Context:
    """Custom runtime context schema."""
    user_id: str 

@tool 
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user info based on user ID."""
    user_id = runtime.context.user_id 
    return "Ottawa" if user_id == "1" else "Toronto" 

## Response format (A punny response)
@dataclass 
class ResponseFormat: 
    """Response format for the weather agent."""
    # A punny response (always required) 
    punny_response: str 
    # Any interesting information about the weather (optional)
    weather_conditions: str | None = None 

## Adding memory 
from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver() 

from langchain.agents.structured_output import ToolStrategy 

agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT, 
    tools=[get_user_location, get_weather_for_location], 
    context_schema=Context, 
    response_format=ToolStrategy(ResponseFormat), 
    checkpointer=checkpointer
) 

# `thread_id` is unique identifier for a given conversation 
config = {"configurable": {"thread_id": "1"}}

response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather outside"}]},
    config=config, 
    context=Context(user_id="1")
)

print(response['structured_response'])
