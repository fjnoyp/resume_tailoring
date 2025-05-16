import pdfplumber
import logging
import asyncio
from typing import Optional
import io

async def parse_pdf(pdf_bytes: bytes) -> Optional[str]:
    """
    Extracts all text from a PDF file provided as bytes using pdfplumber. Use this tool to convert a PDF's content into a single plain text string for further processing or analysis.
    
    Args:
        pdf_bytes: The PDF file content as bytes.
    
    Returns:
        The extracted text as a single string if successful, None otherwise.
    """
    loop = asyncio.get_event_loop()
    try:
        def extract_text():
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        text = await loop.run_in_executor(None, extract_text)
        logging.debug(f"Extracted text from PDF bytes (length: {len(text)})")
        return text
    except Exception as e:
        logging.error(f"Error parsing PDF bytes: {e}")
        return None
