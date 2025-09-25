#!/usr/bin/env python3
"""
FastMCP File Search Server

A simplified MCP server using FastMCP for intelligent file search.
"""

from mcp.server.fastmcp import FastMCP
from fastmcp_file_search import search_files
from models import SearchRequest

# Create FastMCP app
mcp = FastMCP("File Search Server")

@mcp.tool()
def search_files_tool(
    folder_path: str,
    search_prompt: str,
    max_results: int = 10
) -> str:
    """
    Search for files in a local directory by file type, filename, and content.
    
    Args:
        folder_path: Absolute path to the folder to search in
        search_prompt: Natural language description of files to search for
        max_results: Maximum number of results to return (1-100)
    
    Returns:
        Formatted search results with file paths, types, and relevance
    """
    try:
        # Ensure folder_path is absolute
        import os
        if not os.path.isabs(folder_path):
            folder_path = os.path.abspath(folder_path)
        
        # Normalize the path to handle any relative components
        folder_path = os.path.normpath(folder_path)
        

        
        # Create search request
        request = SearchRequest(
            folder_path=folder_path,
            search_prompt=search_prompt,
            max_results=max_results
        )
        
        # Perform search
        results = search_files(request)
        
        if not results:
            # Check if folder exists
            import os
            if not os.path.exists(folder_path):
                return f"❌ Error: Folder '{folder_path}' does not exist"
            elif not os.path.isdir(folder_path):
                return f"❌ Error: '{folder_path}' is not a directory"
            else:
                # If no matches, show all files as fallback
                try:
                    all_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                    
                    if all_files:
                        # Create fallback results
                        from models import SearchResult
                        fallback_results = []
                        for file in all_files[:max_results]:
                            file_path = os.path.join(folder_path, file)
                            relative_path = os.path.relpath(file_path, folder_path)
                            result = SearchResult(
                                file_path=file_path,
                                relative_path=relative_path,
                                file_name=file,
                                relevance_score=5,
                                match_details="Fallback - showing all files in directory", 
                                search_type="fallback"
                            )
                            fallback_results.append(result)
                            
                        # Format fallback results  
                        formatted_results = []
                        for i, result in enumerate(fallback_results, 1):
                            formatted_results.append(
                                f"{i}. **{result.relative_path}**\n"
                                f"   - Full path: {result.file_path}\n"
                                f"   - Relevance: {result.relevance_score}/10\n"
                                f"   - Match: {result.match_details}\n"
                            )
                        
                        return f"Found {len(fallback_results)} files:\n\n" + "\n".join(formatted_results)
                    else:
                        return f"📁 Folder is empty"
                        
                except PermissionError:
                    return f"❌ Error: Permission denied accessing '{folder_path}'"
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(
                f"{i}. **{result.relative_path}**\n"
                f"   - Full path: {result.file_path}\n"
                f"   - Relevance: {result.relevance_score}/10\n"
                f"   - Match: {result.match_details}\n"
            )
        
        return f"Found {len(results)} files matching '{search_prompt}':\n\n" + "\n".join(formatted_results)
        
    except Exception as e:
        return f"Error performing search: {str(e)}"

if __name__ == "__main__":
    # Run the server
    mcp.run()
