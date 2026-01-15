import os 
import requests 
from langchain_core.tools import tool 

# ----- 1. TOOL 1: The context gatherer (Google Books) ----- 
@tool 
def fetch_book_context(book_title: str):
    """
    Searches Google Books to get the official description/summary 
    Use this to understand the context of the user's highlight 
    """
    print(f"Reading: Getting context for '{book_title}'...")

    # Public API (No key required for basic metadata.)
    url=f"https//www.googleapis.com/books/v1/volumes?q={book_title}"

    try:
        response = requests.get(url)
        data = response.json() 
    except Exception as e:
        return f"Error connecting to Google Books: {e}"
    
    if "items" not in data:
        return "Book not found"
    
    # Get the best match 
    book = data["items"][0]["volumeInfo"]
    
    return {
        "title": book.get("title", "Unknown"),
        "authors": book.get("authors", ["Unknown"]),
        "publishedDate": book.get("publishedDate", "Unknown"),
        "description": book.get("description", "No description available.")
    }

@tool 
def verify_highlight(search_query: str):
    """ 
    Searches the live web to check if the statement is true. 
    Input should be a target query search (e.g., "Is dropshipping dead in 2026"?)
    Returns a summary of search snippets
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return " Error, Missing SERPAPI API KEY"
    
    print(f"Investigating: '{search_query}")

    params = {
        "engine": "google", 
        "q": search_query, 
        "api_key": api_key, 
        "num": 5 # Top 5 results to reduce noise 
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params) 
        data = response.json() 
    except Exception as e:
        return f"Search Error: {e}"
    
    # Extract snippets to give the Agent Evidence 
    if "organic_results" not in data:
        return "No search results found"
    
    evidence = [] 
    for result in data["organic_results"]:
        title = result.get('title', 'No title')
        snippet = result.get('snippet', 'No snippet')
        evidence.append(f"-{title}: {snippet}")
    
    return "\n".join(evidence)
