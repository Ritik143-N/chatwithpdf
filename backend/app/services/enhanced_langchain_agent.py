"""
Enhanced LangChain agent with support for multiple LLM providers including Mistral API
"""
from langchain_ollama import OllamaLLM # type: ignore
from langchain_chroma import Chroma # type: ignore
from langchain_huggingface import HuggingFaceEmbeddings # type: ignore
from langchain.text_splitter import RecursiveCharacterTextSplitter # type: ignore
from langchain.chains import RetrievalQA # type: ignore
from langchain.prompts import PromptTemplate # type: ignore
from langchain.schema import Document # type: ignore
from langchain.llms.base import LLM # type: ignore
from pydantic import Field
import os
from typing import List, Dict, Any, Optional
import re
import logging

from .mistral_service import get_mistral_service, is_mistral_available
from .gemini_service import get_gemini_service, is_gemini_available

logger = logging.getLogger(__name__)

class MistralLLM(LLM):
    """Custom LangChain LLM wrapper for Mistral API"""
    
    model_name: str = Field(default="mistral-small-latest")
    
    @property
    def _llm_type(self) -> str:
        return "mistral"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call Mistral API with the prompt"""
        mistral_service = get_mistral_service()
        if not mistral_service:
            return "Mistral service is not available. Please check your MISTRAL_API_KEY."
        
        messages = [{"role": "user", "content": prompt}]
        response = mistral_service.generate_response(messages, model=self.model_name)
        
        if response["success"]:
            return response["answer"]
        else:
            return f"Error: {response.get('error', 'Unknown error')}"


class GeminiLLM(LLM):
    """Custom LangChain LLM wrapper for Google Gemini API"""
    
    model_name: str = Field(default="gemini-1.5-flash")
    
    @property
    def _llm_type(self) -> str:
        return "gemini"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call Gemini API with the prompt"""
        gemini_service = get_gemini_service()
        if not gemini_service:
            return "Gemini service is not available. Please check your GEMINI_API_KEY."
        
        # The updated gemini service takes a string prompt directly
        response = gemini_service.generate_response(prompt, model_name=self.model_name)
        
        # Response is now a string, not a dictionary
        return response


