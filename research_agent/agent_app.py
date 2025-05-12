from dotenv import load_dotenv
from os import getenv

from google.adk.agents import LlmAgent
from google.adk.tools import google_search, built_in_code_execution, agent_tool

import vertexai
from vertexai.preview import reasoning_engines

# Relative imports
from .tools import mistral_ocr_tool

########### DEFINE LLMS TO USE ###########
gemini_2point0_flash = "gemini-2.0-flash"

########### DEFINE SOME CONSTANTS THAT CAN BE USED FOR THE APP SESSIONS ###########
APP_NAME = "AI_Research_Agent"
USER_ID = "user_1"
SESSION_ID = "session_001"

########### INITIALISE VERTEX AI FOR DEPLOYMENT INTO GOOGLE CLOUD ###########
load_dotenv()
gc_location = getenv("GOOGLE_CLOUD_LOCATION")
gc_project_id = getenv("GOOGLE_PROJECT_ID")
gc_storage_uri= getenv("GOOGLE_CLOUD_STORAGE_BUCKET_URI")

vertexai.init(project=gc_project_id,
     location=gc_location,
     staging_bucket=gc_storage_uri,
     )

########### DEFINE THE AGENT AND TOOLS ###########
ocr_agent = LlmAgent(name="OCR_Agent",
                    model=gemini_2point0_flash,
                    description="Runs Optical Character Recognition (OCR) on a document (such as PDFs) using Mistral API",
                    instruction="""You'll need the exact URL of the document to use this tool. This tool returns the text extracted from the document in a JSON dictionary.
                        Please don't print out returned text from the tool. Only return your final response to the user.""",
                    tools=[mistral_ocr_tool],
                    )

search_agent = LlmAgent(name="Google_Search_Agent",
                      model=gemini_2point0_flash,
                      description="Use Google Search to conduct research and find relevant information.",
                      instruction="""To find relevant information, you'll need to use multiple search queries to gather sufficient information 
                      and data to robustly answer all aspects of the user's query.""",
                      tools=[google_search],
                    )

code_agent = LlmAgent(name="Code_Execution_Agent",
                      model=gemini_2point0_flash,
                      description="""Executes Python code to analyze and process data gathered during research.
                      Or if the user uploads CSV/XLSX files with instructions, perform code execution to analyze the data.""",
                      instruction="""You'll need to use the built_in_code_execution tool to generate code that can analyze 
                      and process the data gathered from your research such as parsing data, generating visualisations,
                      and running statistical tests. You can then parse the the code to the BaseCodeExecutor to execute it.
                      Additionally, you can use this tool to execute code, such as data analysis, visualisations, etc.
                      on provided CSV/XLSX files with instructions from the user.""",
                      tools=[built_in_code_execution],
                      # code_executor=BaseCodeExecutor().execute_code(),
                    )

root_agent = LlmAgent(name=APP_NAME,
                      model=gemini_2point0_flash,
                      description="""You're a helpful research assistant that can search the web, perform OCR, read documents that user's provide,
                      execute code, conduct in-depth research, and provide insights on complex topics.""",
                      instruction="""You are an AI research assistant with access to specific tools to help answer questions.
                      You have access to the ocr_agent, code_agent, and search_agent for research, code generation and analysis purposes.
                      If any of the agents return errors, politely inform the user that the agent has returned an error.
                      With respect to your final response:
                      1. Your final response should be detailed enough to justify being called an AI Research Assistant. In other words, when 
                      conducting searches, use as many search terms as you need to find relevant information and data. Don't only run 1 search term, 
                      and generate your final response!
                      2. Your final response should cover all aspects of the user's query. If you require clarification, ask the user follow-up questions.
                      3. You should not print out the raw text returned from the subagents, but provide polished and clear responses.
                      4. Make your response highly detailed, insightful, and verbose.""",
                      sub_agents=[ocr_agent],
                      tools=[agent_tool.AgentTool(agent=search_agent)], 
                      # agent_tool.AgentTool(agent=code_agent)],
                     )

app = reasoning_engines.AdkApp(agent=root_agent,
                               enable_tracing=True)

session = app.create_session(user_id=USER_ID,
                             session_id=SESSION_ID)

app.list_sessions(user_id=USER_ID)

session = app.get_session(user_id=USER_ID,
                          session_id=SESSION_ID)
print(session)

for event in app.stream_query(user_id=USER_ID,
                              session_id=SESSION_ID,
                              message="Hi"):
    
    print(event['content']['parts'][0]['text'])
