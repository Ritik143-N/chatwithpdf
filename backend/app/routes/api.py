from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List, Optional
from ..models.schemas import UploadResponse, QueryRequest, SearchResponse, AskResponse, ContextItem
from ..models.session_schemas import (
    SessionListResponse, SessionDetailResponse, CreateSessionRequest, 
    SaveMessageRequest, ChatSession, ChatMessage
)
from ..services.document_service import document_processor, chunk_text, generate_doc_id
from ..services.enhanced_langchain_agent import enhanced_langchain_agent
from ..services.mistral_service import get_mistral_service, is_mistral_available
from ..services.gemini_service import get_gemini_service, is_gemini_available
from ..services.session_service import session_service
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process multiple document formats (PDF, DOCX, PPTX, TXT, RTF, Excel, etc.)"""
    
    # Check if file format is supported
    if not document_processor.is_supported(file.filename):
        supported_formats = document_processor.get_supported_formats()
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Supported formats: {', '.join(supported_formats)}"
        )
    
    try:
        # Debug file info
        print(f"🔍 Uploading file: {file.filename}")
        print(f"🔍 Content type: {file.content_type}")
        print(f"🔍 File size: {file.size if hasattr(file, 'size') else 'unknown'}")
        
        # Reset file pointer and read a bit to check if file is valid
        file.file.seek(0)
        first_bytes = file.file.read(100)
        file.file.seek(0)  # Reset again for processing
        print(f"🔍 First 100 bytes: {first_bytes[:50]}...")
        
        # Extract text from document
        result = document_processor.extract_text(file.file, file.filename)
        
        if not result['success']:
            error_msg = result['error']
            print(f"❌ Document processing failed: {error_msg}")
            
            # Provide more helpful error messages
            if "not a zip file" in error_msg.lower():
                error_msg = f"Invalid DOCX file format. The file may be corrupted or not a valid DOCX document. Original error: {error_msg}"
            elif "no text found" in error_msg.lower():
                error_msg = f"The document appears to be empty or contains only images/formatting without readable text."
            
            raise HTTPException(status_code=400, detail=f"Error processing document: {error_msg}")
        
        text = result['text']
        metadata = result['metadata']
        file_format = result['format']
        
        print(f"📄 Processed {file_format} file: {file.filename}")
        print(f"📄 Extracted text length: {len(text)}")
        print(f"📄 Metadata: {metadata}")
        print(f"📄 Text preview: {text[:200]}...")
        
        if not text.strip():
            raise HTTPException(status_code=400, detail=f"No text found in {file_format} document")
        
        # Generate document ID
        doc_id = generate_doc_id()
        
        # Add document to enhanced LangChain agent
        success = enhanced_langchain_agent.add_documents([text], doc_id, file.filename)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store document")
        
        print(f"✅ Document stored with ID: {doc_id} using enhanced LangChain agent")
        
        # Get chunk count for response
        collection_info = enhanced_langchain_agent.get_collection_info()
        doc_chunk_count = collection_info.get("documents", {}).get(doc_id, 0)
        
        return UploadResponse(
            filename=file.filename,
            doc_id=doc_id,
            num_chunks=doc_chunk_count,
            message=f"{file_format.upper()} document uploaded and processed successfully with enhanced LangChain"
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions to preserve status codes
        raise
    except Exception as e:
        print(f"❌ Error uploading document: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: QueryRequest):
    """Ask a question using enhanced LangChain agent with Mistral support"""
    try:
        print(f"🤖 Enhanced LangChain agent received question: '{request.query}' for doc_id: {request.doc_id}")
        
        # Use enhanced LangChain agent to answer the question
        result = enhanced_langchain_agent.ask_question(request.query, request.doc_id)
        
        if not result.get("search_successful", False):
            return AskResponse(
                answer=result.get("answer", "Sorry, I couldn't process your question."),
                context=[]
            )
        
        print(f"✅ Enhanced LangChain answer generated with {result.get('source_count', 0)} sources using {result.get('llm_provider', 'unknown')} provider")
        
        # Extract context from sources for frontend display
        context = []
        for i, source in enumerate(result.get("sources", [])[:3]):  # Top 3 sources
            context.append(ContextItem(
                chunk_index=i,
                content=source.get("content_preview", ""),
                metadata=source.get("metadata", {})
            ))
        
        return AskResponse(
            answer=result["answer"],
            context=context
        )
        
    except Exception as e:
        print(f"❌ Error in ask_question: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return AskResponse(
            answer=f"Sorry, there was an error processing your question: {str(e)}",
            context=[]
        )

@router.post("/search", response_model=SearchResponse)
async def search_documents(request: QueryRequest):
    """Search for documents using enhanced LangChain similarity search"""
    try:
        print(f"🔍 Searching for: '{request.query}' in doc_id: {request.doc_id}")
        
        # Use enhanced LangChain agent's search functionality
        search_results = enhanced_langchain_agent.search_documents(
            query=request.query,
            doc_id=request.doc_id,
            k=8
        )
        
        if not search_results:
            return SearchResponse(
                query=request.query,
                results=[],
                total_found=0
            )
        
        # Format results for response
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                "content": result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"],
                "metadata": result["metadata"],
                "rank": result["rank"]
            })
        
        print(f"🔍 Found {len(formatted_results)} search results")
        
        return SearchResponse(
            query=request.query,
            results=formatted_results,
            total_found=len(search_results)
        )
        
    except Exception as e:
        print(f"❌ Error in search: {str(e)}")
        return SearchResponse(
            query=request.query,
            results=[],
            total_found=0,
            error=f"Search failed: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint with enhanced LLM provider information"""
    try:
        # Check enhanced LangChain agent status
        collection_info = enhanced_langchain_agent.get_collection_info()
        provider_info = enhanced_langchain_agent.get_provider_info()
        
        return {
            "status": "healthy",
            "langchain_status": collection_info.get("status", "unknown"),
            "total_chunks": collection_info.get("total_chunks", 0),
            "documents": collection_info.get("documents", {}),
            "llm_provider": provider_info.get("current_provider"),
            "mistral_available": provider_info.get("mistral_available", False),
            "available_providers": provider_info.get("available_providers", [])
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/debug/collections")
async def debug_collections():
    """Debug endpoint to check what's in ChromaDB"""
    try:
        collection_info = enhanced_langchain_agent.get_collection_info()
        
        return {
            "status": "ok",
            "collection_info": collection_info
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@router.post("/debug/test-llm")
async def test_llm(request: QueryRequest):
    """Test LLM directly with enhanced LangChain"""
    try:
        # Test with a simple question
        result = enhanced_langchain_agent.ask_question("What is this document about?")
        
        return {
            "status": "ok",
            "query": request.query,
            "result": result,
            "langchain_working": result.get("search_successful", False)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# New Mistral-specific endpoints
@router.post("/mistral/test")
async def test_mistral_connection():
    """Test Mistral API connection"""
    try:
        mistral_service = get_mistral_service()
        if not mistral_service:
            return {
                "status": "error",
                "message": "Mistral service not available. Please check MISTRAL_API_KEY environment variable."
            }
        
        test_result = mistral_service.test_connection()
        return test_result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error testing Mistral connection: {str(e)}"
        }

# Gemini-specific endpoints
@router.post("/gemini/test")
async def test_gemini_connection():
    """Test Google Gemini API connection"""
    try:
        gemini_service = get_gemini_service()
        if not gemini_service:
            return {
                "status": "error",
                "message": "Gemini service not available. Please check GEMINI_API_KEY environment variable."
            }
        
        test_result = gemini_service.test_connection()
        return test_result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error testing Gemini connection: {str(e)}"
        }

@router.get("/gemini/models")
async def list_gemini_models():
    """List available Gemini models"""
    try:
        gemini_service = get_gemini_service()
        if not gemini_service:
            return {
                "status": "error",
                "message": "Gemini service not available. Please check GEMINI_API_KEY environment variable."
            }
        
        models_result = gemini_service.list_available_models()
        return models_result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing Gemini models: {str(e)}"
        }

