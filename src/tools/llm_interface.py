"""
LLM interface for interacting with OpenAI models
Provides a simple wrapper for chat completions with AutoGen compatibility
"""

from typing import List, Dict, Optional, Any
from openai import OpenAI

from src.config.settings import settings


class LLMInterface:
    """Interface for OpenAI LLM interactions"""

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        verbose: bool = False
    ):
        """
        Initialize LLM interface

        Args:
            model: Model name (defaults to settings.OPENAI_MODEL)
            temperature: Sampling temperature (defaults to settings.OPENAI_TEMPERATURE)
            verbose: Enable verbose logging
        """
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model or settings.OPENAI_MODEL
        self.temperature = temperature if temperature is not None else settings.OPENAI_TEMPERATURE
        self.verbose = verbose

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Get chat completion from OpenAI

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Override default model
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI API parameters

        Returns:
            Assistant's response content
        """
        model = model or self.model
        temperature = temperature if temperature is not None else self.temperature

        if self.verbose:
            print(f"  └─ Calling {model} (temp={temperature})")

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            content = response.choices[0].message.content

            if self.verbose:
                tokens_used = response.usage.total_tokens
                print(f"  └─ Response received ({tokens_used} tokens)")

            return content

        except Exception as e:
            if self.verbose:
                print(f"  └─ LLM error: {e}")
            raise

    def get_autogen_config(self) -> Dict[str, Any]:
        """
        Get configuration dict for AutoGen agents

        Returns:
            Configuration dict compatible with AutoGen's llm_config
        """
        return {
            "config_list": [
                {
                    "model": self.model,
                    "api_key": settings.OPENAI_API_KEY,
                    "temperature": self.temperature,
                }
            ],
            "timeout": settings.AUTOGEN_TIMEOUT,
        }

    def create_system_message(self, content: str) -> Dict[str, str]:
        """Create a system message dict"""
        return {"role": "system", "content": content}

    def create_user_message(self, content: str) -> Dict[str, str]:
        """Create a user message dict"""
        return {"role": "user", "content": content}

    def create_assistant_message(self, content: str) -> Dict[str, str]:
        """Create an assistant message dict"""
        return {"role": "assistant", "content": content}

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        Note: This is a rough estimate. For accurate counts, use tiktoken library.

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 characters per token
        return len(text) // 4


# Convenience function for quick LLM calls
def quick_llm_call(
    prompt: str,
    system_message: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    verbose: bool = False
) -> str:
    """
    Quick utility function for simple LLM calls

    Args:
        prompt: User prompt
        system_message: Optional system message
        model: Model to use
        temperature: Sampling temperature
        verbose: Enable verbose logging

    Returns:
        LLM response
    """
    llm = LLMInterface(model=model, temperature=temperature, verbose=verbose)

    messages = []
    if system_message:
        messages.append(llm.create_system_message(system_message))
    messages.append(llm.create_user_message(prompt))

    return llm.chat_completion(messages)
