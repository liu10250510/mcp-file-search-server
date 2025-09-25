from typing import List, Dict
from models import SearchRequest, SearchResult
from utils import parse_search_prompt, validate_folder_path
from search_functions import search_by_file_type, search_by_filename, search_by_content

def search_files(request: SearchRequest) -> List[SearchResult]:
    """
    Main search function that orchestrates different search types
    """
    # Validate folder path
    validation_error = validate_folder_path(request.folder_path)
    if validation_error:
        return validation_error

    # Parse search prompt
    search_params = parse_search_prompt(request.search_prompt)
    
    all_results = []
    
    # AND logic: Only return files that match ALL specified criteria
    candidate_files = None  # Start with all possible files
    
    for search_type in search_params.search_sequence:
        if search_type == "file_type" and search_params.file_types:
            type_results = search_by_file_type(request.folder_path, search_params.file_types, request.max_results * 10)
            if candidate_files is None:
                candidate_files = {r['file_path']: r for r in type_results}
            else:
                # Keep only files that appear in both sets
                type_files = {r['file_path']: r for r in type_results}
                candidate_files = {path: result for path, result in candidate_files.items() if path in type_files}
            
        elif search_type == "filename" and search_params.filename_keywords:
            filename_results = search_by_filename(request.folder_path, search_params.filename_keywords, [], request.max_results * 10)
            filename_files = {r['file_path']: r for r in filename_results}
            
            if candidate_files is None:
                candidate_files = filename_files
            else:
                # Keep only files that appear in both sets
                candidate_files = {path: result for path, result in candidate_files.items() if path in filename_files}
            
        elif search_type == "content" and search_params.content_keywords:
            content_results = search_by_content(request.folder_path, search_params.content_keywords, [], request.max_results * 10)
            content_files = {r['file_path']: r for r in content_results}
            
            if candidate_files is None:
                candidate_files = content_files
            else:
                # Keep only files that appear in both sets
                candidate_files = {path: result for path, result in candidate_files.items() if path in content_files}
    
    # Convert back to list
    dict_results = list(candidate_files.values()) if candidate_files else []
                

    # Sort by relevance score and search type priority
    type_priority = {"file_type": 3, "filename": 2, "content": 1}
    dict_results.sort(key=lambda x: (type_priority.get(x.get('search_type', 'content'), 0), x['relevance_score']), reverse=True)

    # Convert dictionaries to SearchResult objects
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

    return search_results


