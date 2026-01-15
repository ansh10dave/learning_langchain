# tools.py
import os
import requests
from langchain_core.tools import tool

@tool
def get_book_isbn(query: str):
    """
    Input a book title. Returns the ISBN-13 and Title.
    Uses the public Google Books API (reliable & free).
    """
    print(f"📚 LIBRARIAN: Verifying '{query}'...")
    
    # Public API endpoint - No API Key needed for basic search
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    
    try:
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        return f"Connection Error: {e}"

    if "items" not in data:
        return "Book not found."
    
    # Grab the top result
    book = data["items"][0]["volumeInfo"]
    title = book.get("title", "Unknown")
    authors = ", ".join(book.get("authors", []))
    
    # Extract ISBN-13
    isbn = "Unknown"
    for identifier in book.get("industryIdentifiers", []):
        if identifier["type"] == "ISBN_13":
            isbn = identifier["identifier"]
    
    # If we found an ISBN, great. If not, returning the Title+Author is a good fallback.
    identifier = isbn if isbn != "Unknown" else f"{title} {authors}"
    
    return {
        "title": title,
        "author": authors,
        "isbn": identifier
    }

@tool
def check_market_prices(search_query: str, condition: str = "any"):
    """
    Input the ISBN (preferred) or 'Title + Author'.
    'condition' can be 'new', 'used', or 'any'.
    Searches Google Shopping (Canada) for real-time prices.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return "Error: SERPAPI_API_KEY not found in .env"

    print(f"🛍️ SHOPPER: Checking '{condition}' prices for '{search_query}'...")
    
    # Map 'new'/'used' to SerpApi filters
    tbs_param = "p_ord:p" # Sort by Price: Low to High
    if "new" in condition.lower():
        tbs_param += ",new:1"
    elif "used" in condition.lower():
        tbs_param += ",used:1"

    params = {
        "engine": "google_shopping",
        "q": search_query,
        "api_key": api_key,
        "location": "Ottawa, Ontario, Canada",
        "google_domain": "google.ca",
        "gl": "ca",
        "hl": "en",
        "num": 10,       
        "tbs": tbs_param 
    }
    
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        
        # --- DEBUGGING: If this fails, we will see why ---
        if "error" in data:
            print(f"⚠️ SERPAPI ERROR: {data['error']}")
            return f"SerpApi Error: {data['error']}"
            
    except Exception as e:
        return f"Connection Error: {e}"
    
    if "shopping_results" not in data:
        return "No sellers found. The book might be out of stock."
        
    results = []
    for item in data["shopping_results"]:
        link = item.get("link") or item.get("offer_url")
        if not link: continue
            
        results.append({
            "seller": item.get("source"),
            "price": item.get("price"),       
            "link": link,
            "condition": item.get("condition", "Unknown")
        })
        
        if len(results) >= 5: 
            break
            
    return results