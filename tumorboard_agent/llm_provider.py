"""
Pluggable LLM backend, used only to phrase rationale narratives.

The *decisions* (recommendation category, confidence) are always made by
deterministic, auditable logic elsewhere in the codebase -- this provider
never decides anything, it only writes prose describing a decision that has
already been made. That separation is intentional: it keeps the clinically
meaningful part of the system testable and free of generation risk, while
still demonstrating a real, swappable LLM integration point.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        ...


class TemplateProvider(LLMProvider):
    """No external calls, no API key. Deterministic and always available."""

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return user_prompt


class AnthropicProvider(LLMProvider):
    def __init__(self, model: str = "claude-sonnet-4-6", api_key: str | None = None):
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        self._model = model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        resp = self._client.messages.create(
            model=self._model,
            max_tokens=600,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return "".join(
            block.text for block in resp.content if getattr(block, "type", "") == "text"
        )


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None):
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self._model = model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content or ""


def get_llm_provider(
    provider: str | None = None, api_key: str | None = None
) -> LLMProvider:
    """Select an LLM backend.

    If `provider` and `api_key` are given (e.g. pasted in the app UI), use
    them directly. Otherwise fall back to environment variables, and finally
    to the offline template provider. A pasted key is used only to build the
    client; it is never written to disk or logged by this code.
    """

    if provider == "anthropic" and api_key:
        try:
            return AnthropicProvider(api_key=api_key)
        except Exception:
            return TemplateProvider()
    if provider == "openai" and api_key:
        try:
            return OpenAIProvider(api_key=api_key)
        except Exception:
            return TemplateProvider()

    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            return AnthropicProvider()
        except Exception:
            pass
    if os.getenv("OPENAI_API_KEY"):
        try:
            return OpenAIProvider()
        except Exception:
            pass
    return TemplateProvider()
