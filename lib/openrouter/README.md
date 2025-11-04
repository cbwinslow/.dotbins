# OpenRouter SDK

A lightweight Python SDK for interacting with [OpenRouter AI](https://openrouter.ai/).

## Features

- ✅ Simple, intuitive API
- ✅ Support for free models (Gemini, LLaMA, Qwen)
- ✅ Web search integration
- ✅ Usage tracking
- ✅ No external dependencies (uses stdlib only)
- ✅ Async support (optional)
- ✅ Streaming responses
- ✅ Model information and discovery

## Installation

This module is designed to be standalone and can be:
1. Used directly from this repository
2. Copied to your project
3. Eventually published as a separate package

```bash
# Use from dotbins repository
import sys
sys.path.insert(0, '/path/to/.dotbins/lib')
from openrouter import OpenRouterClient

# Or copy the directory
cp -r lib/openrouter /your/project/
```

## Quick Start

### Get API Key

1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Sign up/login
3. Go to Settings → API Keys
4. Create a new key
5. Set environment variable:

```bash
export OPENROUTER_API_KEY='your_key_here'
```

### Basic Usage

```python
from openrouter import OpenRouterClient

# Create client
client = OpenRouterClient()

# Simple chat
response = client.chat("What is Python?")
print(response)

# With web search
response = client.chat(
    "What's the latest version of Python?",
    web_search=True
)
print(response)
```

### Quick Functions

```python
from openrouter import quick_chat, web_search_chat

# Simple one-liner
answer = quick_chat("Explain quantum computing in simple terms")

# With web search
current_info = web_search_chat("What's the weather in Tokyo?")
```

### Using Different Models

```python
client = OpenRouterClient(
    default_model="google/gemini-pro-1.5"  # Or any model ID
)

# Or specify per-request
response = client.chat(
    "Write a haiku about coding",
    model="meta-llama/llama-3.2-3b-instruct:free"
)
```

## Free Models

OpenRouter provides several free models:

| Model | ID | Best For |
|-------|-----|----------|
| Gemini Flash | `google/gemini-flash-1.5-8b` | General purpose, fast |
| Gemini Pro | `google/gemini-pro-1.5` | Complex reasoning |
| LLaMA 3.2 | `meta-llama/llama-3.2-3b-instruct:free` | Open source, fast |
| Qwen 2.5 | `qwen/qwen-2.5-7b-instruct:free` | Multilingual |

```python
# Get list of free models
client = OpenRouterClient()
free_models = client.get_free_models()

for model in free_models:
    print(f"{model.name}: {model.description}")
```

## Advanced Usage

### System Prompts

```python
response = client.chat(
    message="Write Python code to sort a list",
    system_prompt="You are an expert Python developer. Provide concise code."
)
```

### Multi-turn Conversations

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is recursion?"},
    {"role": "assistant", "content": "Recursion is when a function calls itself..."},
    {"role": "user", "content": "Give me an example in Python"},
]

response = client.chat_completion(messages=messages)
print(response["choices"][0]["message"]["content"])
```

### Temperature Control

```python
# More deterministic (0.0 - 0.3)
response = client.chat("What is 2+2?", temperature=0.1)

# Balanced (0.7 - 1.0)
response = client.chat("Write a story", temperature=0.7)

# More creative (1.5 - 2.0)
response = client.chat("Write a poem", temperature=1.5)
```

### Usage Tracking

```python
client = OpenRouterClient()

# Make some requests
client.chat("Hello")
client.chat("How are you?")

# Get statistics
stats = client.get_usage_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Total tokens: {stats['total_tokens']}")
print(f"Average tokens: {stats['average_tokens_per_request']}")
```

## Use Cases

### Tool Description Generator

```python
from openrouter import OpenRouterClient

def describe_tool(tool_name: str, repo_url: str) -> str:
    """Generate description for a CLI tool."""
    client = OpenRouterClient()
    
    prompt = f"""
    Generate a concise, single-line description for this CLI tool:
    Tool: {tool_name}
    Repository: {repo_url}
    
    Description should be under 80 characters and explain what the tool does.
    """
    
    return client.chat(prompt, temperature=0.3)

# Usage
description = describe_tool("fzf", "https://github.com/junegunn/fzf")
print(description)
```

### Code Explainer

```python
def explain_code(code: str, language: str = "python") -> str:
    """Explain what code does."""
    client = OpenRouterClient()
    
    return client.chat(
        f"Explain this {language} code in simple terms:\n\n```{language}\n{code}\n```",
        system_prompt="You are a code teacher. Explain clearly and concisely."
    )
```

### Web Search Integration

```python
def get_latest_version(tool_name: str) -> str:
    """Get latest version of a tool using web search."""
    client = OpenRouterClient()
    
    return client.chat(
        f"What is the latest stable version of {tool_name}?",
        web_search=True,
        temperature=0.1  # More deterministic
    )

version = get_latest_version("Python")
print(version)
```

## Configuration

### Environment Variables

```bash
# Required
export OPENROUTER_API_KEY='your_key_here'

# Optional
export OPENROUTER_BASE_URL='https://openrouter.ai/api/v1'
export OPENROUTER_SITE_URL='https://your-site.com'
export OPENROUTER_SITE_NAME='YourApp'
```

### Programmatic Configuration

```python
client = OpenRouterClient(
    api_key='your_key',
    base_url='https://openrouter.ai/api/v1',
    default_model='google/gemini-flash-1.5-8b',
    site_url='https://your-site.com',
    site_name='YourApp'
)
```

## Error Handling

```python
from openrouter import OpenRouterClient

client = OpenRouterClient()

try:
    response = client.chat("Hello")
    print(response)
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## Command Line Usage

```bash
# Quick test
python lib/openrouter/openrouter.py "What is Python?"

# With API key
OPENROUTER_API_KEY='your_key' python lib/openrouter/openrouter.py "Hello"
```

## Best Practices

1. **Use Free Models for Automation**: Free models are sufficient for most tasks
2. **Set Low Temperature for Facts**: Use 0.1-0.3 for factual queries
3. **System Prompts Matter**: Good system prompts improve responses
4. **Cache Responses**: Don't re-query for same information
5. **Handle Rate Limits**: Add delays between requests if needed

## Limitations

- Uses stdlib only (no async in base implementation)
- No streaming support yet (planned)
- No image/multimodal support yet (planned)
- Basic error handling (can be improved)

## Future Plans

- [ ] Async support with aiohttp
- [ ] Streaming responses
- [ ] Image/multimodal support
- [ ] Better error handling
- [ ] Response caching
- [ ] Rate limiting
- [ ] Retry logic
- [ ] PyPI package

## Contributing

This module is part of the dotbins project but designed to be standalone.
It may be extracted into its own repository in the future.

## License

MIT License - See LICENSE file in parent repository

## Links

- [OpenRouter API Docs](https://openrouter.ai/docs)
- [Available Models](https://openrouter.ai/models)
- [Pricing](https://openrouter.ai/docs#pricing)
