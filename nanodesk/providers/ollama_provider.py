"""Ollama provider for local LLM support.

This is a custom provider for Nanodesk to support Ollama local models.
When upstream nanobot merges PR #133, this can be replaced.

Usage:
    Set in config.json:
    {
      "agents": {
        "defaults": {
          "model": "qwen2.5:latest",
          "provider": "ollama"
        }
      },
      "providers": {
        "ollama": {
          "apiKey": "not-needed",
          "apiBase": "http://localhost:11434"
        }
      }
    }
"""

from __future__ import annotations

import json
from typing import Any

import httpx
from nanobot.providers.base import LLMProvider, LLMResponse, ToolCallRequest


class OllamaProvider(LLMProvider):
    """Ollama provider for local LLM inference.
    
    Uses Ollama's OpenAI-compatible API endpoint (/v1/chat/completions)
    which is available in Ollama 0.3.0+.
    """
    
    def __init__(
        self,
        api_key: str | None = None,
        api_base: str | None = "http://localhost:11434",
        default_model: str = "qwen2.5:latest",
        extra_headers: dict[str, str] | None = None,
        provider_name: str | None = None,
    ):
        super().__init__(api_key, api_base)
        self.default_model = default_model
        self.extra_headers = extra_headers or {}
        self.provider_name = provider_name or "ollama"
        
        # Ensure api_base has /v1 suffix for OpenAI-compatible endpoint
        if self.api_base and not self.api_base.rstrip("/").endswith("/v1"):
            self.api_base = self.api_base.rstrip("/") + "/v1"
    
    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Send a chat completion request to Ollama."""
        model = model or self.default_model
        
        # Remove ollama/ prefix if present (we handle it internally)
        if model.startswith("ollama/"):
            model = model[7:]
        
        # Build request body for Ollama's OpenAI-compatible API
        body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if tools:
            body["tools"] = tools
        
        print(f"[DEBUG] Ollama request to {self.api_base}/chat/completions")
        print(f"[DEBUG] Model: {model}, Messages count: {len(messages)}")
        
        # 打印原始 prompt 用于调试
        print(f"[DEBUG] === RAW MESSAGES ===")
        for i, msg in enumerate(messages):
            content = msg.get('content', '')[:200]  # 只打印前200字符
            print(f"[DEBUG] [{i}] {msg.get('role', 'unknown')}: {content}...")
        print(f"[DEBUG] === END MESSAGES ===")
        
        # 估算 tokens（粗略：1 token ≈ 4 chars）
        total_chars = sum(len(str(m.get('content', ''))) for m in messages)
        print(f"[DEBUG] Total chars: {total_chars}, Est tokens: {total_chars // 4}")
        
        # Make request to Ollama's OpenAI-compatible endpoint
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    json=body,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                        **self.extra_headers,
                    },
                    timeout=120.0,
                )
                print(f"[DEBUG] Ollama response status: {response.status_code}")
                response.raise_for_status()
                data = response.json()
                print(f"[DEBUG] Ollama response: {str(data)[:500]}")
                return self._parse_response(data)
            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
                print(f"[ERROR] Ollama HTTP error: {error_msg}")
                return LLMResponse(
                    content=f"Error calling Ollama: {error_msg}",
                    finish_reason="error",
                )
            except Exception as e:
                import traceback
                print(f"[ERROR] Ollama exception: {str(e)}")
                print(f"[ERROR] Traceback: {traceback.format_exc()}")
                return LLMResponse(
                    content=f"Error calling Ollama: {str(e)}",
                    finish_reason="error",
                )
    
    def _parse_response(self, data: dict[str, Any]) -> LLMResponse:
        """Parse Ollama response into standard format."""
        if "choices" not in data or not data["choices"]:
            return LLMResponse(
                content="Error: Empty response from Ollama",
                finish_reason="error",
            )
        
        choice = data["choices"][0]
        message = choice.get("message", {})
        
        # Parse tool calls if present
        tool_calls = []
        raw_tool_calls = message.get("tool_calls")
        if raw_tool_calls:
            for tc in raw_tool_calls:
                if "function" in tc:
                    func = tc["function"]
                    tool_calls.append(ToolCallRequest(
                        id=tc.get("id", ""),
                        name=func.get("name", ""),
                        arguments=func.get("arguments", {}),
                    ))
        
        # Get usage info
        usage = data.get("usage", {})
        usage_dict = {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        } if usage else {}
        
        return LLMResponse(
            content=message.get("content", ""),
            tool_calls=tool_calls,
            finish_reason=choice.get("finish_reason", "stop"),
            usage=usage_dict,
        )
    
    def get_default_model(self) -> str:
        """Get the default model."""
        return self.default_model
