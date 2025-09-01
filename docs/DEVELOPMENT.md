# Development Guide

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Initial Setup
```bash
# Clone the repository
git clone https://github.com/Ritik143-N/chatwithpdf.git
cd chatwithpdf

# Run setup script
./scripts/setup.sh
```

## Development Workflow

### Backend Development
```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Format code
black app/

# Type checking
mypy app/
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build

# Lint code
npm run lint
```

## Project Structure

### Backend (`/backend`)
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   ├── routes/
│   │   ├── __init__.py
│   │   └── api.py          # API endpoints
│   └── services/
│       ├── __init__.py
│       ├── pdf_service.py   # PDF processing
│       ├── embedding_service.py # Text embeddings
│       └── llm_service.py   # LLM integration
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
└── venv/                   # Virtual environment
```

### Frontend (`/frontend`)
```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── ChatBox.js      # Chat interface
│   │   ├── DocumentViewer.js # Document display
│   │   ├── FileUpload.js   # File upload component
│   │   └── Navbar.js       # Navigation bar
│   ├── services/
│   │   └── api.js          # API client
│   ├── App.js              # Main application component
│   ├── App.css             # Application styles
│   └── index.js            # React entry point
├── package.json            # Node.js dependencies
├── tailwind.config.js      # Tailwind CSS configuration
└── Dockerfile              # Container configuration
```

## API Development

### Adding New Endpoints

1. Define the request/response models in `backend/app/models/schemas.py`
2. Implement the endpoint logic in `backend/app/routes/api.py`
3. Add any business logic to appropriate service files
4. Update API documentation with docstrings

### Example Endpoint
```python
@router.post("/example", response_model=ExampleResponse)
async def example_endpoint(request: ExampleRequest):
    """
    Example endpoint description.
    """
    # Implementation here
    return ExampleResponse(...)
```

## Testing

### Backend Testing
```bash
cd backend
pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Integration Testing
```bash
# Start both services
docker-compose up

# Run integration tests
python scripts/test_*.py
```

## Environment Variables

### Backend
- `PORT`: Server port (default: 8000)
- `HUGGING_FACE_TOKEN`: HuggingFace API token
- `USE_LOCAL_LLM`: Use local Ollama instead of HuggingFace

### Frontend
- `REACT_APP_BACKEND_URL`: Backend API URL

## Debugging

### Backend Debugging
- Use FastAPI's automatic documentation at `/docs`
- Enable debug logging in development
- Use debugger breakpoints with `import pdb; pdb.set_trace()`

### Frontend Debugging
- Use React Developer Tools browser extension
- Check browser console for errors
- Use `console.log()` for debugging

## Code Style

### Python (Backend)
- Use Black for code formatting
- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for functions and classes

### JavaScript/React (Frontend)
- Use Prettier for code formatting
- Follow React best practices
- Use functional components with hooks
- Implement proper error boundaries

## Performance Optimization

### Backend
- Use async/await for I/O operations
- Implement proper caching for embeddings
- Optimize database queries
- Use connection pooling

### Frontend
- Implement code splitting
- Use React.memo for expensive components
- Optimize bundle size
- Implement proper loading states

## Security Considerations

- Validate all user inputs
- Implement proper file upload restrictions
- Use HTTPS in production
- Sanitize file contents before processing
- Implement rate limiting for API endpoints

## Deployment

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## Troubleshooting

### Common Issues
1. **Port already in use**: Change port in environment variables
2. **Module not found**: Check virtual environment activation
3. **CORS errors**: Verify backend URL in frontend configuration
4. **PDF processing fails**: Check file format and size limits

### Getting Help
- Check existing GitHub issues
- Read error logs carefully
- Verify all prerequisites are met
- Test with minimal examples first
