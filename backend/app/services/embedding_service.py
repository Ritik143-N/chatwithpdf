from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Initialize ChromaDB client with telemetry completely disabled
        self.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection("documents")
        except:
            self.collection = self.client.create_collection("documents")
            
        # Keep track of the current document ID
        self.current_doc_id = None
    
    def clear_all_documents(self) -> None:
        """Clear all documents from the collection"""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection("documents")
            self.collection = self.client.create_collection("documents")
            self.current_doc_id = None
            print("All documents cleared from vector database")
        except Exception as e:
            print(f"Error clearing documents: {e}")
    
    def store_document(self, doc_id: str, chunks: List[str], clear_previous: bool = True) -> None:
        """Store document chunks with embeddings"""
        
        # Clear previous documents if requested (default behavior)
        if clear_previous:
            self.clear_all_documents()
        
        # Set the current document ID
        self.current_doc_id = doc_id
        
        for i, chunk in enumerate(chunks):
            embedding = self.model.encode(chunk).tolist()
            chunk_id = f"{doc_id}_{i}"
            
            # Store in ChromaDB
            self.collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[chunk_id],
                metadatas=[{"doc_id": doc_id, "chunk_index": i}]
            )
        
        print(f"Stored {len(chunks)} chunks for document {doc_id}")
    
    def search_similar(self, query: str, n_results: int = 3, doc_id: Optional[str] = None) -> Dict[str, Any]:
        """Search for similar chunks based on query"""
        query_embedding = self.model.encode(query).tolist()
        
        # If no specific doc_id provided, use the current document
        target_doc_id = doc_id or self.current_doc_id
        
        # Create where clause to filter by document ID if specified
        where_clause = {"doc_id": target_doc_id} if target_doc_id else None
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause
        )
        
        print(f"Search results for query '{query}' in doc '{target_doc_id}': found {len(results.get('documents', [[]])[0])} results")
        
        return results

# Global embedding service instance
embedding_service = EmbeddingService()
