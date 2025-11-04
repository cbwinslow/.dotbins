"""OpenRouter SDK for Python."""

from .openrouter import (
    OpenRouterClient,
    ChatMessage,
    ModelInfo,
    quick_chat,
    web_search_chat,
)

__version__ = "0.1.0"
__all__ = [
    "OpenRouterClient",
    "ChatMessage",
    "ModelInfo",
    "quick_chat",
    "web_search_chat",
]
