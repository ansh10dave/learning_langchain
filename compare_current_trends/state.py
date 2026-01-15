from typing import List, Optional, Literal 
from pydantic import BaseModel, Field 
from typing import TypedDict, Annotated 
import operator 
from langchain_core.messages import BaseMessage 

# ---------------- 1. The Data Models (What the report looks like) --------------
class FactCheck(BaseModel):
    highlight_text: str = Field(description="The specific advice or claim from the book highlighted by user")
    verification_query: str = Field(description="The search query used to check the claim")
    search_evidence: str = Field(description="Summary of real-world search results found")
    status: Literal["VERIFIED", "OUTDATED", "DEBUNKED", "NUANCED"] = Field(description="The final verdict")# <--- Constrained choice 
    reasoning: str = Field(description="Why this verdict was reached")
    alternative_recommendation: Optional[str] = Field(description="Modern alternative if claim is outdated")
    ### E.g. for alternative recommendation: CLaim: Use Odesk for hiring. Recommendation: Use upwork or fiverr instead. 


# 3. The working memory (Clipboard) 
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add] # <--- Chat History 
    
    target_book: str                # <----- Context
    highlight_text: List[str]     # <----- Scratchpad (To-do list)
    
    final_verdict: Optional[FactCheck] # <------- The Goal (Starts empty) 