@router.post("/gemini/switch-model")
async def switch_gemini_model(model_name: str):
    """Switch Gemini model"""
    try:
        gemini_service = get_gemini_service()
        if not gemini_service:
            return {
                "status": "error",
                "message": "Gemini service not available. Please check GEMINI_API_KEY environment variable."
            }
        
        switch_result = gemini_service.switch_model(model_name)
        return switch_result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error switching Gemini model: {str(e)}"
        }

@router.post("/llm/switch")
async def switch_llm_provider(provider: str, model_name: str = None):
    """Switch LLM provider at runtime"""
    try:
        success = enhanced_langchain_agent.switch_llm_provider(provider, model_name)
        
        if success:
            provider_info = enhanced_langchain_agent.get_provider_info()
            return {
                "status": "success",
                "message": f"Switched to {provider_info['current_provider']} provider",
                "provider_info": provider_info
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to switch to {provider} provider"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error switching LLM provider: {str(e)}"
        }

@router.get("/llm/providers")
async def get_llm_providers():
    """Get information about available LLM providers"""
    try:
        provider_info = enhanced_langchain_agent.get_provider_info()
        
        # Add additional info about each provider
        detailed_info = {
            "current_provider": provider_info["current_provider"],
            "providers": {
                "gemini": {
                    "available": provider_info["gemini_available"],
                    "description": "Google Gemini API - Advanced multimodal AI with excellent reasoning",
                    "models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"],
                    "requires": "GEMINI_API_KEY environment variable"
                },
                "mistral": {
                    "available": provider_info["mistral_available"],
                    "description": "Mistral API - Fast and high-quality commercial LLM service",
                    "models": ["mistral-tiny", "mistral-small-latest", "mistral-medium-latest", "mistral-large-latest"],
                    "requires": "MISTRAL_API_KEY environment variable"
                },
                "ollama": {
                    "available": provider_info.get("ollama_available", True),
                    "description": "Ollama - Local open-source LLM models",
                    "models": ["llama3.2:1b", "llama3", "llama2", "codellama"],
                    "requires": "Local Ollama installation and running service"
                },
                "auto": {
                    "available": True,
                    "description": "Auto-detect - Automatically choose the best available provider",
                    "priority": ["gemini", "mistral", "ollama"]
                }
            }
        }
        
        return detailed_info
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@router.delete("/clear")
async def clear_all_documents():
    """Clear all documents from ChromaDB"""
    try:
        success = enhanced_langchain_agent.clear_all_documents()
        
        if success:
            return {
                "status": "success",
                "message": "All documents cleared from ChromaDB"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to clear documents"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@router.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Test endpoint to debug file upload issues"""
    try:
        # Get basic file info
        file_info = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file.size if hasattr(file, 'size') else None,
        }
        
        # Read file content
        file.file.seek(0)
        content = file.file.read()
        file.file.seek(0)
        
        file_info.update({
            "actual_size": len(content),
            "first_100_bytes": content[:100].hex() if len(content) > 0 else "empty",
            "is_supported": document_processor.is_supported(file.filename)
        })
        
        # Try to extract text
        try:
            result = document_processor.extract_text(file.file, file.filename)
            file_info["extraction_result"] = result
        except Exception as e:
            file_info["extraction_error"] = str(e)
            
        return file_info
        
    except Exception as e:
        return {"error": str(e)}

