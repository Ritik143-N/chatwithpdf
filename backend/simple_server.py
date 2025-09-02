import http.server
import socketserver
import json
import os
import urllib.parse
import pdfplumber
from datetime import datetime

class PDFHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.documents = {}  # In-memory document storage
        super().__init__(*args, directory='static', **kwargs)
    
    def do_POST(self):
        if self.path == '/api/upload':
            self.handle_upload()
        elif self.path == '/api/chat':
            self.handle_chat()
        else:
            self.send_error(404)
    
    def do_GET(self):
        if self.path.startswith('/api/'):
            self.send_error(404)
        else:
            super().do_GET()
    
    def handle_upload(self):
        try:
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' not in content_type:
                self.send_error(400)
                return
            
            # Simple file upload handler
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Extract PDF content (simplified)
            boundary = content_type.split('boundary=')[1].encode()
            parts = post_data.split(boundary)
            
            for part in parts:
                if b'Content-Type: application/pdf' in part:
                    # Find PDF content
                    pdf_start = part.find(b'\r\n\r\n') + 4
                    pdf_data = part[pdf_start:]
                    
                    # Save and process PDF
                    filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    filepath = f"uploads/{filename}"
                    
                    os.makedirs('uploads', exist_ok=True)
                    with open(filepath, 'wb') as f:
                        f.write(pdf_data)
                    
                    # Extract text
                    text_content = self.extract_pdf_text(filepath)
                    self.documents[filename] = {
                        'text': text_content,
                        'filename': filename,
                        'upload_time': datetime.now().isoformat()
                    }
                    
                    response = {
                        'status': 'success',
                        'filename': filename,
                        'message': 'PDF uploaded and processed successfully'
                    }
                    
                    self.send_json_response(response)
                    return
            
            self.send_error(400, "No PDF found in upload")
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_chat(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            query = data.get('message', '').lower()
            
            # Simple search across all documents
            results = []
            for doc_id, doc in self.documents.items():
                if query in doc['text'].lower():
                    # Find sentences containing the query
                    sentences = doc['text'].split('.')
                    relevant_sentences = [s.strip() for s in sentences if query in s.lower()]
                    
                    if relevant_sentences:
                        results.extend(relevant_sentences[:3])  # Top 3 per document
            
            if results:
                response_text = f"Based on the uploaded documents, here's what I found:\n\n"
                response_text += "\n".join(f"• {result}" for result in results[:5])
            else:
                response_text = "I couldn't find relevant information in the uploaded documents for your query."
            
            response = {
                'response': response_text,
                'status': 'success'
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def extract_pdf_text(self, filepath):
        try:
            with pdfplumber.open(filepath) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data)
        self.wfile.write(response_json.encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    PORT = int(os.environ.get('PORT', 10000))
    
    with socketserver.TCPServer(("", PORT), PDFHandler) as httpd:
        print(f"Server running on port {PORT}")
        httpd.serve_forever()
