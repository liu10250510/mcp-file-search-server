from pydantic import BaseModel
from typing import List, Dict

class SearchRequest(BaseModel):
    folder_path: str
    search_prompt: str
    max_results: int = 10

class SearchParams(BaseModel):
    file_types: List[str] = []
    filename_keywords: List[str] = []
    content_keywords: List[str] = []
    search_sequence: List[str] = ["file_type", "filename", "content"]
    search_logic: str = "AND"  # "AND" or "OR" - defines if all criteria must match or any

class SearchResult(BaseModel):
    file_path: str
    relative_path: str
    file_name: str
    relevance_score: int
    match_details: str
    search_type: str = "combined"
