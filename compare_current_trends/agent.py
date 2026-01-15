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
