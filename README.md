# MCP File Search Server

A Model Context Protocol (MCP) server that provides intelligent file search capabilities for local directories. This server can search by file type, filename patterns, and file content using natural language queries.

## Features

- 🔍 **Natural Language Search**: Use plain English to describe what files you're looking for
- 📁 **Multi-Type Search**: Search by file extension, filename keywords, and file content
- 🤖 **AI-Powered Parsing**: Uses OpenAI GPT to intelligently parse search requests
- 📄 **Multiple File Formats**: Supports PDF, Word docs, Excel, JSON, CSV, and text files
- ⚡ **Fast Search**: Efficient file system traversal with smart filtering
- 🎯 **Relevance Scoring**: Results ranked by relevance to your query

## Installation

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run the setup script:**
   ```bash
   python setup_mcp_server.py
   ```

## Usage

### As MCP Server

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "file-search": {
      "command": "python",
      "args": ["/path/to/mcp_file_search_server.py"],
      "env": {}
    }
  }
}
```

### Available Tools

#### `search_files`

Search for files in a local directory using natural language.

**Parameters:**
- `folder_path` (required): Absolute path to search directory
- `search_prompt` (required): Natural language search description
- `max_results` (optional): Maximum results to return (default: 10)

**Examples:**

```json
{
  "folder_path": "/Users/john/Documents",
  "search_prompt": "pdf files about machine learning",
  "max_results": 5
}
```

```json
{
  "folder_path": "/Users/john/Projects",
  "search_prompt": "python scripts with neural network code",
  "max_results": 10
}
```

### Standalone Usage

You can also use the search functionality directly:

```python
from fastmcp_file_search import search_files
from models import SearchRequest

request = SearchRequest(
    folder_path="/path/to/search",
    search_prompt="find all PDF files about AI",
    max_results=10
)

results = search_files(request)
for result in results:
    print(f"Found: {result['file_name']}")
```

### Web UI

Run the Streamlit web interface:

```bash
streamlit run file_search_ui.py
```

## Supported File Types

- **Documents**: PDF, Word (.docx, .doc), Excel (.xlsx, .xls)
- **Data**: JSON, CSV
- **Code**: Python (.py), JavaScript (.js), HTML, CSS, XML
- **Text**: Plain text, Markdown (.md), YAML (.yml), etc.

## Search Examples

- `"pdf files about machine learning"`
- `"python scripts with neural network code"`
- `"excel spreadsheets containing budget data"`
- `"json configuration files"`
- `"word documents from last month"`
- `"text files with API documentation"`

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_ORG_ID`: Your OpenAI organization ID (optional)

### Search Behavior

- Uses AND logic by default (files must match all criteria)
- Searches file extensions, filenames, and content
- Excludes system directories (.git, .venv, __pycache__, etc.)
- Limits content search to first 50KB of each file

## Architecture

```
mcp_file_search_server.py  # MCP server implementation
├── fastmcp_file_search.py # Main search orchestration
├── models.py              # Data models
├── utils.py               # LLM parsing and utilities
├── search_functions.py    # Individual search functions
└── file_search_ui.py      # Web interface
```

## Troubleshooting

1. **"Import mcp could not be resolved"**
   - Install the MCP package: `pip install mcp`

2. **"LLM parsing failed"**
   - Check your OpenAI API key in `.env`
   - Verify internet connection

3. **"No files found"**
   - Check folder path exists and is readable
   - Try broader search terms
   - Verify file types exist in target directory

## Project Structure

```
├── mcp_file_search_server.py    # Main MCP server implementation
├── models.py                    # Pydantic data models
├── utils.py                     # LLM integration and utilities
├── search_functions.py          # Individual search operations
├── fastmcp_file_search.py      # Main search orchestration
├── file_search_ui.py           # Streamlit web interface
├── test_official_client.py     # Official MCP client test
├── test_mcp_client.py          # JSON-RPC test client
├── mcp_config.json             # MCP server configuration
├── pyproject.toml              # Project dependencies
├── README.md                   # This file
└── USAGE_GUIDE.md              # Detailed usage instructions
```

## Development

To extend the server:

1. Add new search functions in `search_functions.py`
2. Update the search orchestration in `fastmcp_file_search.py`
3. Add new tools to `mcp_file_search_server.py`

## License

MIT License - see LICENSE file for details.
