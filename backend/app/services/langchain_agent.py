from langchain_ollama import OllamaLLM # type: ignore
from langchain_chroma import Chroma # type: ignore
from langchain_community.embeddings import HuggingFaceEmbeddings # type: ignore
from langchain.text_splitter import RecursiveCharacterTextSplitter # type: ignore
from langchain.chains import RetrievalQA # type: ignore
from langchain.prompts import PromptTemplate # type: ignore
from langchain.schema import Document # type: ignore
import os
from typing import List, Dict, Any
import re


class LangChainAgent:
    def __init__(self, model_name: str = "llama3.2:1b"):
        """Initialize the LangChain agent with Ollama LLM and single ChromaDB"""
        self.model_name = model_name
        # Use single ChromaDB directory
        self.persist_directory = "./chroma_db"
        
        # Initialize Ollama LLM
        self.llm = OllamaLLM(
            model=self.model_name,
            base_url="http://localhost:11434"
        )
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize ChromaDB vector store (single collection)
        self.vectorstore = Chroma(
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name="documents"  # Single collection for all documents
        )
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Setup QA chain
        self._setup_qa_chain()
    
    def _setup_qa_chain(self):
        """Setup the retrieval QA chain"""
        # Custom prompt template for better document QA
        custom_prompt_template = """You are a helpful assistant that answers questions based on the provided document context.
        
Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say "I cannot find this information in the provided document."

ALWAYS cite specific parts of the document when answering.
Be precise and detailed in your answers.

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
                search_kwargs={"k": 8}  # Retrieve more documents for better context
            ),
            chain_type_kwargs={"prompt": self.PROMPT},
            return_source_documents=True
        )
    
    def add_documents(self, texts: List[str], doc_id: str, filename: str = None):
        """Add documents to the vector store"""
        try:
            print(f"🔄 Processing document: {filename or doc_id}")
            
            # Clear existing documents for this doc_id first
            try:
                # Get existing documents with this doc_id
                existing_docs = self.vectorstore.get(where={"doc_id": doc_id})
                if existing_docs['ids']:
                    print(f"🧹 Removing {len(existing_docs['ids'])} existing chunks for doc_id: {doc_id}")
                    self.vectorstore.delete(ids=existing_docs['ids'])
            except Exception as e:
                print(f"Note: Could not clear existing docs (may not exist): {e}")
            
            # Create documents with metadata
            documents = []
            total_chunks = 0
            
            for i, text in enumerate(texts):
                # Split text into chunks
                chunks = self.text_splitter.split_text(text)
                
                for j, chunk in enumerate(chunks):
                    # Enhanced metadata
                    metadata = {
                        "doc_id": doc_id,
                        "chunk_id": f"{doc_id}_{i}_{j}",
                        "source": filename or f"document_{i}",
                        "chunk_index": j,
                        "text_index": i,
                        "chunk_length": len(chunk)
                    }
                    
                    # Add content-based metadata for better search
                    chunk_lower = chunk.lower()
                    if any(word in chunk_lower for word in ["risk", "security", "monitoring", "performance"]):
                        if "risk" in chunk_lower:
                            metadata["contains_risk"] = True
                        if "security" in chunk_lower:
                            metadata["contains_security"] = True
                        if "monitoring" in chunk_lower:
                            metadata["contains_monitoring"] = True
                        if "performance" in chunk_lower:
                            metadata["contains_performance"] = True
                    
                    # Check for document metadata (author, date, etc.)
                    if any(word in chunk_lower for word in ["prepared by", "author", "date:", "version:"]):
                        metadata["has_metadata"] = True
                    
                    doc = Document(
                        page_content=chunk,
                        metadata=metadata
                    )
                    documents.append(doc)
                    total_chunks += 1
            
            # Add to vector store
            self.vectorstore.add_documents(documents)
            print(f"✅ Successfully stored {total_chunks} chunks in ChromaDB")
            
            # Verify storage
            verification = self.vectorstore.get(where={"doc_id": doc_id})
            print(f"🔍 Verification: {len(verification['ids'])} chunks stored for doc_id: {doc_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding documents: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def ask_question(self, question: str, doc_id: str = None) -> Dict[str, Any]:
        """Ask a question using the LangChain QA chain"""
        try:
            print(f"\n🤖 LANGCHAIN AGENT: Processing question: '{question}'")
            
            # If doc_id is provided, filter search to that document
            if doc_id:
                # Create a new retriever with doc_id filter
                retriever = self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={
                        "k": 8,
                        "filter": {"doc_id": doc_id}
                    }
                )
                
                # Create temporary QA chain with filtered retriever
                temp_qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=retriever,
                    chain_type_kwargs={"prompt": self.PROMPT},
                    return_source_documents=True
                )
                
                result = temp_qa_chain.invoke({"query": question})
            else:
                # Use default QA chain (searches all documents)
                result = self.qa_chain.invoke({"query": question})
            
            answer = result['result']
            sources = result.get('source_documents', [])
            
            print(f"📝 Generated answer with {len(sources)} source documents")
            
            # Prepare response
            response = {
                "answer": answer,
                "source_count": len(sources),
                "sources": [],
                "search_successful": True
            }
            
            # Add source information for debugging/context
            for i, source in enumerate(sources[:3]):  # Top 3 sources
                source_info = {
                    "chunk_index": i,
                    "content_preview": source.page_content[:200].replace('\n', ' ') + "...",
                    "metadata": source.metadata
                }
                response["sources"].append(source_info)
            
            return response
            
        except Exception as e:
            print(f"❌ Error in LangChain agent: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "answer": f"Sorry, there was an error processing your question: {str(e)}",
                "source_count": 0,
                "sources": [],
                "search_successful": False
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
                "status": "healthy"
            }
        except Exception as e:
            return {
                "total_chunks": 0,
                "collection_exists": False,
                "documents": {},
                "error": str(e),
                "status": "error"
            }
    
    def clear_all_documents(self):
        """Clear all documents from the collection"""
        try:
            # Get all documents and delete them
            all_docs = self.vectorstore.get()
            if all_docs['ids']:
                self.vectorstore.delete(ids=all_docs['ids'])
                print("✅ Cleared all documents from ChromaDB")
            else:
                print("📝 No documents to clear")
            return True
        except Exception as e:
            print(f"❌ Error clearing documents: {e}")
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
            print(f"❌ Error searching documents: {e}")
            return []


# Global instance
langchain_agent = LangChainAgent()
