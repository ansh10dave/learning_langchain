from langchain_openai import ChatOpenAI 
from langgraph.graph import StateGraph, END 
from langchain_core.messages import SystemMessage, HumanMessage 

# Import our custom parts 
from state import AgentState, FactCheck 
from tools import fetch_book_context, verify_highlight 

# ------ Setup the LLM -----
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# ---- NODES (The Steps) ----
 
def get_book_context(state: AgenState):
    """ Step 1: Understand the Book"""
    book = state["target_book"]

    # Run the tool directly 
    context_data = fetch_book_context.invoke(book)
    
    # Create a message to store in memory 
    context_msg = f"Context for book'{book}':\n{context_data['description']}"

    return {"messages": [SystemMessage(content=context_msg)]}

def investigate_highlight(state: AgentState):
    """ Step 2: Search for the truth. """
    highlight = state["highlight_text"]
    book = state["target_book"]

    # 1. Ask the LLM to write a good search query 
    query_gen_prompt = f"""
    I am reading '{book}'. 
    I higlighted this text: "{highlight}"

    Write a Google search query to check if this is true claim in 2026. 
    Focus on "is this still true" or "modern criticism". Search all the newly published papers and studies.
    Output only the query. 
    """
    search_query = llm.invoke(query_gen_prompt).content.strip('"')

    # 2. Run the search tool 
    evidence = verify_highlight.invoke(search_query)

    # 3. Store the evidence 
    evidence_msg = f"""
    SEARCH query used: {search_query}
    Evidence found: 
    {evidence}
    """ 

    return {"messages": [HumanMessage(content=evidence_msg)]}

def judge_verdict(state: AgentState):
    """ Step 3: The Final Decision""" 

    # We bind the Pydantic model to the LLM to force JSON output 
    structured_llm = llm.with_structured_output(FactCheck)

    system_prompt = """
    You are a Fact Checking Editor. 
    Review the Highlight, the Book Context, and the Search Evidence.
    
    Determine if the highlight is:
    - VERIFIED (Evidence supports it)
    - OUTDATED (It was true then, but false/bad advice now)
    - DEBUNKED (It was never true)
    - NUANCED (It's complicated)
    
    Fill out the report accurately.
    """
    
    # We pass the full history (Context -> Evidence) to the Judge
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    # Generate the Pydantic object
    verdict = structured_llm.invoke(messages)
    
    return {"final_verdict": verdict}

## ----- Graph Construction -----

workflow = StateGraph(AgentState)

# Add nodes 
workflow.add_node("get_context", get_book_context)
workflow.add_node("investigate", investigate_highlight)
workflow.add_node("judge", judge_verdict)

# Set flow 
workflow.set_entry_point("get_context")
workflow.add_edge("get_context", "investigate")
workflow.add_edge("investigate", "judge")
workflow.add_edge("judge", END) 

# Compile 
reality_check_agent = workflow.compile() 