class EnhancedLangChainAgent:
    def __init__(self, llm_provider: str = "auto", model_name: str = None):
        """
        Initialize the enhanced LangChain agent with multiple LLM support
        
        Args:
            llm_provider: "mistral", "gemini", "ollama", or "auto" (auto-detect)
            model_name: Specific model name to use
        """
        self.llm_provider = llm_provider
        self.persist_directory = "./chroma_db"
        
        # Initialize the appropriate LLM
        self.llm = self._initialize_llm(llm_provider, model_name)
        
        # Cache embeddings model to avoid reloading
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'batch_size': 32}
        )
        
        # Initialize ChromaDB vector store with optimization
        self.vectorstore = Chroma(
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name="documents",
            collection_metadata={"hnsw:space": "cosine"}
        )
        
        # Optimized text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Document cache to avoid reprocessing
        self.document_cache = {}
        
        # Setup QA chain
        self._setup_qa_chain()
    
    def _initialize_llm(self, llm_provider: str, model_name: Optional[str] = None):
        """Initialize the appropriate LLM based on provider"""
        
        if llm_provider == "auto":
            # Auto-detect available LLM provider (priority: Gemini > Mistral > Ollama)
            if is_gemini_available():
                llm_provider = "gemini"
                logger.info("Auto-detected: Using Gemini API")
            elif is_mistral_available():
                llm_provider = "mistral"
                logger.info("Auto-detected: Using Mistral API")
            else:
                llm_provider = "ollama"
                logger.info("Auto-detected: Using Ollama (no API services available)")
        
        if llm_provider == "gemini":
            if not is_gemini_available():
                logger.warning("Gemini API not available, trying Mistral...")
                if is_mistral_available():
                    llm_provider = "mistral"
                    logger.info("Falling back to Mistral API")
                else:
                    logger.warning("Mistral API also not available, falling back to Ollama")
                    llm_provider = "ollama"
            else:
                self.llm_provider = "gemini"
                model_name = model_name or "gemini-1.5-flash"
                logger.info(f"Initializing Gemini LLM with model: {model_name}")
                return GeminiLLM(model_name=model_name)
        
        if llm_provider == "mistral":
            if not is_mistral_available():
                logger.warning("Mistral API not available, falling back to Ollama")
                llm_provider = "ollama"
            else:
                self.llm_provider = "mistral"
                model_name = model_name or "mistral-small-latest"
                logger.info(f"Initializing Mistral LLM with model: {model_name}")
                return MistralLLM(model_name=model_name)
        
        # Default to Ollama
        self.llm_provider = "ollama"
        model_name = model_name or "llama3.2:1b"
        logger.info(f"Initializing Ollama LLM with model: {model_name}")
        
        return OllamaLLM(
            model=model_name,
            base_url="http://localhost:11434",
            num_ctx=2048,
            num_predict=512,
            temperature=0.1,
            top_k=10,
            top_p=0.9,
            repeat_penalty=1.1
        )
    
    def _setup_qa_chain(self):
        """Setup the retrieval QA chain"""
        if self.llm_provider == "gemini":
            # Detailed prompt for Gemini with markdown formatting
            custom_prompt_template = """You are a helpful assistant that answers questions based on the provided context.

Use the following context to answer the question. Follow these guidelines:
- Answer only based on the information in the context
- Be accurate and cite specific parts of the context when relevant
- Use markdown formatting for better readability (**bold**, *italic*, lists, etc.)
- If the context doesn't contain relevant information, say so clearly
- Provide comprehensive but concise answers

Context: {context}

Question: {question}

Answer: """
        elif self.llm_provider == "mistral":
            # More detailed prompt for Mistral which handles instructions better
            custom_prompt_template = """You are a helpful assistant that answers questions based on the provided context. 

Use the following context to answer the question. Be accurate and cite specific parts of the context when relevant.

Context: {context}

Question: {question}

Answer: """
        else:
            # Simpler prompt for Ollama models
            custom_prompt_template = """Answer the question based on the context. Be concise and cite specific parts.

Context: {context}
Question: {question}
Answer: """
        
        self.PROMPT = PromptTemplate(
            template=custom_prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            ),
            chain_type_kwargs={"prompt": self.PROMPT},
            return_source_documents=True
        )
    
    def add_documents(self, texts: List[str], doc_id: str, filename: str = None):
        """Add documents to the vector store"""
        try:
            # Check cache first to avoid reprocessing
            cache_key = f"{doc_id}_{hash(''.join(texts))}"
            if cache_key in self.document_cache:
                logger.info(f"Using cached version of document: {filename or doc_id}")
                return True
            
            logger.info(f"Processing document: {filename or doc_id}")
            
            # Clear existing documents for this doc_id first
            try:
                existing_docs = self.vectorstore.get(where={"doc_id": doc_id})
                if existing_docs['ids']:
                    if len(existing_docs['metadatas']) > 0:
                        existing_content_hash = existing_docs['metadatas'][0].get('content_hash', '')
                        new_content_hash = str(hash(''.join(texts)))
                        
                        if existing_content_hash == new_content_hash:
                            logger.info(f"Document unchanged, skipping: {filename or doc_id}")
                            self.document_cache[cache_key] = True
                            return True
                    
                    logger.info(f"Removing {len(existing_docs['ids'])} existing chunks for doc_id: {doc_id}")
                    self.vectorstore.delete(ids=existing_docs['ids'])
            except Exception as e:
                logger.debug(f"Could not clear existing docs (may not exist): {e}")
            
            # Create documents with metadata
            documents = []
            total_chunks = 0
            new_content_hash = str(hash(''.join(texts)))
            
            for i, text in enumerate(texts):
                chunks = self.text_splitter.split_text(text)
                
                for j, chunk in enumerate(chunks):
                    metadata = {
                        "doc_id": doc_id,
                        "chunk_id": f"{doc_id}_{i}_{j}",
                        "source": filename or f"document_{i}",
                        "chunk_index": j,
                        "text_index": i,
                        "content_hash": new_content_hash
                    }
                    
                    # Add content-based metadata for better search
                    chunk_lower = chunk.lower()
                    for keyword in ["risk", "security", "monitoring", "performance"]:
                        if keyword in chunk_lower:
                            metadata[f"contains_{keyword}"] = True
                    
                    doc = Document(page_content=chunk, metadata=metadata)
                    documents.append(doc)
                    total_chunks += 1
            
            # Batch add documents
            if documents:
                self.vectorstore.add_documents(documents)
                logger.info(f"Successfully stored {total_chunks} chunks in ChromaDB")
                
                # Cache successful processing
                self.document_cache[cache_key] = True
                
                # Verify storage
                verification = self.vectorstore.get(where={"doc_id": doc_id})
                logger.info(f"Verification: {len(verification['ids'])} chunks stored for doc_id: {doc_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False
    
    def ask_question(self, question: str, doc_id: str = None) -> Dict[str, Any]:
        """Ask a question using the enhanced QA chain"""
        try:
            logger.info(f"Processing question with {self.llm_provider.upper()}: '{question}'")
            
            # If doc_id is provided, filter search to that document
            if doc_id:
                retriever = self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={
                        "k": 4,
                        "filter": {"doc_id": doc_id}
                    }
                )
                
                temp_qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=retriever,
                    chain_type_kwargs={"prompt": self.PROMPT},
                    return_source_documents=True
                )
                
                result = temp_qa_chain.invoke({"query": question})
            else:
                result = self.qa_chain.invoke({"query": question})
            
            answer = result['result']
            sources = result.get('source_documents', [])
            
            logger.info(f"Generated answer with {len(sources)} source documents using {self.llm_provider}")
            
            # Prepare response
            response = {
                "answer": answer,
                "source_count": len(sources),
                "sources": [],
                "search_successful": True,
                "llm_provider": self.llm_provider
            }
            
            # Add source information
            for i, source in enumerate(sources[:3]):
                source_info = {
                    "chunk_index": i,
                    "content_preview": source.page_content[:200].replace('\n', ' ') + "...",
                    "metadata": source.metadata
                }
                response["sources"].append(source_info)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in enhanced LangChain agent: {e}")
            
            return {
                "answer": f"Sorry, there was an error processing your question: {str(e)}",
                "source_count": 0,
                "sources": [],
                "search_successful": False,
                "llm_provider": self.llm_provider
            }
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current ChromaDB collection"""
        try:
            collection_data = self.vectorstore.get()
            
            # Count documents by doc_id
            doc_counts = {}
            metadatas = collection_data.get('metadatas', [])
            for metadata in metadatas:
                doc_id = metadata.get('doc_id', 'unknown')
                doc_counts[doc_id] = doc_counts.get(doc_id, 0) + 1
            
            return {
                "total_chunks": len(collection_data.get('documents', [])),
                "collection_exists": True,
                "documents": doc_counts,
                "status": "healthy",
                "llm_provider": self.llm_provider
            }
        except Exception as e:
            return {
                "total_chunks": 0,
                "collection_exists": False,
                "documents": {},
                "error": str(e),
                "status": "error",
                "llm_provider": self.llm_provider
            }
    
    def clear_all_documents(self):
        """Clear all documents from the collection"""
        try:
            all_docs = self.vectorstore.get()
            if all_docs['ids']:
                self.vectorstore.delete(ids=all_docs['ids'])
                logger.info("Cleared all documents from ChromaDB")
            else:
                logger.info("No documents to clear")
            return True
        except Exception as e:
            logger.error(f"Error clearing documents: {e}")
            return False
    
    def search_documents(self, query: str, doc_id: str = None, k: int = 5) -> List[Dict]:
        """Search for documents similar to the query"""
        try:
            search_kwargs = {"k": k}
            if doc_id:
                search_kwargs["filter"] = {"doc_id": doc_id}
            
            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs=search_kwargs
            )
            
            docs = retriever.invoke(query)
            
            results = []
            for i, doc in enumerate(docs):
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "rank": i + 1
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def switch_llm_provider(self, provider: str, model_name: str = None):
        """Switch LLM provider at runtime"""
        try:
            old_provider = self.llm_provider
            self.llm = self._initialize_llm(provider, model_name)
            self._setup_qa_chain()
            logger.info(f"Switched LLM provider from {old_provider} to {self.llm_provider}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch LLM provider: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about available and current LLM providers"""
        return {
            "current_provider": self.llm_provider,
            "gemini_available": is_gemini_available(),
            "mistral_available": is_mistral_available(),
            "ollama_available": True,  # Assume ollama is always available for fallback
            "available_providers": ["gemini", "mistral", "ollama", "auto"]
        }


# Global instance with auto-detection
enhanced_langchain_agent = EnhancedLangChainAgent(llm_provider="gemini")
