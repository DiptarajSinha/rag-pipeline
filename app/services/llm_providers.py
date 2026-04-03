from typing import List, Optional
import logging
import time
from google import genai
from google.genai import types
import openai
import cohere
from pydantic import BaseModel
from ..config import settings

logger = logging.getLogger("rag-pipeline.llm_providers")

# Initialize Gemini Client
gemini_client = None
if settings.GOOGLE_GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=settings.GOOGLE_GEMINI_API_KEY)

class LLMRequest(BaseModel):
    query: str
    context: str

class LLMProvider:
    def __init__(self, name: str, priority: int):
        self.name = name
        self.priority = priority
    
    def generate(self, request: LLMRequest) -> str:
        raise NotImplementedError

class GeminiProvider(LLMProvider):
    def __init__(self):
        super().__init__("gemini", 1)
        # Upgrading to Gemini 3 Flash for elite speed and fresh quota
        self.model_id = "gemini-3-flash"
    
    def generate(self, request: LLMRequest) -> str:
        if not gemini_client:
            raise ValueError("Gemini API key not configured")
            
        system_prompt = (
            "You are a professional RAG assistant. "
            "Use ONLY the following context to answer the user's question. "
            "If the answer is not in the context, say 'I cannot find the answer in the documents provided.' "
            "Keep your answer concise and accurate. DO NOT repeat the context itself."
        )
        
        user_prompt = f"CONTEXT:\n{request.context}\n\nQUESTION: {request.query}\n\nANSWER:"
        
        # Retry loop for 429s
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = gemini_client.models.generate_content(
                    model=self.model_id,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.1,
                        max_output_tokens=1000
                    )
                )
                if not response.text:
                    raise ValueError("Empty response from AI")
                return response.text
            except Exception as e:
                error_str = str(e)
                if ("429" in error_str or "quota" in error_str.lower() or "RESOURCE_EXHAUSTED" in error_str) and attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    logger.warning(f"Rate Limit hit. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                raise e

class OpenAIProvider(LLMProvider):
    def __init__(self):
        super().__init__("openai", 2)
        self._client = None
    
    @property
    def client(self):
        if self._client is None and settings.OPENAI_API_KEY:
            self._client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client
    
    def generate(self, request: LLMRequest) -> str:
        if not self.client:
            raise ValueError("OpenAI API key not configured")
            
        system_msg = "You are a helpful assistant. Use the provided context to answer the question concisely."
        user_msg = f"Context: {request.context}\n\nQuestion: {request.query}"
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.2,
            max_tokens=500
        )
        return response.choices[0].message.content

class CohereProvider(LLMProvider):
    def __init__(self):
        super().__init__("cohere", 3)
        self._client = None
        
    @property
    def client(self):
        if self._client is None and settings.COHERE_API_KEY:
            self._client = cohere.Client(api_key=settings.COHERE_API_KEY)
        return self._client
    
    def generate(self, request: LLMRequest) -> str:
        if not self.client:
            raise ValueError("Cohere API key not configured")
            
        prompt = f"Context: {request.context}\nQuestion: {request.query}\nAnswer:"
        response = self.client.generate(
            model="command-r",
            prompt=prompt,
            max_tokens=400,
            temperature=0.2
        )
        return response.generations[0].text

# Initialize providers
AVAILABLE_PROVIDERS: List[LLMProvider] = []
if settings.GOOGLE_GEMINI_API_KEY:
    AVAILABLE_PROVIDERS.append(GeminiProvider())
if settings.OPENAI_API_KEY:
    AVAILABLE_PROVIDERS.append(OpenAIProvider())
if settings.COHERE_API_KEY:
    AVAILABLE_PROVIDERS.append(CohereProvider())

def generate_with_fallback(request: LLMRequest) -> dict:
    """Try providers in order until one succeeds"""
    last_error = "No providers configured"
    
    for provider in AVAILABLE_PROVIDERS:
        try:
            logger.info(f"Trying LLM provider: {provider.name}")
            response = provider.generate(request)
            return {
                "answer": response,
                "provider_used": provider.name,
                "success": True
            }
        except Exception as e:
            error_str = str(e)
            logger.error(f"Provider {provider.name} failed: {error_str}")
            
            if "429" in error_str or "quota" in error_str.lower():
                last_error = f"Rate limit reached for {provider.name}. Please wait for a fresh quota bucket."
            else:
                last_error = error_str
            continue
    
    return {
        "answer": f"AI Error: {last_error}",
        "provider_used": "none",
        "success": False,
        "error": last_error
    }
