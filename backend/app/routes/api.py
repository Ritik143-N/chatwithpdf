from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from ..models.schemas import UploadResponse, QueryRequest, SearchResponse, AskResponse
from ..services.pdf_service import extract_text_from_pdf, chunk_text, generate_doc_id
from ..services.langchain_agent import langchain_agent

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file using LangChain"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(file.file)
        
        print(f"📄 Extracted text length: {len(text)}")
        print(f"📄 Text preview: {text[:200]}...")
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")
        
        # Generate document ID
        doc_id = generate_doc_id()
        
        # Add document to LangChain agent
        success = langchain_agent.add_documents([text], doc_id, file.filename)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store document")
        
        print(f"✅ Document stored with ID: {doc_id} using LangChain agent")
        
        # Get chunk count for response
        collection_info = langchain_agent.get_collection_info()
        doc_chunk_count = collection_info.get("documents", {}).get(doc_id, 0)
        
        return UploadResponse(
            filename=file.filename,
            doc_id=doc_id,
            num_chunks=doc_chunk_count,
            message="PDF uploaded and processed successfully with LangChain"
        )
        
    except Exception as e:
        print(f"❌ Error uploading PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: QueryRequest):
    """Ask a question using LangChain agent"""
    try:
        print(f"🤖 LangChain agent received question: '{request.query}' for doc_id: {request.doc_id}")
        
        # Use LangChain agent to answer the question
        result = langchain_agent.ask_question(request.query, request.doc_id)
        
        if not result.get("search_successful", False):
            return AskResponse(
                answer=result.get("answer", "Sorry, I couldn't process your question."),
                context=[]
            )
        
        print(f"✅ LangChain answer generated with {result.get('source_count', 0)} sources")
        
        # Extract context from sources for frontend display
        context_docs = []
        for source in result.get("sources", [])[:3]:  # Top 3 sources
            context_docs.append(source.get("content_preview", ""))
        
        return AskResponse(
            answer=result["answer"],
            context=context_docs
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
    """Search for documents using LangChain similarity search"""
    try:
        print(f"🔍 Searching for: '{request.query}' in doc_id: {request.doc_id}")
        
        # Use LangChain agent's search functionality
        search_results = langchain_agent.search_documents(
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
    """Health check endpoint"""
    try:
        # Check LangChain agent status
        collection_info = langchain_agent.get_collection_info()
        
        return {
            "status": "healthy",
            "langchain_status": collection_info.get("status", "unknown"),
            "total_chunks": collection_info.get("total_chunks", 0),
            "documents": collection_info.get("documents", {})
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
        collection_info = langchain_agent.get_collection_info()
        
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
    """Test LLM directly with LangChain"""
    try:
        # Test with a simple question
        result = langchain_agent.ask_question("What is this document about?")
        
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

@router.delete("/clear")
async def clear_all_documents():
    """Clear all documents from ChromaDB"""
    try:
        success = langchain_agent.clear_all_documents()
        
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
