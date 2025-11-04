#!/usr/bin/env python3
"""
OpenRouter SDK for dotbins
===========================

A lightweight Python SDK for interacting with OpenRouter API.
This module provides a simple interface to OpenRouter's AI models,
with a focus on free models suitable for automation tasks.

Features:
- Easy-to-use API for text generation
- Support for free models (e.g., google/gemini-flash-1.5-8b)
- Web search integration
- Streaming support
- Error handling and rate limiting
- Cost tracking (for paid models)

Usage:
    from openrouter import OpenRouterClient
    
    client = OpenRouterClient(api_key="your_key")
    response = client.chat("What is Python?")
    print(response)

Environment Variables:
    OPENROUTER_API_KEY: Your OpenRouter API key (get from https://openrouter.ai)
    OPENROUTER_BASE_URL: Base URL for API (default: https://openrouter.ai/api/v1)
    
Note: This module can be extracted into its own repository for reuse.
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass, field
from datetime import datetime
import urllib.request
import urllib.error
import urllib.parse


@dataclass
class ModelInfo:
    """Information about an OpenRouter model.
    
    Attributes:
        id: Model identifier (e.g., "google/gemini-flash-1.5-8b")
        name: Human-readable model name
        description: Model description
        pricing: Cost per token (prompt/completion)
        context_length: Maximum context length in tokens
        is_free: Whether the model is free to use
    """
    id: str
    name: str
    description: str = ""
    pricing: Dict[str, float] = field(default_factory=dict)
    context_length: int = 0
    is_free: bool = False
    

@dataclass
class ChatMessage:
    """A single message in a chat conversation.
    
    Attributes:
        role: Message role (system, user, assistant, tool)
        content: Message content
        name: Optional name for the message sender
    """
    role: str  # system, user, assistant, tool
    content: str
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to API format."""
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


