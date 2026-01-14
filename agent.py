from typing import Annotated, TypedDict, List 
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition 
from langchain_openai import ChatOpenAI 
from langchain_core.messages import BaseMessage, SystemMessage
import operator

from tools import get_book_isbn, check_market_prices

# ---1. Define state... 
class ScoutState(TypedDict):
    # 'messages' tracks the conversation history 
    messages: Annotated[List[BaseMessage], operator.add]

# ---2. Setup tools and model---
tools = [get_book_isbn, check_market_prices] 

# We bind the tools to the model so it knows it can use them 
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# -- Define nodes--

def reasoner(state: ScoutState):
    """
    The agent decides what to do next based on the messages.
    """ 
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# --- 4. BUILD THE GRAPH ---

workflow = StateGraph(ScoutState) 

# Node: Reasoner (the brain)
workflow.add_node("agent", reasoner)

# Node: Tools (The Action) 
workflow.add_node("tools", ToolNode(tools))

# Entry point 
workflow.set_entry_point("agent")

# Logic:
# If the agent returns a tool call -> Go to 'tools' 
# If agent returns a final answer -> Go to END 
workflow.add_conditional_edges(
    "agent", 
    tools_condition,
)

# If tools run, always go back to agent to process the result 
workflow.add_edge("tools", "agent")

scout_app = workflow.compile() 
