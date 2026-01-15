from dotenv import load_dotenv
from agent import reality_check_agent

load_dotenv()

def run_reality_check():
    print("🕵️ REALITY CHECK: Smart Reader Agent (Debug Mode)")
    print("-------------------------------------------------")
    
    book_title = input("Enter Book Title: ")
    highlight = input("Enter Highlight to Check: ")
    
    print("\n--- Agent Starting ---")
    
    initial_state = {
        "target_book": book_title,
        "highlight_text": highlight,
        "messages": [],
        "final_verdict": None 
    }
    
    try:
        # Run the agent
        result = reality_check_agent.invoke(initial_state)
        
        # --- DEBUGGING: Print what keys the agent returned ---
        print(f"\n[DEBUG] Keys returned by Agent: {list(result.keys())}")
        
        # Safe extraction
        verdict = result.get("final_verdict")
        
        # CRITICAL CHECK: Did we get a verdict?
        if verdict is None:
            print("\n❌ ERROR: The Agent finished, but 'final_verdict' is empty.")
            print("Possible causes:")
            print("1. The LLM refused to generate structured JSON.")
            print("2. The graph execution stopped early.")
            print("3. Check your .env file for OPENAI_API_KEY.")
            return

        # If we get here, verdict is safe to use
        print("\n" + "="*40)
        print(f"REPORT: {book_title}")
        print("="*40)
        print(f"📝 CLAIM:    {verdict.highlight_text}")
        print(f"🔎 QUERY:    {verdict.verification_query}")
        print(f"🛡️ STATUS:   {verdict.status}")
        print(f"💡 REASON:   {verdict.reasoning}")
        
        if verdict.alternative_recommendation:
            print(f"✨ TRY THIS: {verdict.alternative_recommendation}")
        print("="*40 + "\n")

    except Exception as e:
        print(f"\n❌ SYSTEM CRASH: {e}")
        # Print full traceback if needed
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_reality_check()