@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported document formats"""
    formats = document_processor.get_supported_formats()
    format_descriptions = {
        ".pdf": "PDF Documents (with OCR support)",
        ".docx": "Microsoft Word Documents (2007+)",
        ".doc": "Microsoft Word Documents (Legacy)",
        ".pptx": "Microsoft PowerPoint Presentations (2007+)",
        ".ppt": "Microsoft PowerPoint Presentations (Legacy)",
        ".xlsx": "Microsoft Excel Spreadsheets (2007+)",
        ".xls": "Microsoft Excel Spreadsheets (Legacy)",
        ".txt": "Plain Text Files",
        ".rtf": "Rich Text Format Documents",
        ".md": "Markdown Files",
    }
    
    return {
        "supported_formats": formats,
        "format_descriptions": format_descriptions,
        "total_formats": len(formats)
    }

@router.get("/document/{doc_id}/content")
async def get_document_content(doc_id: str):
    """Get document content for preview"""
    try:
        # Get document from vector store
        result = enhanced_langchain_agent.search_documents("", doc_id, k=50)  # Get more chunks for preview
        
        # The search_documents method returns a list directly, not a dict with "results"
        if not result or not isinstance(result, list):
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Combine chunks to reconstruct document content
        content_parts = []
        seen_chunks = set()
        
        for doc in result:
            chunk_content = doc.get("content", "")
            chunk_metadata = doc.get("metadata", {})
            chunk_id = chunk_metadata.get("chunk_index", "")
            
            # Avoid duplicate chunks
            if chunk_id not in seen_chunks and chunk_content.strip():
                content_parts.append(chunk_content)
                seen_chunks.add(chunk_id)
        
        # Sort by chunk index if available
        def get_chunk_index(item):
            if isinstance(item, str):
                return 0
            try:
                # Try to find chunk index from the content or metadata
                return 0  # Default sorting
            except:
                return 0
        
        # Get document info
        collection_info = enhanced_langchain_agent.get_collection_info()
        doc_info = collection_info.get("documents", {}).get(doc_id, 0)
        
        return {
            "doc_id": doc_id,
            "content": "\\n\\n".join(content_parts),
            "preview_content": "\\n\\n".join(content_parts[:10]),  # First 10 chunks for preview
            "total_chunks": len(content_parts),
            "metadata": {"chunks": doc_info}
        }
        
    except Exception as e:
        print(f"❌ Error getting document content: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving document content: {str(e)}")

# ==========================================
# SESSION MANAGEMENT ENDPOINTS
# ==========================================

@router.post("/sessions", response_model=ChatSession)
async def create_session(request: CreateSessionRequest):
    """Create a new chat session for a document"""
    try:
        # Get current model provider
        provider_info = enhanced_langchain_agent.get_provider_info()
        current_provider = provider_info.get("current_provider", "unknown")
        
        session = session_service.create_session(
            document_id=request.document_id,
            document_name=request.document_name,
            document_filename=request.document_filename,
            model_provider=current_provider
        )
        
        return session
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get("/sessions", response_model=SessionListResponse)
async def get_sessions(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    """Get list of all chat sessions"""
    try:
        return session_service.get_sessions(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")

@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(session_id: str):
    """Get detailed information about a specific session including messages"""
    try:
        session_detail = session_service.get_session_detail(session_id)
        if not session_detail:
            raise HTTPException(status_code=404, detail="Session not found")
        return session_detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@router.get("/sessions/document/{document_id}")
async def get_sessions_by_document(document_id: str):
    """Get all sessions for a specific document"""
    try:
        sessions = session_service.get_sessions_by_document(document_id)
        return {"sessions": sessions, "count": len(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document sessions: {str(e)}")

@router.post("/sessions/{session_id}/messages", response_model=ChatMessage)
async def save_message(session_id: str, request: SaveMessageRequest):
    """Save a message to a session"""
    try:
        # Verify session exists
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        message = session_service.save_message(
            session_id=request.session_id,
            message_type=request.message_type,
            content=request.content,
            model_used=request.model_used,
            context_sources=request.context_sources
        )
        
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save message: {str(e)}")

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str, 
    limit: int = Query(100, ge=1, le=500), 
    offset: int = Query(0, ge=0)
):
    """Get messages for a specific session"""
    try:
        # Verify session exists
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = session_service.get_session_messages(session_id, limit=limit, offset=offset)
        return {"messages": messages, "count": len(messages)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all its messages"""
    try:
        success = session_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@router.put("/sessions/{session_id}/model")
