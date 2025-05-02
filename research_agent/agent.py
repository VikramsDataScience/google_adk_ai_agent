import asyncio

from google.adk.agents import LlmAgent
# from google.adk.models.lite_llm import LiteLlm # For multi-modal support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.tools import google_search

# Relative imports
from .tools import mistral_ocr_tool

########### DEFINE LLMS TO USE ###########
gemini_2point0_flash = "gemini-2.0-flash"

########### DEFINE SOME CONSTANTS THAT CAN BE USED FOR THE APP SESSIONS ###########
APP_NAME = "AI_Research_Agent"
USER_ID = "user_1"
SESSION_ID = "session_001"

########### DEFINE THE AGENT AND TOOLS ###########
ocr_tool = LlmAgent(name="OCR_Tool",
                    model=gemini_2point0_flash,
                    description="Runs Optical Character Recognition (OCR) on a document (such as PDFs) using Mistral API",
                    instruction="You'll need the exact URL of the document to use this tool. This tool returns the text extracted from the document in a JSON dictionary.\
                        Please don't print out returned text from the tool. Only return your final response to the user.",
                    tools=[mistral_ocr_tool],
                    )

search_tool = LlmAgent(name="Google_Search_Tool",
                      model=gemini_2point0_flash,
                      description="Searches the web for information using Google Search API",
                      instruction="You'll need to provide a search query to use this tool",
                      tools=[google_search],
                    )

root_agent = LlmAgent(name=APP_NAME,
                      model=gemini_2point0_flash,
                      description="You're a helpful research assistant that can search the web, perform OCR, read documents that user's provide,\
                        answer questions, and provide insights on complex topics.",
                      instruction="You are an AI research assistant with access to specific tools to help answer questions.\
                      You have access to the ocr_tool and search_tool for research purposes.\
                      If any of the tools return errors, politely inform the user that you are unable to use that tool.",
                      sub_agents=[search_tool, ocr_tool],
                     )

# Create conversation session
session_memory = InMemorySessionService()
session_memory.create_session(app_name=APP_NAME,
                            user_id=USER_ID,
                            session_id=SESSION_ID,
                            )

# Orchestrate the agent execution loop with the runner
runner = Runner(agent=root_agent,
                session_service=session_memory,
                app_name=APP_NAME,
                memory_service=session_memory,
                )


async def call_agent_async(query: str, runner=runner, user_id=USER_ID, session_id=SESSION_ID):
  """Sends a query to the agent and prints the final response."""
  print(f"\n>>> User Query: {query}")

  # Prepare the user's message in ADK format
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "Agent did not produce a final response."

  # Iterate through events to find the final answer.
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):

      # is_final_response() marks the concluding message for the turn.
      if event.is_final_response():
          if event.content and event.content.parts:
             # Assuming text response in the first part
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # Handle potential errors/escalations
             final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
          # Add more checks here if needed (e.g., specific error codes)
          break # Stop processing events once the final response is found
      
      print(f"\n>>> Final Response: {final_response_text}")

async def run_conversation():
       """Given the potential for numerous API calls that may result in I/O requests, 
       run the conversation with the agent asynchronously."""

       await call_agent_async()


if __name__ == "__main__":
    asyncio.run(run_conversation())
