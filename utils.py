import os
import re
from typing import List, Iterator, Tuple, Dict
from models import SearchParams

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading .env file
    pass

def get_valid_files(folder_path: str) -> Iterator[Tuple[str, str, str]]:
    """
    Generator that yields valid files from the folder, filtering out unwanted directories and files.
    
    Yields:
        Tuple[str, str, str]: (filepath, relative_path, filename)
    """
    for root, _, files in os.walk(folder_path):
        # Skip unwanted directories
        if any(pattern in root.lower() for pattern in [
            '.cache', '.local', '.vscode', '.ds_store', '.venv', '.git', 
            'venv', '__pycache__', 'site-packages', 'cloudstorage', 'clouddocs'
        ]):
            continue
            
        for file in files:
            # Skip hidden files and system files
            if file.startswith('.') or file.startswith('~') or file.endswith('.h'):
                continue
                
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, folder_path)
            
            yield filepath, rel_path, file

def parse_search_prompt_with_llm(prompt: str) -> SearchParams:
    """
    Use an LLM to parse the user prompt and extract search parameters.
    Replace this with actual LLM API calls (OpenAI, Claude, etc.)
    """
    # Standard prompt template for file search parsing
    system_prompt = """You are an expert file search parameter extraction assistant. Your task is to analyze user requests for file searches and extract structured parameters.

## Your Role:
- Parse natural language file search requests
- Extract relevant search criteria
- Return structured JSON data
- Be precise and consistent

## Output Format:
Always return ONLY valid JSON in this exact structure:
{
    "file_types": [],
    "filename_keywords": [],
    "content_keywords": [],
    "search_sequence": ["file_type", "filename", "content"],
    "search_logic": "AND"
}

## Field Definitions:
- file_types: File extensions (.pdf, .txt, .docx, .doc, .ipynb, .py, .js, etc.)
- filename_keywords: Keywords to appear in file names. If the keywrods are used to define file types, just ignore them here.
- content_keywords: Keywords likely to appear inside file contents
- search_sequence: Always use ["file_type", "filename", "content"]
- search_logic: Always use "AND" (files must match all criteria)

## Examples:
User: "find pdf files about machine learning"
Output: {"file_types": [".pdf"], "filename_keywords": ["machine", "learning"], "content_keywords": ["machine", "learning"], "search_sequence": ["file_type", "filename", "content"], "search_logic": "AND"}

User: "python scripts with neural network code"
Output: {"file_types": [".py"], "filename_keywords": ["neural", "network"], "content_keywords": ["neural", "network", "python"], "search_sequence": ["file_type", "filename", "content"], "search_logic": "AND"}"""
    
    user_prompt = f"""Parse this file search request:

Request: "{prompt}"

Return the JSON structure with extracted parameters."""
    
    try:
        from openai import OpenAI
        client = OpenAI()
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        llm_response = response.choices[0].message.content
        print(f"LLM Response: {llm_response}")  # Debug output
        
        if not llm_response or llm_response.strip() == "":
            raise ValueError("Empty response from OpenAI API")

        # Clean the response - remove any markdown code blocks or extra text
        llm_response = llm_response.strip()
        if llm_response.startswith("```json"):
            llm_response = llm_response[7:]
        if llm_response.startswith("```"):
            llm_response = llm_response[3:]
        if llm_response.endswith("```"):
            llm_response = llm_response[:-3]
        llm_response = llm_response.strip()

        import json
        parsed = json.loads(llm_response)
        return SearchParams(**parsed)
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        print(f"Raw LLM response: '{llm_response}'")
        return fallback_parse_prompt(prompt)
    except Exception as e:
        print(f"LLM parsing failed: {e}, falling back to rule-based parsing")
        return fallback_parse_prompt(prompt)

def fallback_parse_prompt(prompt: str) -> SearchParams:
    """Fallback rule-based parsing if LLM fails"""
    prompt_lower = prompt.lower()
    
    # Extract file types
    file_types = re.findall(r'\.(\w+)', prompt_lower)
    file_types = [f'.{ext}' for ext in file_types]
    
    # Remove file type mentions and extract keywords
    keyword_text = re.sub(r'\.(\w+)', '', prompt_lower)
    keywords = [word.strip() for word in keyword_text.split() if word.strip() and len(word) > 2]
    
    # Determine search logic from prompt
    search_logic = "OR" if any(word in prompt_lower for word in [' or ', ' either ', ' any ']) else "AND"
    
    return SearchParams(
        file_types=file_types,
        filename_keywords=keywords,
        content_keywords=keywords,
        search_sequence=["file_type", "filename", "content"],
        search_logic=search_logic
    )

def parse_search_prompt(prompt: str) -> SearchParams:
    """Main parsing function that uses LLM with fallback"""
    return parse_search_prompt_with_llm(prompt)

def validate_folder_path(folder_path: str) -> List[Dict[str, str]]:
    """Validate if folder path exists and is a directory"""
    if not os.path.exists(folder_path):
        return [{"error": f"Folder path {folder_path} does not exist"}]

    if not os.path.isdir(folder_path):
        return [{"error": f"{folder_path} is not a directory"}]
    
    return []