async def update_session_model(session_id: str, model_provider: str):
    """Update the model provider for a session"""
    try:
        success = session_service.update_session_model(session_id, model_provider)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": f"Session model updated to {model_provider}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update session model: {str(e)}")

# Enhanced ask endpoint with session support
@router.post("/sessions/{session_id}/ask", response_model=AskResponse)
async def ask_question_with_session(session_id: str, request: QueryRequest):
    """Ask a question within a specific session context"""
    try:
        # Verify session exists
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        print(f"🤖 Session-based question: '{request.query}' for session: {session_id}")
        
        # Use the document_id from the session if not provided in request
        doc_id = request.doc_id or session.document_id
        
        # Get current model provider
        provider_info = enhanced_langchain_agent.get_provider_info()
        current_provider = provider_info.get("current_provider", "unknown")
        
        # Use enhanced LangChain agent to answer the question
        result = enhanced_langchain_agent.ask_question(request.query, doc_id)
        
        if not result.get("search_successful", False):
            bot_response = result.get("answer", "Sorry, I couldn't process your question.")
        else:
            bot_response = result.get("answer", "")
        
        # Save user message to session
        session_service.save_message(
            session_id=session_id,
            message_type="user",
            content=request.query
        )
        
        # Save bot response to session
        context_sources = []
        if result.get("sources"):
            context_sources = [{"content": src.get("content_preview", ""), "metadata": src.get("metadata", {})} 
                             for src in result["sources"]]
        
        session_service.save_message(
            session_id=session_id,
            message_type="bot",
            content=bot_response,
            model_used=current_provider,
            context_sources=context_sources
        )
        
        print(f"✅ Session answer generated with {result.get('source_count', 0)} sources using {current_provider}")
        
        # Extract context from sources for frontend display
        context = []
        if result.get("sources"):
            for i, source in enumerate(result["sources"][:3]):
                context.append(ContextItem(
                    chunk_index=i,
                    content=source.get("content_preview", ""),
                    metadata=source.get("metadata", {})
                ))
        
        return AskResponse(
            answer=bot_response,
            context=context,
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in session-based ask: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")
