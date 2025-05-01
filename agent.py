import asyncio

from google.adk.agents import Agent
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

root_agent = Agent(name=APP_NAME,
                       model=gemini_2point0_flash,
                       description="A research assistant that can search the web, read documents, and answer questions.",
                       instruction="""You are an AI research assistant with access to specific tools to help answer questions.
                       You have access to the following tools (with instructions on how to use them contained in their docstrings):
                       mistral_ocr_tool, google_search, and read_csv_xlsx.
                       If any of the tools return errors, politely inform the user that you are unable to use that tool.""",
                       tools=[google_search],
                     )

# Create conversation session
session_memory = InMemorySessionService()
session_memory.create_session(app_name=APP_NAME,
                            user_id=USER_ID,
                            session_id=SESSION_ID)

# Orchestrate the agent execution loop with the runner
runner = Runner(agent=root_agent,
                 session_service=session_memory,
                 app_name=APP_NAME)

prompt = "Please list 3 key insights you are able to glean by conducting a search on the Deepseek R1 technical paper. Additionally, see if you can find the technical paper itself on arxiv. If so, please list the URL of the paper."

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

       await call_agent_async(prompt)


if __name__ == "__main__":
    asyncio.run(run_conversation())
