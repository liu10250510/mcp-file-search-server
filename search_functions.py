import os
import mimetypes
from typing import List, Dict
from utils import get_valid_files

def search_by_file_type(folder_path: str, file_types: List[str], max_results: int = 50) -> List[Dict[str, str]]:
    """Search files by file extension"""
    if not file_types:
        return []
    
    results = []
    
    for filepath, rel_path, filename in get_valid_files(folder_path):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in [ft.lower() for ft in file_types]:
            results.append({
                'file_path': filepath,
                'relative_path': rel_path,
                'file_name': filename,
                'relevance_score': 15,
                'match_details': f"file type: {file_ext}",
                'search_type': 'file_type'
            })
            
            if len(results) >= max_results:
                break
                
    return results

def search_by_filename(folder_path: str, keywords: List[str], existing_files: List[str] = None, max_results: int = 50) -> List[Dict[str, str]]:
    """Search files by filename keywords"""
    if not keywords:
        return []
    
    results = []
    existing_paths = set(existing_files) if existing_files else set()
    
    for filepath, rel_path, filename in get_valid_files(folder_path):
        # Skip if already found in previous search
        if filepath in existing_paths:
            continue
            
        filename_lower = filename.lower()
        matched_keywords = []
        relevance_score = 0
        
        for keyword in keywords:
            if keyword.lower() in filename_lower:
                matched_keywords.append(keyword)
                relevance_score += 10
                
        if matched_keywords:
            results.append({
                'file_path': filepath,
                'relative_path': rel_path,
                'file_name': filename,
                'relevance_score': relevance_score,
                'match_details': f"filename: {', '.join(matched_keywords)}",
                'search_type': 'filename'
            })
            
            if len(results) >= max_results:
                break
                
    return results

def search_by_content(folder_path: str, keywords: List[str], existing_files: List[str] = None, max_results: int = 50) -> List[Dict[str, str]]:
    """Search files by content keywords"""
    if not keywords:
        return []
    
    results = []
    existing_paths = set(existing_files) if existing_files else set()
    
    for filepath, rel_path, filename in get_valid_files(folder_path):
        # Skip if already found in previous searches
        if filepath in existing_paths:
            continue
            
        try:
            content = ""
            mime_type, _ = mimetypes.guess_type(filepath)
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Handle different file types based on MIME type and extension
            if mime_type == 'application/pdf' or file_ext == '.pdf':
                # Handle PDF files
                try:
                    import PyPDF2
                    with open(filepath, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages[:5]:  # Read first 5 pages
                            content += page.extract_text() or ""
                except ImportError:
                    # Fallback: try to read as text (might not work well)
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(50000)
                except Exception:
                    content = ""
                    
            elif (mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or 
                  mime_type == 'application/msword' or 
                  file_ext in ['.docx', '.doc']):
                # Handle Word documents
                try:
                    import docx
                    doc = docx.Document(filepath)
                    content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                except ImportError:
                    content = ""
                except Exception:
                    content = ""
                    
            elif mime_type == 'application/json' or file_ext == '.json':
                # Handle JSON files
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        import json
                        data = json.load(f)
                        content = json.dumps(data, ensure_ascii=False)
                except Exception:
                    # Fallback: read as text
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(50000)
                        
            elif (mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or
                  mime_type == 'application/vnd.ms-excel' or
                  file_ext in ['.xlsx', '.xls']):
                # Handle Excel files
                try:
                    import openpyxl
                    wb = openpyxl.load_workbook(filepath)
                    content_parts = []
                    for sheet in wb.worksheets[:3]:  # First 3 sheets
                        for row in sheet.iter_rows(max_row=100, values_only=True):  # First 100 rows
                            content_parts.extend([str(cell) for cell in row if cell is not None])
                    content = ' '.join(content_parts)
                except ImportError:
                    content = ""
                except Exception:
                    content = ""
                    
            elif mime_type == 'text/csv' or file_ext == '.csv':
                # Handle CSV files
                try:
                    import csv
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        reader = csv.reader(f)
                        content_parts = []
                        for i, row in enumerate(reader):
                            if i > 1000:  # Limit to first 1000 rows
                                break
                            content_parts.extend(row)
                        content = ' '.join(content_parts)
                except Exception:
                    content = ""
                    
            elif (mime_type and mime_type.startswith('text/') or 
                  file_ext in ['.py', '.js', '.html', '.css', '.xml', '.yaml', '.yml', '.md', '.rst', '.txt', '.log']):
                # Handle text files and code files
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(50000)  # Read first 50KB
                except Exception:
                    content = ""
                    
            # If no specific handler found, try to read as text if MIME type suggests it's readable
            elif mime_type and any(readable_type in mime_type for readable_type in ['text', 'xml', 'json', 'javascript', 'css']):
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(50000)
                except Exception:
                    content = ""

            if content:
                content = content.lower()
                content_matches = []
                relevance_score = 0
                
                for keyword in keywords:
                    count = content.count(keyword.lower())
                    if count > 0:
                        relevance_score += count * 2
                        content_matches.append(f"{keyword}({count})")
                        
                if content_matches:
                    results.append({
                        'file_path': filepath,
                        'relative_path': rel_path,
                        'file_name': filename,
                        'relevance_score': relevance_score,
                        'match_details': f"content: {', '.join(content_matches)}",
                        'search_type': 'content'
                    })
                    
        except (PermissionError, UnicodeDecodeError, OSError):
            pass  # Skip files we can't read
            
        if len(results) >= max_results:
            break
            
    return results

if __name__ == "__main__":
    # Example usage
    folder = "/Users/lucy/Documents"
    file_types = [".pdf", ".txt"]
    filename_keywords = ["lucy", "resume"]
    content_keywords = ["machine learning", "AI"]
    
    print("Searching by file type...")
    type_results = search_by_file_type(folder, file_types, max_results=5)
    for res in type_results:
        print(res)
        
    print("\nSearching by filename...")
    filename_results = search_by_filename(folder, filename_keywords, existing_files=[r['file_path'] for r in type_results], max_results=5)
    for res in filename_results:
        print(res)
        
    print("\nSearching by content...")
    content_results = search_by_content(folder, content_keywords, existing_files=[r['file_path'] for r in type_results + filename_results], max_results=5)
    for res in content_results:
        print(res)