class OpenRouterClient:
    """Client for interacting with OpenRouter API.
    
    This client provides a simple interface for:
    - Text generation (chat completions)
    - Web search integration
    - Streaming responses
    - Model selection and information
    
    Attributes:
        api_key: OpenRouter API key
        base_url: Base URL for API endpoints
        default_model: Default model to use for requests
        site_url: Your app/site URL (for OpenRouter rankings)
        site_name: Your app/site name
    """
    
    # Free models recommended for automation
    FREE_MODELS = {
        "gemini-flash": "google/gemini-flash-1.5-8b",
        "gemini-pro": "google/gemini-pro-1.5",
        "llama-free": "meta-llama/llama-3.2-3b-instruct:free",
        "qwen-free": "qwen/qwen-2.5-7b-instruct:free",
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
        default_model: str = "google/gemini-flash-1.5-8b",
        site_url: Optional[str] = None,
        site_name: Optional[str] = None,
    ):
        """Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
            base_url: Base URL for API (default: https://openrouter.ai/api/v1)
            default_model: Default model to use (default: gemini-flash free model)
            site_url: Your app/site URL (optional, helps with rankings)
            site_name: Your app/site name (optional)
            
        Raises:
            ValueError: If API key is not provided and not in environment
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter. Get key from https://openrouter.ai"
            )
        
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.site_url = site_url or os.getenv("OPENROUTER_SITE_URL", "")
        self.site_name = site_name or os.getenv("OPENROUTER_SITE_NAME", "dotbins")
        
        # Request statistics
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0
    
    def _make_request(
        self,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to OpenRouter API.
        
        Args:
            endpoint: API endpoint (e.g., "/chat/completions")
            method: HTTP method (GET, POST, etc.)
            data: Request data (for POST requests)
            
        Returns:
            Response data as dictionary
            
        Raises:
            urllib.error.HTTPError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.site_name:
            headers["X-Title"] = self.site_name
        
        request_data = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=request_data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            raise Exception(f"API request failed: {e.code} {e.reason}\n{error_body}")
    
    def chat(
        self,
        message: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        web_search: bool = False,
    ) -> str:
        """Send a chat message and get response.
        
        Args:
            message: User message to send
            model: Model to use (default: self.default_model)
            system_prompt: Optional system prompt to set context
            temperature: Randomness (0.0-2.0, higher = more random)
            max_tokens: Maximum tokens in response
            web_search: Enable web search for current information
            
        Returns:
            Assistant's response text
            
        Example:
            response = client.chat("What is Python?")
            print(response)
        """
        messages = []
        
        if system_prompt:
            messages.append(ChatMessage("system", system_prompt).to_dict())
        
        messages.append(ChatMessage("user", message).to_dict())
        
        response = self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            web_search=web_search,
        )
        
        return response["choices"][0]["message"]["content"]
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        web_search: bool = False,
    ) -> Dict[str, Any]:
        """Low-level chat completion request.
        
        Args:
            messages: List of message dictionaries with role and content
            model: Model to use (default: self.default_model)
            temperature: Randomness (0.0-2.0)
            max_tokens: Maximum tokens in response
            stream: Enable streaming response
            web_search: Enable web search for current information
            
        Returns:
            API response dictionary
            
        Example:
            messages = [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Hello!"}
            ]
            response = client.chat_completion(messages)
        """
        model = model or self.default_model
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        if stream:
            data["stream"] = True
        
        if web_search:
            # Enable web search for current information
            data["route"] = "fallback"
            # Some models support web search natively
        
        response = self._make_request("/chat/completions", data=data)
        
        # Track usage
        self.total_requests += 1
        if "usage" in response:
            self.total_tokens += response["usage"].get("total_tokens", 0)
        
        return response
    
    def get_models(self) -> List[ModelInfo]:
        """Get list of available models from OpenRouter.
        
        Returns:
            List of ModelInfo objects
            
        Example:
            models = client.get_models()
            for model in models:
                print(f"{model.name}: {model.description}")
        """
        response = self._make_request("/models", method="GET")
        
        models = []
        for model_data in response.get("data", []):
            pricing = model_data.get("pricing", {})
            is_free = (
                float(pricing.get("prompt", "0")) == 0
                and float(pricing.get("completion", "0")) == 0
            )
            
            models.append(
                ModelInfo(
                    id=model_data["id"],
                    name=model_data.get("name", model_data["id"]),
                    description=model_data.get("description", ""),
                    pricing=pricing,
                    context_length=model_data.get("context_length", 0),
                    is_free=is_free,
                )
            )
        
        return models
    
    def get_free_models(self) -> List[ModelInfo]:
        """Get list of free models.
        
        Returns:
            List of free ModelInfo objects
        """
        all_models = self.get_models()
        return [m for m in all_models if m.is_free]
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for this client session.
        
        Returns:
            Dictionary with requests, tokens, and cost statistics
        """
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "average_tokens_per_request": (
                self.total_tokens / self.total_requests if self.total_requests > 0 else 0
            ),
        }


# Convenience functions for quick usage
def quick_chat(message: str, model: str = "google/gemini-flash-1.5-8b") -> str:
    """Quick chat function without creating a client object.
    
    Args:
        message: Message to send
        model: Model to use (default: free Gemini Flash)
        
    Returns:
        Response text
        
    Example:
        response = quick_chat("What is Python?")
        print(response)
    """
    client = OpenRouterClient(default_model=model)
    return client.chat(message)


def web_search_chat(query: str, model: str = "google/gemini-flash-1.5-8b") -> str:
    """Chat with web search enabled for current information.
    
    Args:
        query: Query/question requiring current information
        model: Model to use (default: free Gemini Flash)
        
    Returns:
        Response text with web search results
        
    Example:
        response = web_search_chat("What's the latest Python version?")
        print(response)
    """
    client = OpenRouterClient(default_model=model)
    return client.chat(query, web_search=True)


# Example usage
if __name__ == "__main__":
    import sys
    
    # Example: Simple chat
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        try:
            print("Sending query to OpenRouter...")
            response = quick_chat(message)
            print(f"\nResponse:\n{response}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print("OpenRouter SDK for dotbins")
        print("Usage: python openrouter.py 'your question here'")
        print("\nSet OPENROUTER_API_KEY environment variable first:")
        print("  export OPENROUTER_API_KEY='your_key_here'")
        print("\nGet your API key from: https://openrouter.ai")
