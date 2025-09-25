# FastMCP File Search Server - Usage Guide

## 🎉 Success! Your FastMCP Server is Working

Your FastMCP File Search Server is now fully functional and ready to use. The server uses FastMCP for simplified, clean code with the same powerful features.

## Testing Methods

### 1. FastMCP Test Client (✅ Working)
```bash
python test_fastmcp.py
```
This tests the FastMCP server with a simple client.

### 2. Streamlit Web Interface
```bash
streamlit run file_search_ui.py
```
Access the web interface at http://localhost:8501

### 3. Direct Python Function
```python
from fastmcp_file_search import search_files
from models import SearchRequest

request = SearchRequest(
    folder_path="/path/to/search",
    search_prompt="Python files with machine learning",
    max_results=10
)
results = search_files(request)
```

## Integration with Claude Desktop

To use this server with Claude Desktop:

1. **Find your Claude Desktop config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%/Claude/claude_desktop_config.json`

2. **Add this configuration:**
```json
{
  "mcpServers": {
    "file-search": {
      "command": "/Users/lucy/projects/MCP/.venv/bin/python",
      "args": ["/Users/lucy/projects/MCP/fastmcp_server.py"],
      "env": {
        "PYTHONPATH": "/Users/lucy/projects/MCP"
      }
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Test it by asking Claude:**
   - "Search for Python files in my project that contain machine learning code"
   - "Find all PDF documents about neural networks"
   - "Look for configuration files in my codebase"

## Server Features

### 🔍 Smart Search Capabilities
- **File Type Search**: Find files by extension (`.py`, `.pdf`, `.docx`, etc.)
- **Filename Search**: Search by filename patterns
- **Content Search**: Search inside file contents (text, PDF, Word, Excel)
- **Natural Language**: Use plain English to describe what you're looking for

### 🧠 LLM-Powered Query Parsing
- Automatically parses natural language queries
- Supports AND/OR logic ("Python files AND machine learning")
- Fallback parsing if LLM is unavailable

### 📁 Supported File Types
- **Text**: `.py`, `.js`, `.html`, `.css`, `.md`, `.txt`, `.json`, `.xml`, `.csv`
- **Documents**: `.pdf`, `.docx`, `.xlsx`
- **Code**: All common programming languages

### ⚡ Fast and Efficient
- Parallel file processing
- MIME type detection
- Configurable result limits

## Example Queries

```python
# Natural language queries that work:
"Find Python files with machine learning or AI"
"PDF documents about neural networks"  
"Configuration files in JSON format"
"Excel spreadsheets with financial data"
"Documentation files containing API information"
```

## Troubleshooting

If you encounter issues:

1. **Check imports**: Run `python -c "import fastmcp_server"`
2. **Test FastMCP server**: Run `python test_fastmcp.py`
3. **Check dependencies**: Run `uv pip list` to see installed packages
4. **Test web interface**: Run `streamlit run file_search_ui.py`

## Next Steps

Your MCP server is ready for production use! You can:

1. **Deploy to Claude Desktop** for daily use
2. **Integrate with other MCP clients** 
3. **Extend functionality** by adding more search types
4. **Deploy as a service** for team use

Congratulations on building a fully functional MCP server! 🚀
