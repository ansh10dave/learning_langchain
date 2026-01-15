from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from agent import scout_app 

# Load Keys 
load_dotenv() 

def run_scout():
    print("Book Scout: Ottawa Edition")
    print ("Type your requests")
    print("Type 'q' to quit")

    # Define the persona 
    system_prompt = """ 
    You are a Book Scout Agent.
    Your Goal: Find the best deal for the user. 

    RULES:
    1. ALWAYS get the ISBN first using 'get_book_isbn'. Searching by name is inaccurate.
    2. Then check prices using 'check_market_prices'.
    3. Analyze the results. If a price is in CAD, mention that.
    4. Provide the link to the best deal found.
    """ 

    # Persistent chat history for this session 
    chat_history = [SystemMessage(content=system_prompt)]

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'q':
            break

        # Add user message to history 
        chat_history.append(HumanMessage(content=user_input))

        # Run agents
        inputs = {"messages": chat_history}

        print ("\n---Scout is working...") 

        for event in scout_app.stream(inputs):
            # We print tools outputs as they happen for visibility 
            for key, value in event.items():
                if key == "tools":
                    # value['messages'][0] is the tool output message
                    tool_output = value['messages'][0].content
                    # Just print a snippet so it's not too noisy
                    print(f"Checking data sources...")

        # The final result is the last message in the state
        # We need to fetch the final state to get the agent's actual answer
        final_state = scout_app.invoke(inputs)
        agent_response = final_state["messages"][-1].content
        
        print(f"\n🤖 SCOUT: {agent_response}\n")
        
        # Add agent response to history so you can ask follow-ups
        # e.g., "Is there anything cheaper?"
        chat_history.append(final_state["messages"][-1])

if __name__ == "__main__":
    run_scout()


