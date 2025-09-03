"""
Google Gemini API service for chat functionality
Enhanced implementation with proper API integration
"""
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging
import requests
import json

load_dotenv()
logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini service with API key"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. "
                "Please set it with your Google AI API key."
            )
        
        # Use the REST API directly for better compatibility
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model_name = "gemini-1.5-flash"  # Fast and efficient model
        
        # Available models:
        # - gemini-1.5-flash: Fast, efficient, good for most tasks
        # - gemini-1.5-pro: More capable, better reasoning
        # - gemini-1.0-pro: Stable, reliable
        
        logger.info(f"Gemini service initialized with model: {self.model_name}")
    
    def generate_response(
        self, 
        prompt: str,
        model_name: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = 2048
    ) -> str:
        """
        Generate a response using Gemini API via REST
        
        Args:
            prompt: The input prompt text
            model_name: Model to use (defaults to self.model_name)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        try:
            current_model = model_name or self.model_name
            
            # Prepare the API request
            url = f"{self.base_url}/models/{current_model}:generateContent?key={self.api_key}"
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "topK": 40,
                    "topP": 0.8,
                    "maxOutputTokens": max_tokens or 2048,
                    "stopSequences": []
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            # Make the API request
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    
                    if 'content' in candidate and 'parts' in candidate['content']:
                        text = candidate['content']['parts'][0].get('text', '')
                        if text:
                            logger.info(f"✅ Gemini API response successful with model: {current_model}")
                            return text.strip()
                    
                    # Check if content was blocked
                    if candidate.get('finishReason') == 'SAFETY':
                        return "Response was blocked due to safety filters. Please try rephrasing your question."
                
                # Fallback if no content found
                logger.warning("No content found in Gemini response")
                return "Sorry, I couldn't generate a response. Please try rephrasing your question."
            
            else:
                error_msg = f"Gemini API error: HTTP {response.status_code}"
                if response.text:
                    try:
                        error_detail = response.json()
                        if 'error' in error_detail:
                            error_msg += f" - {error_detail['error'].get('message', response.text)}"
                    except:
                        error_msg += f" - {response.text}"
                
                logger.error(error_msg)
                return f"API Error: {error_msg}"
                
        except requests.exceptions.Timeout:
            logger.error("Gemini API request timed out")
            return "Request timed out. Please try again."
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error calling Gemini API: {e}")
            return f"Network error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in Gemini API: {e}")
            return f"Error generating response: {str(e)}"
    
    def chat_with_context(
        self, 
        question: str, 
        context: str, 
        model_name: Optional[str] = None
    ) -> str:
        """
        Generate a response with document context (for RAG)
        
        Args:
            question: User question
            context: Relevant document context
            model_name: Model to use
            
        Returns:
            Generated response text
        """
        
        # Create enhanced prompt with context
        prompt = f"""You are a helpful AI assistant that answers questions based on the provided context.

**Guidelines:**
- Answer only based on the information in the context
- If the context doesn't contain relevant information, say so clearly
- Be accurate and cite specific parts of the context when relevant
- Use markdown formatting for better readability (**bold**, *italic*, lists, etc.)
- Provide comprehensive but concise answers
- If asked about something not in the context, explain that the information isn't available in the provided documents

**Context:**
{context}

**Question:** {question}

**Answer:**"""
        
        return self.generate_response(prompt, model_name=model_name, temperature=0.2)
    
    def test_connection(self) -> bool:
        """Test the Gemini API connection"""
        try:
            test_prompt = "Hello! Please respond with 'Connection successful' to confirm the API is working."
            response = self.generate_response(test_prompt, max_tokens=50)
            
            # Check if response indicates success
            return ("successful" in response.lower() or 
                   "working" in response.lower() or
                   len(response) > 10)  # Any substantial response indicates success
                
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get available Gemini models"""
        return [
            "gemini-1.5-flash",    # Current default
            "gemini-1.5-pro",      # More capable
            "gemini-1.0-pro"       # Stable version
        ]
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to a different Gemini model"""
        available_models = self.get_available_models()
        if model_name in available_models:
            self.model_name = model_name
            logger.info(f"Switched Gemini model to: {model_name}")
            return True
        else:
            logger.error(f"Invalid model name: {model_name}. Available: {available_models}")
            return False


# Global instance - will be initialized when API key is available
gemini_service = None

def get_gemini_service() -> Optional[GeminiService]:
    """Get or create Gemini service instance"""
    global gemini_service
    
    if gemini_service is None:
        try:
            gemini_service = GeminiService()
            logger.info("Gemini service initialized successfully with REST API")
        except ValueError as e:
            logger.warning(f"Gemini service not available: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            return None
    
    return gemini_service

def is_gemini_available() -> bool:
    """Check if Gemini service is available"""
    return get_gemini_service() is not None
