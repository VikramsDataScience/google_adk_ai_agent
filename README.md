## Multi Agentic AI using Google Agent Development Kit (ADK)

This project is an extension of the previous Agentic AI project that was built using <a href="https://github.com/VikramsDataScience/ocr_ai_agent/tree/main">Hugging Face's Smolagents</a> framework. The severe limitation with the Hugging Face framework is that their inference compute credits are extremely limited on a free tier. 
The only option for a free tier user like myself is to try to host the LLM locally. Since I'm quite GPU poor, hosting a decent LLM locally (even when it's been quantized to its lowest 4-bit precision) proved to be a very painstaking, and ultimately a fruitless endeavour 😩. So when I found out that Google's
ADK framework has a very generous free tier for their Gemini 2.0 Flash model, I wanted to build a very similar agent using their framework! And, of course, their GPUs 😉! Another reason is that the ADK framework has a whole bunch of front-end production friendly capabilities that come out of the box. This mean that we 
can focus more on building code and therefore prototype much faster, rather than playing around with TypeScript to build out frontend applications.<br>

If you'd like to run this agent yourself, after cloning this repo, please follow these steps:
- Install ADK `pip install google-adk`
- Get yourself an API key from https://aistudio.google.com/app/apikey
- For using the document Optical Character Recognition (OCR) agent, you'll also need an API key from <a href="https://console.mistral.ai/">Mistral</a>.
- You'll need to create a `.env` file that's actually called .env, but no actual filename (super important, otherwise ADK will have a heartattack). In that file you'll need to paste the API keys into `GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"`
`MISTRAL_API_KEY"YOUR_MISTRAL_API_KEY"`
- From the `C:\google_adk_ai_agent>` directory (assuming you're using a Windows machine) run the following command in the CLI: `adk web`. This will launch the front-end app, where you can follow the link in the terminal to open a new tab in your browser. From here you can test and use the research agent to help you find things!
Here's an example that is similar to the prompt I ran for the previous smolagents agent:
![image](https://github.com/user-attachments/assets/d19d643e-9f0f-4785-b858-250cb298a6ed)
The above was to test the OCR tool calling capability, and ensure that the Managing Agent (called the `root_agent` in ADK terminology) is able to correctly identify the use case to assign the task to the `OCR_Tool` agent (which is a sub-agent to the root_agent). So, the way that I've built this agent is actually not so much to use
just tool calling, but rather that I've built separate sub-agents under a managing agent. Each sub-agent has a specialist skillset that allows it to only complete certain types of tasks, before then reporting those results to the managing agent, which will then decide how best to use that data or information. In the above example
because the prompt asked for a summary and 4 insights into the DeepSeek Technical paper but also provided the exact link to the PDF on arXiv, we can see that the managing agent correctly assigns the OCR task to the 'OCR_Tool' agent. That sub-agent then performs the OCR on the arXiv paper, and feeds the results back to the managing
agent who then disseminates that information to answer the user's query.
