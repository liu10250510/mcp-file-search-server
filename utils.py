import os
import re
import logging
from typing import List, Iterator, Tuple, Dict
from models import SearchParams

# Get logger
logger = logging.getLogger('FastMCP_FileSearch')

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
    logger.debug(f"parse_search_prompt_with_llm() called with prompt: '{prompt}'")
    
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
        logger.info("🤖 Making LLM API call to parse search prompt")
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
        logger.info(f"✅ LLM API call successful. Response length: {len(llm_response) if llm_response else 0} characters")
        logger.debug(f"LLM raw response: {llm_response}")
        
        if not llm_response or llm_response.strip() == "":
            logger.error("Empty response from OpenAI API")
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
        logger.debug(f"Cleaned LLM response: {llm_response}")

        import json
        parsed = json.loads(llm_response)
        logger.info(f"✅ Successfully parsed LLM response into SearchParams")
        logger.debug(f"Parsed parameters: {parsed}")
        return SearchParams(**parsed)
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing failed: {e}")
        logger.error(f"Raw LLM response: '{llm_response}'")
        logger.info("🔄 Falling back to rule-based parsing")
        return fallback_parse_prompt(prompt)
    except Exception as e:
        logger.error(f"❌ LLM parsing failed: {e}")
        logger.info("🔄 Falling back to rule-based parsing")
        return fallback_parse_prompt(prompt)

def fallback_parse_prompt(prompt: str) -> SearchParams:
    """Fallback rule-based parsing if LLM fails"""
    logger.info("🔧 Using fallback rule-based parsing")
    logger.debug(f"Fallback parsing prompt: '{prompt}'")
    
    prompt_lower = prompt.lower()
    
    # Extract file types
    file_types = re.findall(r'\.(\w+)', prompt_lower)
    file_types = [f'.{ext}' for ext in file_types]
    logger.debug(f"Extracted file types: {file_types}")
    
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

if __name__ == "__main__":
    # Test the LLM parsing
    test_prompt = "find pdf files and txt documents about machine learning and AI"
    print("Testing LLM parsing...")
    print(f"Input: {test_prompt}")
    
    # Check if OpenAI API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"API Key present: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API Key starts with: {api_key[:10]}...")
    
    result = parse_search_prompt(test_prompt)
    print(f"Result: {result}")

    # Example usage
    prompt = "Find pdf files and txt documents with name containing 'lucy' and about machine learning and AI"
    params = parse_search_prompt(prompt)
    print(params)
