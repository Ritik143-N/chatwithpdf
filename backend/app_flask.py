from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename
import pdfplumber
from typing import List, Dict, Any

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = './uploads'

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('./static', exist_ok=True)

class SimpleDocumentStore:
    """Simple document storage without ML dependencies"""
    
    def __init__(self):
        self.documents = {}
        self.doc_counter = 0
    
    def store_document(self, filename: str, content: str) -> str:
        """Store document and return document ID"""
        self.doc_counter += 1
        doc_id = f"doc_{self.doc_counter}"
        
        # Simple text chunking
        chunks = self.chunk_text(content)
        
        self.documents[doc_id] = {
            'filename': filename,
            'content': content,
            'chunks': chunks
        }
        
        return doc_id
    
    def chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Simple text chunking"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def search_documents(self, query: str, doc_id: str = None) -> List[Dict[str, Any]]:
        """Simple keyword-based search"""
        results = []
        query_words = query.lower().split()
        
        docs_to_search = [doc_id] if doc_id and doc_id in self.documents else list(self.documents.keys())
        
        for did in docs_to_search:
            if did not in self.documents:
                continue
                
            doc = self.documents[did]
            for i, chunk in enumerate(doc['chunks']):
                chunk_lower = chunk.lower()
                score = sum(1 for word in query_words if word in chunk_lower)
                
                if score > 0:
                    results.append({
                        'doc_id': did,
                        'chunk_index': i,
                        'content': chunk,
                        'score': score,
                        'filename': doc['filename']
                    })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:5]  # Return top 5 results

# Global document store
doc_store = SimpleDocumentStore()

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from PDF file"""
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

# Routes
@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "msg": "Chat with PDF Flask API is running",
        "backend": "flask",
        "ml_available": False
    })

@app.route('/health', methods=['GET'])
def health():
    """Detailed health check"""
    return jsonify({
        "status": "healthy",
        "service": "chat-with-pdf-flask",
        "ml_available": False,
        "documents": len(doc_store.documents)
    })

@app.route('/api/v1/upload', methods=['POST'])
def upload_pdf():
    """Upload and process PDF"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract text from PDF
            text = extract_text_from_pdf(filepath)
            
            if not text.strip():
                return jsonify({"error": "No text could be extracted from the PDF"}), 400
            
            # Store document
            doc_id = doc_store.store_document(filename, text)
            
            # Clean up temporary file
            os.remove(filepath)
            
            return jsonify({
                "message": "PDF uploaded and processed successfully",
                "doc_id": doc_id,
                "filename": filename,
                "chunks_created": len(doc_store.documents[doc_id]['chunks'])
            })
            
        except Exception as e:
            # Clean up temporary file in case of error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": str(e)}), 500
    
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/api/v1/ask', methods=['POST'])
def ask_question():
    """Ask question about documents"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Query is required"}), 400
        
        query = data['query']
        doc_id = data.get('doc_id')
        
        if not doc_store.documents:
            return jsonify({"error": "No documents uploaded yet"}), 400
        
        # Search for relevant chunks
        results = doc_store.search_documents(query, doc_id)
        
        if not results:
            return jsonify({
                "answer": "I couldn't find relevant information in the uploaded documents for your question.",
                "query": query,
                "context": []
            })
        
        # Simple answer generation (without LLM)
        top_chunks = [r['content'] for r in results[:3]]
        context = "\n\n".join(top_chunks)
        
        answer = f"Based on the uploaded documents, here are the most relevant sections:\n\n{context}"
        
        return jsonify({
            "answer": answer,
            "query": query,
            "context": results[:3],
            "note": "This is a simple keyword-based search. For AI-powered responses, ML dependencies need to be installed."
        })
    
    except Exception as e:
        return jsonify({"error": f"Question processing failed: {str(e)}"}), 500

@app.route('/api/v1/search', methods=['POST'])
def search_documents():
    """Search documents"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Query is required"}), 400
        
        query = data['query']
        doc_id = data.get('doc_id')
        
        results = doc_store.search_documents(query, doc_id)
        
        return jsonify({
            "query": query,
            "results": results,
            "total_results": len(results)
        })
    
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

# Serve React static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React static files"""
    if path != "" and os.path.exists(os.path.join('./static', path)):
        return send_from_directory('./static', path)
    else:
        return send_from_directory('./static', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
