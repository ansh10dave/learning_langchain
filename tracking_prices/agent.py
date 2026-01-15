# agent.py
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
import operator

from tools import get_book_isbn, check_market_prices

class ScoutState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

tools = [get_book_isbn, check_market_prices]
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools(tools)

def reasoner(state: ScoutState):
    system_msg = """
    You are a Canadian Book Scout. 
    
    PROTOCOL:
    1. IF user input does NOT specify "New" or "Used" (and it's the first turn), 
       ASK: "Would you like a New or Used copy?"
    
    2. ONCE condition is known:
       - Call 'get_book_isbn' to verify the book details (Title & Author).
       - **CRITICAL:** Call 'check_market_prices'. 
         - USE THE QUERY: "{Title} {Author}" (e.g. "Atomic Habits James Clear"). 
         - DO NOT use the ISBN for the price check (it is too strict).
         - Pass the 'condition' argument ("new" or "used").
    
    3. REPORTING:
       - Return the top 3 deals found.
       - ALWAYS include the specific Price, Seller, and Link.
       - If the tool returns empty results, STOP and say: "I couldn't find any deals online."
    """
    
    messages = [{"role": "system", "content": system_msg}] + state["messages"]
    return {"messages": [llm_with_tools.invoke(messages)]}

workflow = StateGraph(ScoutState)
workflow.add_node("agent", reasoner)
workflow.add_node("tools", ToolNode(tools))

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

scout_app = workflow.compile()