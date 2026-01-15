# agent.py (Robust Debug Version)
import json
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.utils.function_calling import convert_to_openai_function

# Import our custom parts
from state import AgentState, FactCheck
from tools import fetch_book_context, verify_highlight

# --- SETUP THE LLM ---
# We use a standard LLM first, then bind structure later
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# --- NODES (The Steps) ---

def get_book_context(state: AgentState):
    print("   [Node] 1. Get Book Context: STARTED")
    book = state["target_book"]
    
    # Run the tool
    try:
        context_data = fetch_book_context.invoke(book)
        
        # Safe extraction
        if isinstance(context_data, str):
            description = context_data  
        else:
            description = context_data.get('description', 'No description available.')
            
        # Truncate description to prevent context overflow (First 2000 chars is usually enough)
        if len(description) > 2000:
            description = description[:2000] + "...(truncated)"

        context_msg = f"CONTEXT FOR BOOK '{book}':\n{description}"
        print("   [Node] 1. Get Book Context: SUCCESS")
        return {"messages": [SystemMessage(content=context_msg)]}
        
    except Exception as e:
        print(f"   [Node] 1. ERROR: {e}")
        return {"messages": [SystemMessage(content=f"Context Error: {e}")]}

def investigate_highlight(state: AgentState):
    print("   [Node] 2. Investigate Highlight: STARTED")
    highlight = state["highlight_text"]
    book = state["target_book"]
    
    # 1. Generate safe query
    query_gen_prompt = f"""
    I am reading '{book}'.
    I highlighted this text: "{highlight}"
    
    Write a simple, 5-8 word Google search query to check if this is true in 2026.
    Do NOT use operators. Just keywords.
    """
    
    try:
        search_query = llm.invoke(query_gen_prompt).content.replace('"', '').strip()
        print(f"   [Node] 2. Generated Query: {search_query}")
        
        # 2. Run the search tool
        evidence = verify_highlight.invoke(search_query)
        
        evidence_msg = f"""
        SEARCH QUERY USED: {search_query}
        EVIDENCE FOUND:
        {evidence}
        """
        print("   [Node] 2. Investigate Highlight: SUCCESS")
        return {"messages": [HumanMessage(content=evidence_msg)]}
        
    except Exception as e:
        print(f"   [Node] 2. ERROR: {e}")
        return {"messages": [HumanMessage(content=f"Search Failed: {e}")]}

def judge_verdict(state: AgentState):
    print("   [Node] 3. Judge Verdict: STARTED")
    
    # Bind the Pydantic model
    structured_llm = llm.with_structured_output(FactCheck)
    
    system_prompt = """
    You are a Fact Checking Editor. 
    Review the Highlight, the Book Context, and the Search Evidence.
    
    Determine if the highlight is:
    - VERIFIED (Evidence supports it)
    - OUTDATED (It was true then, but false/bad advice now)
    - DEBUNKED (It was never true)
    - NUANCED (It's complicated)
    
    Fill out the JSON report accurately.
    """
    
    # Compile messages
    # We take the LAST 5 messages to ensure we don't overload context
    recent_messages = state["messages"][-5:]
    messages = [SystemMessage(content=system_prompt)] + recent_messages
    
    try:
        print("   [Node] 3. Calling LLM for JSON...")
        verdict = structured_llm.invoke(messages)
        
        if verdict:
            print("   [Node] 3. Judge Verdict: SUCCESS (JSON Generated)")
            return {"final_verdict": verdict}
        else:
            print("   [Node] 3. ERROR: LLM returned Empty Result")
            return {"final_verdict": None}
            
    except Exception as e:
        print(f"   [Node] 3. CRASH: {e}")
        # Return a dummy verdict so the app doesn't crash
        return {"final_verdict": None}

# --- GRAPH CONSTRUCTION ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("get_context", get_book_context)
workflow.add_node("investigate", investigate_highlight)
workflow.add_node("judge", judge_verdict)

# Set Flow
workflow.set_entry_point("get_context")
workflow.add_edge("get_context", "investigate")
workflow.add_edge("investigate", "judge")
workflow.add_edge("judge", END)

# Compile
reality_check_agent = workflow.compile()