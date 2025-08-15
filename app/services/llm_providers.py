import os
from typing import List
from pydantic import BaseModel
import google.generativeai as genai
import openai
import cohere

# Configure API clients
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
cohere_client = cohere.Client(os.getenv("COHERE_API_KEY"))

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
        super().__init__("gemini", 1)  # Priority 1 (highest)
        self.model = genai.GenerativeModel("gemini-2.0-flash-lite")
    
    def generate(self, request: LLMRequest) -> str:
        prompt = f"Context: {request.context}\n\nQuestion: {request.query}\n\nAnswer:"
        response = self.model.generate_content(prompt)
        return response.text

class OpenAIProvider(LLMProvider):
    def __init__(self):
        super().__init__("openai", 2)  # Priority 2
    
    def generate(self, request: LLMRequest) -> str:
        messages = [
            {"role": "user", "content": f"Context: {request.context}\n\nQuestion: {request.query}"}
        ]
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.2,
            max_tokens=500
        )
        return response.choices[0].message.content

class CohereProvider(LLMProvider):
    def __init__(self):
        super().__init__("cohere", 3)  # Priority 3
    
    def generate(self, request: LLMRequest) -> str:
        prompt = f"Context: {request.context}\n\nQuestion: {request.query}\n\nAnswer:"
        response = cohere_client.generate(
            model="command-r",
            prompt=prompt,
            max_tokens=400,
            temperature=0.2
        )
        return response.generations[0].text

# Initialize providers in priority order
PROVIDERS: List[LLMProvider] = [
    GeminiProvider(),
    OpenAIProvider(), 
    CohereProvider()
]

def generate_with_fallback(request: LLMRequest) -> dict:
    """Try providers in order until one succeeds"""
    last_error = None
    
    for provider in PROVIDERS:
        try:
            print(f"Trying {provider.name}...")
            response = provider.generate(request)
            return {
                "answer": response,
                "provider_used": provider.name,
                "success": True
            }
        except Exception as e:
            print(f"{provider.name} failed: {str(e)}")
            last_error = str(e)
            continue
    
    # If all providers fail
    return {
        "answer": "Sorry, all AI providers are currently unavailable.",
        "provider_used": "none",
        "success": False,
        "error": last_error
    }
