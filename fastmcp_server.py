#!/usr/bin/env python3
"""
FastMCP File Search Server

A simplified MCP server using FastMCP for intelligent file search.
"""

import logging
from mcp.server.fastmcp import FastMCP
from fastmcp_file_search import search_files
from models import SearchRequest
from logging_config import setup_logging

# Setup logging
logger = setup_logging()

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
    logger.info("🔍 New search request received")
    logger.info(f"   Folder: {folder_path}")
    logger.info(f"   Query: {search_prompt}")
    logger.info(f"   Max Results: {max_results}")
    
    try:
        # Ensure folder_path is absolute
        import os
        if not os.path.isabs(folder_path):
            folder_path = os.path.abspath(folder_path)
            logger.info(f"   Converted to absolute path: {folder_path}")
        
        # Normalize the path to handle any relative components
        folder_path = os.path.normpath(folder_path)
        logger.debug(f"   Normalized path: {folder_path}")
        

        
        # Create search request
        request = SearchRequest(
            folder_path=folder_path,
            search_prompt=search_prompt,
            max_results=max_results
        )
        logger.debug(f"   Created search request: {request}")
        
        # Perform search
        logger.info("   Starting file search...")
        results = search_files(request)
        logger.info(f"   Search completed: {len(results)} results found")
        
        if not results:
            logger.warning("   No search results found, checking folder status...")
            # Check if folder exists
            import os
            if not os.path.exists(folder_path):
                logger.error(f"   Folder does not exist: {folder_path}")
                return f"❌ Error: Folder '{folder_path}' does not exist"
            elif not os.path.isdir(folder_path):
                logger.error(f"   Path is not a directory: {folder_path}")
                return f"❌ Error: '{folder_path}' is not a directory"
            else:
                # If no matches, show all files as fallback
                logger.info("   Attempting fallback: showing all files in directory")
                try:
                    all_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                    logger.info(f"   Found {len(all_files)} files for fallback")
                    
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
                        
                        logger.info(f"   Returning {len(fallback_results)} fallback results")
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
                        logger.info("   Directory is empty")
                        return f"📁 Folder is empty"
                        
                except PermissionError:
                    logger.error(f"   Permission denied accessing folder: {folder_path}")
                    return f"❌ Error: Permission denied accessing '{folder_path}'"
        
        # Format results
        logger.info(f"   Formatting {len(results)} search results for response")
        formatted_results = []
        for i, result in enumerate(results, 1):
            logger.debug(f"   Result {i}: {result.relative_path} (score: {result.relevance_score})")
            formatted_results.append(
                f"{i}. **{result.relative_path}**\n"
                f"   - Full path: {result.file_path}\n"
                f"   - Relevance: {result.relevance_score}/10\n"
                f"   - Match: {result.match_details}\n"
            )
        
        logger.info(f"✅ Search completed successfully - returning {len(results)} results")
        return f"Found {len(results)} files matching '{search_prompt}':\n\n" + "\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"❌ Search failed with error: {str(e)}", exc_info=True)
        return f"Error performing search: {str(e)}"

if __name__ == "__main__":
    # Run the server
    mcp.run()
