# Chat with PDF

A full-stack application that allows users to upload PDF documents and chat with their content using AI.

## 📁 Project Structure

```
chatwithpdf/
├── backend/                 # FastAPI backend service
│   ├── app/                # Application code
│   │   ├── models/         # Data models and schemas
│   │   ├── routes/         # API routes
│   │   ├── services/       # Business logic services
│   │   └── main.py         # Application entry point
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend containerization
├── frontend/               # React frontend application
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   └── services/      # API services
│   ├── public/           # Static assets
│   ├── package.json      # Node.js dependencies
│   └── Dockerfile        # Frontend containerization
├── docs/                  # Documentation
│   └── RENDER_DEPLOYMENT.md
├── scripts/              # Setup and utility scripts
│   ├── setup.sh         # Main setup script
│   ├── setup_ollama.sh  # Ollama setup script
│   ├── status.sh        # Status check script
│   └── test_*.py        # Test files
├── docker-compose.yml    # Local development setup
├── render.yaml          # Render deployment configuration
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ritik143-N/chatwithpdf.git
   cd chatwithpdf
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Using Docker Compose
```bash
docker-compose up --build
```

## 🔧 Configuration

### Environment Variables

**Backend:**
- `PORT`: Server port (default: 8000)

**Frontend:**
- `REACT_APP_BACKEND_URL`: Backend API URL

## 📚 API Documentation

Once the backend is running, visit:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/

## 🚀 Deployment

### Render (Recommended)
See [deployment guide](docs/RENDER_DEPLOYMENT.md) for detailed instructions.

### Manual Deployment
1. Build and push Docker images
2. Deploy to your preferred cloud provider
3. Set environment variables
4. Configure persistent storage for ChromaDB

## 🛠️ Development

### Backend Structure
- **FastAPI** framework for REST API
- **ChromaDB** for vector storage
- **Sentence Transformers** for embeddings
- **PDFPlumber** for PDF text extraction

### Frontend Structure
- **React** with functional components
- **Tailwind CSS** for styling
- **Axios** for API communication

## 📝 Scripts

- `scripts/setup.sh` - Complete environment setup
- `scripts/setup_ollama.sh` - Ollama installation and setup
- `scripts/status.sh` - Check service status
- `scripts/test_*.py` - Test scripts

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/api/v1/upload` | Upload and process PDF |
| POST | `/api/v1/ask` | Ask question about documents |
| POST | `/api/v1/search` | Search document chunks |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues or have questions, please:
1. Check existing issues
2. Create a new issue with detailed information
3. Provide logs and error messages

## 🌟 Features

- **PDF Upload & Processing**: Upload PDF documents and extract text content
- **Intelligent Chunking**: Split documents into meaningful chunks for better retrieval
- **Semantic Search**: Use embeddings to find relevant document sections
- **AI-Powered Chat**: Ask questions and get answers based on document content
- **Modern UI**: Clean, responsive React interface with Tailwind CSS
- **Real-time Chat**: Interactive chat interface with loading states

## 🏗️ Architecture

```
Frontend (React + Tailwind)
    ↓
FastAPI Backend
    ├── PDF Processing (pdfplumber)
    ├── Text Chunking
    ├── Embeddings (Sentence Transformers)
    ├── Vector Database (ChromaDB)
    └── LLM Integration (HuggingFace/Ollama)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone and setup the project:**
   ```bash
   git clone <your-repo-url>
   cd chatwithpdf
   ./setup.sh
   ```

2. **Start the backend server:**
   ```bash
   cd backend
   source venv/bin/activate
   python -m uvicorn app.main:app --reload --port 8000
   ```

3. **Start the frontend (in a new terminal):**
   ```bash
   cd frontend
   npm start
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🔧 Configuration

### LLM Setup

You have three options for the LLM backend:

#### Option 1: No Setup (Basic Functionality)
The app will work without any LLM setup, providing document search with context.

#### Option 2: HuggingFace API (Recommended for beginners)
1. Get a free token from [HuggingFace](https://huggingface.co/settings/tokens)
2. Set the environment variable:
   ```bash
   export HUGGING_FACE_TOKEN=your_token_here
   ```

#### Option 3: Local Ollama (Better privacy and control)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve

# Download a model (in another terminal)
ollama run llama3

# Set environment variable
export USE_LOCAL_LLM=true
```

**Note:** The system uses `google/flan-t5-base` by default as it's reliable and available on HuggingFace Inference API. If you encounter model errors, the system will provide fallback responses with the relevant document context.

## 📁 Project Structure

```
chatwithpdf/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Main FastAPI application
│   │   ├── models/            # Pydantic models
│   │   │   └── schemas.py
│   │   ├── routes/            # API routes
│   │   │   └── api.py
│   │   └── services/          # Business logic
│   │       ├── pdf_service.py
│   │       ├── embedding_service.py
│   │       └── llm_service.py
│   ├── requirements.txt       # Python dependencies
│   └── venv/                  # Virtual environment
├── frontend/                  # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── FileUpload.js
│   │   │   └── ChatBox.js
│   │   ├── services/          # API services
│   │   │   └── api.js
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
├── setup.sh                  # Setup script
└── README.md
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/api/v1/upload` | Upload and process PDF |
| POST | `/api/v1/ask` | Ask question about documents |
| POST | `/api/v1/search` | Search document chunks |
| GET | `/api/v1/health` | API health status |

## 📝 Usage

1. **Upload a PDF**: Drag and drop or select a PDF file to upload
2. **Wait for Processing**: The system will extract text and create embeddings
3. **Start Chatting**: Ask questions about the document content
4. **Get Answers**: Receive AI-generated answers based on the document

## 🛠️ Development

### Backend Development

```bash
cd backend
source venv/bin/activate

# Install development dependencies
pip install pytest black flake8

# Run tests
pytest

# Format code
black app/

# Start with auto-reload
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## 🧪 Testing

### Test the API

```bash
# Upload a PDF
curl -X POST "http://localhost:8000/api/v1/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/your/document.pdf"

# Ask a question
curl -X POST "http://localhost:8000/api/v1/ask" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is this document about?"}'
```

## 🚀 Deployment

### Backend (Railway/Heroku)

1. Create `Procfile`:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. Update requirements.txt with production dependencies

3. Set environment variables in your hosting platform

### Frontend (Vercel/Netlify)

1. Update API base URL in `src/services/api.js`
2. Build and deploy: `npm run build`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **Import errors in backend**: Make sure virtual environment is activated
2. **CORS errors**: Check that backend is running on port 8000
3. **Embedding model download**: First run might be slow due to model download
4. **PDF processing fails**: Ensure uploaded file is a valid PDF

### Getting Help

1. Check the logs in both backend and frontend terminals
2. Verify all dependencies are installed correctly
3. Ensure ports 3000 and 8000 are available
4. Check the API documentation at http://localhost:8000/docs

## 🎯 Next Steps

- [ ] Add user authentication
- [ ] Support multiple document types
- [ ] Implement document management
- [ ] Add citation display
- [ ] Performance optimizations
- [ ] Docker containerization
