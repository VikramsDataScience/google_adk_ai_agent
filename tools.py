import time
import random
import httpx
from markdownify import markdownify
from typing import Optional, Dict
from pathlib import Path
from dotenv import load_dotenv
from os import getenv

from mistralai import Mistral
from duckduckgo_search import DDGS
from serpapi import search
import pandas as pd


def fetch_full_page(url: str) -> Optional[str]:
    """This is not a tool, but a helper function that can be used 
    by the duckduckgo_search_tool() to fetch full page content from a URL."""
    
    try:
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
            return markdownify(response.text)
        
    except Exception as e:
        print(f"Error fetching page content for URL: {e}")
        return None


def duckduckgo_search_tool(query: str, max_results: int = 3, full_page: bool = True) -> Dict[str, list[dict[str, any]]]:
    """
    A tool to parse search query via _query_ arg, 
    run search using DuckDuckGo and return top 3 results.
    N.B. USE SPARINGLY TO AVOID API LIMITS!
    
    Args:
        query: The search query to be parsed to the DuckDuckGo search engine.
        max_results: The maximum number of search results to return.
        full_page: Whether to return full page content or not. If True, it will use 
        the fetch_full_page() helper function.
        
    Returns:
        dict: A dict where the values are a list of dictionaries containing the search results."""

    try:
        ddgs = DDGS(headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        results = []
        search_results = list(ddgs.text(keywords=query,
                        max_results=max_results))
        
        for r in search_results:
            url = r.get("href")
            title = r.get("title")
            search_content = r.get("body")
            
            # If full_page is True, fetch full page content using the fetch_full_page() helper function
            if full_page:
                full_page_content = fetch_full_page(url)

            # Append search results to list
            result = {
                "title": title,
                "url": url,
                "search_content": search_content,
                "full_page_content": full_page_content
            }
            results.append(result)

            return {"results": results}

    except Exception as e:
        print(f"DuckDuckGo API limit reached. Attempting randomized delay: {e}. \nRetrying after a delay...")
        time.sleep(random.uniform(10, 30))  # Randomized backoff to avoid detection
        print(f"Full error stack trace: {type(e).__name__}")

    return results

def google_search_serpapi(query: str) -> Dict[str, dict[str, any]]:
    """
    A tool to run Google searches via SerpAPI.
    
    Args:
        query: The search query to be parsed to the Google search engine.
        
    Returns:
        dict: A dict where the values are a list of dictionaries containing the search results."""

    # Load environment variables from the .env file
    load_dotenv()
    serpapi_api_key = getenv("SERPAPI_API_KEY")

    params_dict = {"q": query, 
                   "location": "Melbourne, Australia",
                    "hl": "en",
                    "gl": "au",
                    "google_domain": "google.com.au",
                    "api_key": serpapi_api_key}

    search_results = search(**params_dict)
    
    return search_results


def mistral_ocr_tool(document_url: str) -> str:
    """ 
    A tool to parse document URL via _document_url_ arg, 
    and run OCR using Mistral API.
    
    Args:
        document_url: The URL of the document to be processed. 
        Must be a publicly accessible URL pointing to a PDF document.
        
    Returns:
        str: All the extracted text from the document."""
    
    # Load environment variables from the .env file
    load_dotenv()
    mistral_api_key = getenv("MISTRAL_API_KEY")

    if not mistral_api_key:
        raise ValueError("Mistral API key not found. Please provide a valid Mistral API key.")
    
    client = Mistral(api_key=mistral_api_key)
    
    pdf_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
        "type": "document_url",
        "document_url": document_url,
    },
    include_image_base64=True
    )
    
    # Perform markdown on the extracted text
    extracted_text = "\n\n".join(page.markdown for page in pdf_response.pages)

    return extracted_text


def read_csv_xlsx(file_path: Path, sheet_name = Optional[str]) -> pd.DataFrame:
    """
    A tool to read CSV or XLSX files from a user provided file path 
    and returns a Pandas DataFrame. If the file is an XLSX, you'll need to ask 
    the to provide the name of the sheet to read from the XLSX file.
    
    Args:
        file_path: The path to the CSV or XLSX file.
        sheet_name: If the _file_path_ suffix is an XLSX, the 
        name of the sheet to read from the XLSX file.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the data from the file."""
    
    try:
        if '.xlsx' in file_path.suffix:
            df = pd.read_excel(file_path, sheet_name)
        elif '.csv' in file_path.suffix:
            df = pd.read_csv(file_path)
        else:
            raise ValueError("Unsupported file format or incorrect file path. Please provide a valid path that points to a CSV or XLSX file.")
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    return df