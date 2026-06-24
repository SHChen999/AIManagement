"""LLM 服务：支持多种大模型（Qianwen、DeepSeek）"""
import os
import base64
import httpx
import logging
from typing import Optional, AsyncIterator
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMService:
    """统一的大模型服务接口"""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider or settings.llm_provider
        self.model = model

    async def think(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """同步调用，返回完整响应"""
        if self.provider == "qianwen":
            return await self._call_qianwen(prompt, system_prompt)
        elif self.provider == "deepseek":
            return await self._call_deepseek(prompt, system_prompt)
        else:
            raise ValueError(f"不支持的 LLM provider: {self.provider}")

    async def think_stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncIterator[str]:
        """流式调用，yield 每个 token"""
        if self.provider == "qianwen":
            async for chunk in self._call_qianwen_stream(prompt, system_prompt):
                yield chunk
        elif self.provider == "deepseek":
            async for chunk in self._call_deepseek_stream(prompt, system_prompt):
                yield chunk
        else:
            raise ValueError(f"不支持的 LLM provider: {self.provider}")

    # ==================== Qianwen (通义千问) ====================
    async def _call_qianwen(self, prompt: str, system_prompt: Optional[str]) -> str:
        """调用阿里云通义千问 API"""
        api_key = settings.qianwen_api_key
        if not api_key:
            raise ValueError("请在 .env 中配置 QIANWEN_API_KEY")

        model = self.model or "qwen-turbo"
        url = f"https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                url,
                json={"model": model, "messages": messages},
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def _call_qianwen_stream(self, prompt: str, system_prompt: Optional[str]) -> AsyncIterator[str]:
        """Qianwen 流式调用"""
        api_key = settings.qianwen_api_key
        if not api_key:
            raise ValueError("请在 .env 中配置 QIANWEN_API_KEY")

        model = self.model or "qwen-turbo"
        url = f"https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST", url,
                json={"model": model, "messages": messages, "stream": True},
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data:"):
                        import json
                        try:
                            chunk = json.loads(line[5:])
                            if chunk.get("choices", [{}])[0].get("delta", {}).get("content"):
                                yield chunk["choices"][0]["delta"]["content"]
                        except:
                            pass

    # ==================== DeepSeek ====================
    async def _call_deepseek(self, prompt: str, system_prompt: Optional[str]) -> str:
        """调用 DeepSeek API"""
        api_key = settings.deepseek_api_key
        if not api_key:
            raise ValueError("请在 .env 中配置 DEEPSEEK_API_KEY")

        model = self.model or "deepseek-chat"
        url = "https://api.deepseek.com/v1/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                url,
                json={"model": model, "messages": messages},
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def _call_deepseek_stream(self, prompt: str, system_prompt: Optional[str]) -> AsyncIterator[str]:
        """DeepSeek 流式调用"""
        api_key = settings.deepseek_api_key
        if not api_key:
            raise ValueError("请在 .env 中配置 DEEPSEEK_API_KEY")

        model = self.model or "deepseek-chat"
        url = "https://api.deepseek.com/v1/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST", url,
                json={"model": model, "messages": messages, "stream": True},
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data:"):
                        import json
                        try:
                            chunk = json.loads(line[5:])
                            if chunk.get("choices", [{}])[0].get("delta", {}).get("content"):
                                yield chunk["choices"][0]["delta"]["content"]
                        except:
                            pass


# 全局实例
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取 LLM 服务单例"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def init_llm_service(provider: str, model: Optional[str] = None) -> LLMService:
    """初始化 LLM 服务"""
    global _llm_service
    _llm_service = LLMService(provider=provider, model=model)
    return _llm_service
