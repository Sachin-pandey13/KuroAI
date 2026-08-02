# Creating Inference Providers

Inference Providers encapsulate calls to LLMs and Image Generation APIs.

```python
class CustomLLMProvider:
    def generate(self, prompt: str, **kwargs) -> str:
        # Connect to provider API and return completion
        return "Generated response"
```
