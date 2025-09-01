import requests
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.hf_token = os.getenv("HUGGING_FACE_TOKEN", "")
        # HuggingFace model URL (only used if USE_LOCAL_LLM=false)
        self.model_url = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
        
        # Prefer local LLM by default, or if explicitly set
        self.use_local = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"  # Default to true
        self.local_url = "http://localhost:11434/api/generate"
    
    def generate_answer(self, question: str, context: str) -> str:
        """Generate answer using retrieved context"""
        if not context or context.strip() == "":
            return "I don't have any document content to work with. Please make sure you've uploaded a PDF document first."
        
        prompt = f"""You are a helpful AI assistant. Answer the question based on the provided context from a document. 
If the context doesn't contain enough information to answer the question, provide what information you can find and mention what's missing.

Context from document:
{context}

Question: {question}

Answer:"""
        return self._call_local_llm(prompt) if self.use_local else self._call_huggingface_api(prompt)
    
    def _call_huggingface_api(self, prompt: str) -> str:
        """Call Hugging Face API"""
        if not self.hf_token:
            # Provide a simple fallback response when no token is available
            return f"Based on the provided context, I can help answer questions about your document. However, for enhanced AI responses, please set your HUGGING_FACE_TOKEN environment variable. For now, here's the relevant context that might answer your question: {prompt[-200:]}"
        
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        data = {"inputs": prompt, "parameters": {"max_new_tokens": 256, "temperature": 0.7}}

        try:
            response = requests.post(self.model_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "No response generated.")
            elif isinstance(result, dict) and "generated_text" in result:
                return result["generated_text"]
            return "No response generated."
            
        except requests.exceptions.RequestException as e:
            # Provide fallback response on API error
            return f"I found relevant information in your document, but there was an issue with the AI service: {str(e)}. Here's the context that might help: {prompt[-300:]}"
    
    def _call_local_llm(self, prompt: str) -> str:
        """Call local Ollama API"""
        # Try different models in order of preference
        models_to_try = ["llama3.2:1b", "llama3.2:3b", "llama3", "llama2"]
        
        for model in models_to_try:
            try:
                print(f"Trying model: {model}")
                data = {"model": model, "prompt": prompt, "stream": False}
                
                # Increase timeout to 120 seconds for local LLM
                response = requests.post(self.local_url, json=data, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    generated_response = result.get("response", "No response generated.")
                    print(f"Successfully got response from {model}")
                    return generated_response
                else:
                    print(f"Model {model} returned status {response.status_code}")
                    continue
                
            except requests.exceptions.Timeout:
                print(f"Timeout with model {model}, trying next...")
                continue
            except requests.exceptions.RequestException as e:
                print(f"Request error with model {model}: {e}")
                continue  # Try next model
        
        # If all models failed, return a helpful error message
        return "I apologize, but I'm having trouble connecting to the AI service right now. The service might be loading or busy. Please try again in a moment."


# Global LLM service instance
llm_service = LLMService()
