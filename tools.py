import requests 
import os 
from langchain_core.tools import tool 

@tool 
def get_book_isbn(query: str):
    """
    Input a book title (e.g., "Deep Work Cal New Port").
    Returns the ISBN-13, exact title and author. 
    ALWAYS run this first to get the correct ISBN 
    """
    print(f"Librarian: Searching Google Books for '{query}'...")

    # We use the public Google Books API (no key needed for basic search)
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url)

    if response.status_code != 200:
        return "Error connecting to Google Books"
    
    data = response.json 
    if "items" not in data:
        return "Book not found"
    
    # Get the best match 
    book = data["items"][0]["volumeInfo"]
    title = book.get("title", "Unknown")
    authors = ", ".join(book.get("authors", []))

    # Extract ISBN-13 
    isbn = "Unknown" 
    for identifier in book.get("industryIdentifiers", []):
        if identifier["type"] == "ISBN_13":
            isbn = identifier["identifier"] 
    
    return f"Found: {title} by {authors}. ISBN-13: {isbn}"

@tool 
def check_market_prices(isbn: str, title: str):
    """
    Input the ISBN-13. 
    Searches online stores (Amazon, Indigo, eBay, etc...) for real-time prices 
    Returns a list of sellers and prices in CAD
    """ 
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return "Error: Missing SerpAPI Key."
    
    print(f"Shopper: Checking prices for Book {title}... ")

    params = {
        "engine": "google_shopping",
        "q": isbn,
        "api_key" = api_key,
        "location": "Ottawa, Ontario, Canada",
        "google_domain": "google.ca",
        "gl": "ca",
        "hl": "en",
        "num": 5
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json() 
    except Exception as e:
        return f"Search Error: {str(e)}" 
    
    if "shopping_results" not in data:
        return "No sellers found. The book might be out of stock."
    
    results = [] 
    for item in data["shopping_results"][:5]:
        results.append({
            "seller": item.get("source"),
            "price": item.get("price"), 
            "link": item.get("link"),
            "shipping": item.get("delivery", "Unknown Shipping")
        })
    
    return results 

