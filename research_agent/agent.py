import asyncio

from google.adk.agents import LlmAgent
# from google.adk.models.lite_llm import LiteLlm # For multi-modal support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.tools import google_search, built_in_code_execution, agent_tool

# Relative imports
from .tools import mistral_ocr_tool

########### DEFINE LLMS TO USE ###########
gemini_2point0_flash = "gemini-2.0-flash"

########### DEFINE SOME CONSTANTS THAT CAN BE USED FOR THE APP SESSIONS ###########
APP_NAME = "AI_Research_Agent"
USER_ID = "user_1"
SESSION_ID = "session_001"

########### DEFINE THE AGENT AND TOOLS ###########
ocr_agent = LlmAgent(name="OCR_Agent",
                    model=gemini_2point0_flash,
                    description="Runs Optical Character Recognition (OCR) on a document (such as PDFs) using Mistral API",
                    instruction="You'll need the exact URL of the document to use this tool. This tool returns the text extracted from the document in a JSON dictionary.\
                        Please don't print out returned text from the tool. Only return your final response to the user.",
                    tools=[mistral_ocr_tool],
                    )

search_agent = LlmAgent(name="Google_Search_Agent",
                      model=gemini_2point0_flash,
                      description="Searches the web for information using Google Search",
                      instruction="You'll need to provide a search query to use this tool",
                      tools=[google_search],
                    )

code_agent = LlmAgent(name="Code_Execution_Agent",
                      model=gemini_2point0_flash,
                      description="Executes Python code to analyze and process data gathered during research.\
                      Or if the user uploads CSV/XLSX files with instructions, perform code execution to analyze the data.",
                      instruction="You'll need to use this tool to analyze and process the data gathered from your research \
                      such as parsing data, generating visualisations, and running statistical tests.\
                      Or you can use this tool to perform code execution on a user provided CSV/XLSX file with instructions from the user.",
                      tools=[built_in_code_execution],
                    )

root_agent = LlmAgent(name=APP_NAME,
                      model=gemini_2point0_flash,
                      description="You're a helpful research assistant that can search the web, perform OCR, read documents that user's provide,\
                      execute code, conduct in-depth research, and provide insights on complex topics.",
                      instruction="You are an AI research assistant with access to specific tools to help answer questions.\
                      You have access to the ocr_agent, code_agent, and search_agent for research, code generation and analysis purposes.\
                      If any of the agents return errors, politely inform the user that the agent has returned an error.",
                      sub_agents=[ocr_agent],
                      tools=[agent_tool.AgentTool(agent=search_agent), 
                      agent_tool.AgentTool(agent=code_agent)],
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
