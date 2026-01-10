from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain.agents import create_agent

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
model_for_computer_use = ChatGoogleGenerativeAI(model="gemini-2.5-computer-use-preview-10-2025")

# response = model.invoke(
#     "Summarize the spoiler free reviews at https://www.goodreads.com/book/show/2767052-the-hunger-games", 
#     tools=[{"url_context": {}}],
# )

# response = model.invoke(
#     "Use Python to calculate 3^3.",
#     tools=[{"code_execution": {}}], 
# )

response = model_for_computer_use.invoke(
    "Please navigate to indeed.ca",
    tools=[{"computer_use": {}}], 
)

print(response.content_blocks)



# agent = create_agent(
#     model=model, 
#     tools=[{"google_maps":{}}], 
# )


# response = agent.invoke(
#     {
#         "messages": [
#             {"role": "user", "content":"Using google maps, How far is 481 Brigatine avenue from 17 hackney private, stiitsville, can you give me directions" }
#         ]
#     }
# )
    

# print(response["messages"][-1].content)


