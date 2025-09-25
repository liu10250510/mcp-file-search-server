import streamlit as st
from fastmcp_file_search import search_files
from models import SearchRequest

st.title("🔍 Local File Search Agent")
st.markdown("Search for files in your local folders by name and content")

# Input fields
col1, col2 = st.columns([2, 1])

with col1:
    folder_path = st.text_input(
        "Folder Path",
        value="/Users/lucy/Documents",
        help="Enter the full path to the folder you want to search"
    )

with col2:
    max_results = st.number_input(
        "Max Results",
        min_value=1,
        max_value=50,
        value=10,
        help="Maximum number of results to return"
    )

search_prompt = st.text_area(
    "Search Prompt",
    placeholder="e.g., python files with machine learning, or .pdf documents about AI",
    help="Describe what files you're looking for. Include file types (e.g., .py, .txt) and keywords for content search"
)

# Search button
if st.button("🔍 Search Files", type="primary"):
    if search_prompt and folder_path:
        request = SearchRequest(
            folder_path=folder_path,
            search_prompt=search_prompt,
            max_results=max_results
        )
        
        with st.spinner("Searching files..."):
            results = search_files(request)
        
        if results and not results[0].get("error"):
            st.success(f"Found {len(results)} files")
            for result in results:
                with st.expander(f"📄 {result['file_path']} (Score: {result['relevance_score']})"):
                    st.write(f"**Path:** {result['relative_path']}")
                    #st.write(f"**Full Path:** {result['file_path']}")
                    st.write(f"**Matches:** {result['match_details']}")
        else:
            if results and results[0].get("error"):
                st.error(results[0]["error"])
            else:
                st.warning("No files found matching your search criteria")
    else:
        st.warning("Please enter both folder path and search prompt")

# Help section
with st.expander("📖 How to Use"):
    st.markdown("""
    1. **Folder Path**: Enter the full path to the folder you want to search
    2. **Search Prompt**: Describe what you're looking for:
       - File types: `.py`, `.txt`, `.pdf`, etc.
       - Keywords: Content you want to find in files
    3. **Max Results**: Limit the number of results returned
    
    **Examples:**
    - "python files with machine learning"
    - ".pdf documents about AI"
    - "txt files containing password"
    """)

# Footer
st.markdown("---")
st.markdown("*Built with FastMCP and Streamlit*")