"""
Mistral API service for chat functionality
"""
import os
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from mistralai import Mistral, UserMessage, SystemMessage, AssistantMessage
import logging


load_dotenv()
logger = logging.getLogger(__name__)

class MistralService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Mistral service with API key"""
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "MISTRAL_API_KEY environment variable is required. "
                "Please set it with your Mistral API key."
            )
        
        self.client = Mistral(api_key=self.api_key)
        
        # Default model - you can change this to other Mistral models
        self.model = "mistral-small-latest"  # Fast and cost-effective
        
        # Available models:
        # - mistral-tiny: Cheapest, fastest
        # - mistral-small-latest: Good balance of cost/performance 
        # - mistral-medium-latest: Better performance
        # - mistral-large-latest: Best performance, most expensive
    
    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = 1000
    ) -> Dict[str, Any]:
        """
        Generate a response using Mistral API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to self.model)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Convert messages to Mistral format
            mistral_messages = []
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                if role == "system":
                    mistral_messages.append(SystemMessage(content=content))
                elif role == "user":
                    mistral_messages.append(UserMessage(content=content))
                elif role == "assistant":
                    mistral_messages.append(AssistantMessage(content=content))
                else:
                    # Default to user message
                    mistral_messages.append(UserMessage(content=content))
            
            # Make API call
            response = self.client.chat.complete(
                model=model or self.model,
                messages=mistral_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract response
            if response.choices and len(response.choices) > 0:
                answer = response.choices[0].message.content
                
                return {
                    "success": True,
                    "answer": answer,
                    "model": model or self.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    }
                }
            else:
                return {
                    "success": False,
                    "answer": "No response generated",
                    "error": "Empty response from Mistral API"
                }
                
        except Exception as e:
            logger.error(f"Mistral API error: {e}")
            return {
                "success": False,
                "answer": f"Error generating response: {str(e)}",
                "error": str(e)
            }
    
    def chat_with_context(
        self, 
        question: str, 
        context: str, 
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response with document context (for RAG)
        
        Args:
            question: User question
            context: Relevant document context
            model: Model to use
            
        Returns:
            Dictionary with response and metadata
        """
        
        # Create system prompt for RAG
        system_prompt = """You are a helpful assistant that answers questions based on the provided context. 
Follow these guidelines:
- Answer only based on the information in the context
- If the context doesn't contain relevant information, say so clearly
- Be concise and accurate
- Include relevant quotes or references from the context when appropriate
- If asked about something not in the context, explain that the information isn't available in the provided documents"""
        
        # Create user prompt with context
        user_prompt = f"""Context:
{context}

Question: {question}

Please answer the question based on the provided context."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.generate_response(messages, model=model, temperature=0.2)
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the Mistral API connection"""
        try:
            test_messages = [
                {"role": "user", "content": "Hello, this is a test message. Please respond with 'Connection successful'."}
            ]
            
            response = self.generate_response(test_messages, max_tokens=50)
            
            if response["success"]:
                return {
                    "success": True,
                    "message": "Mistral API connection successful",
                    "model": self.model,
                    "response": response["answer"]
                }
            else:
                return {
                    "success": False,
                    "message": "Mistral API connection failed",
                    "error": response.get("error", "Unknown error")
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": "Mistral API connection failed",
                "error": str(e)
            }


# Global instance - will be initialized when API key is available
mistral_service = None

def get_mistral_service() -> Optional[MistralService]:
    """Get or create Mistral service instance"""
    global mistral_service
    
    if mistral_service is None:
        try:
            mistral_service = MistralService()
            logger.info("Mistral service initialized successfully")
        except ValueError as e:
            logger.warning(f"Mistral service not available: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize Mistral service: {e}")
            return None
    
    return mistral_service

def is_mistral_available() -> bool:
    """Check if Mistral service is available"""
    return get_mistral_service() is not None
