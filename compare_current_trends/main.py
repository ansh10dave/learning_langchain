from dotenv import load_dotenv
from agent import reality_check_agent

load_dotenv() 

def run_reality_check():
    print("Reality check: Smart Reader Agent")
    print("---------------")

    # 1. Get user input 
    book_title= input("Enter Book Title: ")
    highlight= input("Enter Highlight to check: ")

    print("\n--- Agent Starting ---")

    # 2. Initialize agent 
    initial_state = {
        "target_book": book_title, 
        "highlight_text": highlight, 
        "messages": []
    }

    # 3. Run the graph 
    result = reality_check_agent.invoke(initial_state)

    # 4. Display Result 
    verdict = result["final_verdict"]

    print("\n" + "="*40)
    print(f"Report: {book_title}")
    print("="*40)
    print(f"CLAIM: {verdict.highlight_text}")
    print(f"QUERY: {verdict.verification_query}")
    print(f"STATUS: {verdict.status}")
    print(f"REASON: {verdict.reasoning}")

    if verdict.alternative_recommendation:
        print(f"TRY THIS: {verdict.alternative_recommendation}")
    
    print("="*40 + "\n")

if __name__ == "__main__":
    run_reality_check() 

