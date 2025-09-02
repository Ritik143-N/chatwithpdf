import pdfplumber # type: ignore
import pytesseract  # type: ignore
from pdf2image import convert_from_bytes # type: ignore
from PIL import Image # type: ignore
from typing import List
import uuid
import io

def extract_text_from_pdf(file) -> str:
    """Extract text from uploaded PDF file using text extraction and OCR fallback"""
    # First, try to extract text directly
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error with pdfplumber extraction: {e}")
    
    # If no text was extracted or very little text, use OCR
    if len(text.strip()) < 100:  # Less than 100 characters suggests scanned PDF
        print("Text extraction yielded little content. Attempting OCR...")
        try:
            # Reset file pointer to beginning
            file.seek(0)
            file_bytes = file.read()
            
            # Convert PDF pages to images
            images = convert_from_bytes(file_bytes, dpi=300, fmt='jpeg')
            
            ocr_text = ""
            for i, image in enumerate(images):
                print(f"Processing page {i+1} with OCR...")
                # Use Tesseract OCR to extract text from image
                page_text = pytesseract.image_to_string(image, lang='eng')
                if page_text.strip():
                    ocr_text += f"Page {i+1}:\n{page_text.strip()}\n\n"
            
            if ocr_text.strip():
                text = ocr_text
                print(f"OCR extracted {len(text)} characters")
            else:
                print("OCR extraction failed to find text")
                
        except Exception as e:
            print(f"Error with OCR extraction: {e}")
            # Reset file pointer for any subsequent operations
            file.seek(0)
    
    return text.strip()

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks with better context preservation"""
    
    # First, try to split by paragraphs
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # If adding this paragraph would exceed chunk size, save current chunk and start new one
        if len(current_chunk) + len(paragraph) + 2 > chunk_size and current_chunk:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap from previous chunk
            if overlap > 0 and current_chunk:
                words = current_chunk.split()
                overlap_words = words[-overlap//4:] if len(words) > overlap//4 else words[-10:]
                current_chunk = " ".join(overlap_words) + " " + paragraph
            else:
                current_chunk = paragraph
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # If we ended up with very few chunks, fall back to word-based chunking
    if len(chunks) < 3:
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk.strip())
    
    return chunks

def generate_doc_id() -> str:
    """Generate unique document ID"""
    return str(uuid.uuid4())
