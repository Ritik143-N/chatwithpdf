from fastapi import APIRouter, UploadFile, File, HTTPException
from ..models.schemas import UploadResponse, QueryRequest, SearchResponse, AskResponse
from ..services.pdf_service import extract_text_from_pdf, chunk_text, generate_doc_id
from ..services.embedding_service import embedding_service
from ..services.llm_service import llm_service

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(file.file)
        
        print(f"Extracted text length: {len(text)}")
        print(f"Text preview: {text[:200]}...")
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")
        
        # Generate document ID
        doc_id = generate_doc_id()
        
        # Chunk the text
        chunks = chunk_text(text)
        
        print(f"Number of chunks created: {len(chunks)}")
        print(f"First chunk preview: {chunks[0][:100]}..." if chunks else "No chunks created")
        
        # Store embeddings
        embedding_service.store_document(doc_id, chunks)
        
        print(f"Document stored with ID: {doc_id}")
        
        return UploadResponse(
            message=f"PDF uploaded and processed successfully. Created {len(chunks)} chunks.",
            content=text[:500] + "..." if len(text) > 500 else text,
            doc_id=doc_id
        )
        
    except Exception as e:
        raise e
        print(f"Error in upload_pdf: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.post("/search", response_model=SearchResponse)
async def search_documents(request: QueryRequest):
    """Search for relevant document chunks"""
    try:
        results = embedding_service.search_similar(request.query, doc_id=request.doc_id)
        return SearchResponse(results=results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: QueryRequest):
    """Ask a question and get an answer based on stored documents"""
    try:
        # Search for relevant chunks
        search_results = embedding_service.search_similar(request.query, n_results=3, doc_id=request.doc_id)
                
        # Check if we have any documents
        if not search_results.get("documents") or not search_results["documents"]:
            return AskResponse(
                answer="I don't have any documents to search through. Please upload a PDF document first.",
                context=[]
            )
        
        # Check if documents list is empty or contains empty lists
        documents = search_results["documents"]
        if not documents or (isinstance(documents, list) and len(documents) == 0):
            return AskResponse(
                answer="No documents found. Please make sure you have uploaded a PDF document.",
                context=[]
            )
        
        # Get the first batch of documents
        doc_list = documents[0] if isinstance(documents[0], list) else documents
        
        if not doc_list:
            return AskResponse(
                answer="No relevant content found in your document for this question. Try asking about different topics covered in your PDF.",
                context=[]
            )
        
        # Combine context from top results
        context = " ".join(doc_list)
        
        print(f"Context length: {len(context)}")
        print(f"Context preview: {context[:200]}...")
        
        # Generate answer using LLM
        answer = llm_service.generate_answer(request.query, context)
        
        return AskResponse(
            answer=answer,
            context=doc_list
        )
        
    except Exception as e:
        print(f"Error in ask_question: {str(e)}")
        return AskResponse(
            answer=f"Sorry, there was an error processing your question: {str(e)}. Please try uploading your document again.",
            context=[]
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@router.get("/debug/collections")
async def debug_collections():
    """Debug endpoint to check what's in the vector database"""
    try:
        # Get collection info
        collection = embedding_service.collection
        count = collection.count()
        
        # Try to get a few documents
        if count > 0:
            sample = collection.peek(limit=3)
            return {
                "status": "ok",
                "collection_count": count,
                "sample_documents": sample.get("documents", []),
                "sample_ids": sample.get("ids", [])
            }
        else:
            return {
                "status": "empty",
                "collection_count": 0,
                "message": "No documents found in collection"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@router.post("/debug/test-llm")
async def test_llm(request: QueryRequest):
    """Test LLM directly with sample context"""
    sample_context = "This is a test document about a company called Test Corp. The company was founded in 2020 and specializes in AI technology."
    
    try:
        answer = llm_service.generate_answer(request.query, sample_context)
        return {
            "status": "ok",
            "query": request.query,
            "context": sample_context,
            "answer": answer,
            "using_local_llm": llm_service.use_local
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
