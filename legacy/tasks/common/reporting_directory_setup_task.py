import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

async def ensure_reporting_directory_exists() -> str:
    """
    Ensures that the reporting output directory exists.
    
    Returns:
        str: Path to the reporting directory
    """
    
    # Create reports directory in the project root with 777 permissions
    reports_dir = Path("reports")
    reports_dir.mkdir(mode=0o777, exist_ok=True)
    
    # Set permissions explicitly in case umask affects mkdir
    os.chmod(reports_dir, 0o777)
    
    logger.info(f"Reporting directory ensured at: {reports_dir.absolute()}")
    
    return str(reports_dir.absolute())