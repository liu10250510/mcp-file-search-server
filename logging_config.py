import logging
import os
import glob
from datetime import datetime, timedelta

def cleanup_old_logs(log_dir):
    """Remove log files older than 1 day"""
    try:
        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        
        # Find all log files matching the pattern
        log_pattern = os.path.join(log_dir, "mcp_server_*.log")
        log_files = glob.glob(log_pattern)
        
        for log_file in log_files:
            # Extract date from filename
            filename = os.path.basename(log_file)
            if filename.startswith("mcp_server_") and filename.endswith(".log"):
                date_str = filename[11:-4]  # Extract YYYYMMDD part
                try:
                    file_date = datetime.strptime(date_str, '%Y%m%d')
                    # Remove if older than yesterday
                    if file_date < yesterday:
                        os.remove(log_file)
                        print(f"Removed old log file: {log_file}")
                except ValueError:
                    # Skip files that don't match the expected date format
                    continue
    except Exception as e:
        # Don't let log cleanup break the application
        print(f"Warning: Could not cleanup old logs: {e}")

def setup_logging(log_level=logging.INFO):
    """Setup logging configuration for the MCP server"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Clean up old log files (keep only last day)
    cleanup_old_logs(log_dir)
    
    # Create log filename with timestamp
    log_filename = f"mcp_server_{datetime.now().strftime('%Y%m%d')}.log"
    log_path = os.path.join(log_dir, log_filename)
    
    # Configure logging - only file handler, no console output
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler - saves to log file only
            logging.FileHandler(log_path, encoding='utf-8')
        ]
    )
    
    # Create logger for the MCP server
    logger = logging.getLogger('FastMCP_FileSearch')
    
    logger.info("="*60)
    logger.info("MCP File Search Server Starting")
    logger.info(f"Log file: {log_path}")
    logger.info("="*60)
    
    return logger
