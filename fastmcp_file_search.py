import logging
from typing import List, Dict
from models import SearchRequest, SearchResult
from utils import parse_search_prompt, validate_folder_path
from search_functions import search_by_file_type, search_by_filename, search_by_content

# Get logger
logger = logging.getLogger('FastMCP_FileSearch')

def search_files(request: SearchRequest) -> List[SearchResult]:
    """
    Main search function that orchestrates different search types
    """
    logger.debug(f"search_files() called with: {request}")
    
    # Validate folder path
    logger.debug("Validating folder path...")
    validation_error = validate_folder_path(request.folder_path)
    if validation_error:
        logger.error(f"Folder validation failed: {validation_error}")
        return validation_error

    # Parse search prompt
    logger.debug(f"Parsing search prompt: '{request.search_prompt}'")
    search_params = parse_search_prompt(request.search_prompt)
    logger.info(f"Parsed search parameters: {search_params}")
    
    all_results = []
    
    # AND logic: Only return files that match ALL specified criteria
    candidate_files = None  # Start with all possible files
    logger.info(f"Starting search with sequence: {search_params.search_sequence}")
    
    for search_type in search_params.search_sequence:
        if search_type == "file_type" and search_params.file_types:
            logger.debug(f"Searching by file types: {search_params.file_types}")
            type_results = search_by_file_type(request.folder_path, search_params.file_types, request.max_results * 10)
            logger.debug(f"File type search returned {len(type_results)} results")
            
            if candidate_files is None:
                candidate_files = {r['file_path']: r for r in type_results}
            else:
                # Keep only files that appear in both sets
                type_files = {r['file_path']: r for r in type_results}
                candidate_files = {path: result for path, result in candidate_files.items() if path in type_files}
                logger.debug(f"After file type filtering: {len(candidate_files)} candidates remain")
            
        elif search_type == "filename" and search_params.filename_keywords:
            logger.debug(f"Searching by filename keywords: {search_params.filename_keywords}")
            filename_results = search_by_filename(request.folder_path, search_params.filename_keywords, [], request.max_results * 10)
            logger.debug(f"Filename search returned {len(filename_results)} results")
            
            filename_files = {r['file_path']: r for r in filename_results}
            
            if candidate_files is None:
                candidate_files = filename_files
            else:
                # Keep only files that appear in both sets
                candidate_files = {path: result for path, result in candidate_files.items() if path in filename_files}
                logger.debug(f"After filename filtering: {len(candidate_files)} candidates remain")
            
        elif search_type == "content" and search_params.content_keywords:
            logger.debug(f"Searching by content keywords: {search_params.content_keywords}")
            content_results = search_by_content(request.folder_path, search_params.content_keywords, [], request.max_results * 10)
            logger.debug(f"Content search returned {len(content_results)} results")
            
            content_files = {r['file_path']: r for r in content_results}
            
            if candidate_files is None:
                candidate_files = content_files
            else:
                # Keep only files that appear in both sets
                candidate_files = {path: result for path, result in candidate_files.items() if path in content_files}
                logger.debug(f"After content filtering: {len(candidate_files)} candidates remain")
    
    # Convert back to list
    dict_results = list(candidate_files.values()) if candidate_files else []
    logger.info(f"Total search results before sorting: {len(dict_results)}")
                

    # Sort by relevance score and search type priority
    logger.debug("Sorting results by relevance and type priority")
    type_priority = {"file_type": 3, "filename": 2, "content": 1}
    dict_results.sort(key=lambda x: (type_priority.get(x.get('search_type', 'content'), 0), x['relevance_score']), reverse=True)

    # Convert dictionaries to SearchResult objects
    logger.debug(f"Converting {len(dict_results)} results to SearchResult objects")
    search_results = []
    for result_dict in dict_results[:request.max_results]:
        file_path = result_dict['file_path']
        # Calculate relative path
        relative_path = file_path.replace(request.folder_path, '').lstrip('/')
        
        search_result = SearchResult(
            file_path=file_path,
            relative_path=relative_path,
            file_name=result_dict.get('file_name', ''),
            relevance_score=int(result_dict.get('relevance_score', 0)),
            match_details=result_dict.get('match_details', 'Found matching criteria'),
            search_type=result_dict.get('search_type', 'combined')
        )
        search_results.append(search_result)

    logger.info(f"Returning {len(search_results)} final search results")
    return search_results

if __name__ == "__main__":
    # Example usage
    request = SearchRequest(
        folder_path="/Users/lucy/Documents",
        search_prompt="pdf files with machine learning",
        max_results=5
    )
    results = search_files(request)
    for result in results:
        print(f"File: {result['file_name']}")
        print(f"Path: {result['file_path']}")
        print(f"Search Type: {result.get('search_type', 'N/A')}")
        print(f"Relevance: {result['relevance_score']}")
        print(f"Matches: {result.get('match_details', 'N/A')}\n")
