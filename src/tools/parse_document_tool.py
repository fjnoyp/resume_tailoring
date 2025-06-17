import pdfplumber
import docx2txt
import olefile
import logging
import asyncio
from typing import Optional
import io

async def parse_document(file_bytes: bytes, file_extension: str) -> Optional[str]:
    """
    Extracts text from a document file (PDF, DOCX, or DOC) provided as bytes.
    
    Args:
        file_bytes: The document file content as bytes
        file_extension: The file extension (pdf, docx, or doc) without the dot
    
    Returns:
        The extracted text as a single string if successful, None otherwise.
    """
    loop = asyncio.get_event_loop()
    file_extension = file_extension.lower().lstrip('.')
    
    try:
        if file_extension == 'pdf':
            def extract_pdf():
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    return "\n".join(page.extract_text() or "" for page in pdf.pages)
            text = await loop.run_in_executor(None, extract_pdf)
            
        elif file_extension == 'docx':
            def extract_docx():
                return docx2txt.process(io.BytesIO(file_bytes))
            text = await loop.run_in_executor(None, extract_docx)
            
        elif file_extension == 'doc':
            def extract_doc():
                try:
                    # Create a BytesIO object for the file
                    file_io = io.BytesIO(file_bytes)
                    
                    # Try to open as OLE file
                    if olefile.isOleFile(file_io):
                        ole = olefile.OleFileIO(file_io)
                        # Get the main content stream
                        if ole.exists('WordDocument'):
                            with ole.openstream('WordDocument') as stream:
                                content = stream.read()
                                # Try to decode as text, ignoring errors
                                return content.decode('utf-8', errors='ignore')
                    return ""
                except Exception as e:
                    logging.warning(f"Failed to extract .doc using olefile: {e}")
                    # Fallback to simple text extraction
                    try:
                        return file_bytes.decode('utf-8', errors='ignore')
                    except Exception as e:
                        logging.error(f"Failed to extract .doc as text: {e}")
                        return ""
            text = await loop.run_in_executor(None, extract_doc)
            
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")
        
        logging.debug(f"Extracted text from {file_extension.upper()} file (length: {len(text)})")
        return text
        
    except Exception as e:
        logging.error(f"Error parsing {file_extension.upper()} file: {e}")
        return None
