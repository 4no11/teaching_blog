# -*- coding: utf-8 -*-
"""
LangChain 兼容层 - 云端 API 集成

提供基于 LangChain 标准接口的 ChatModel 和 Embeddings 实现，
内部使用纯 HTTP 调用 OpenAI 兼容 API（如硅基流动），
避免 langchain-openai 原生包的底层依赖冲突。
"""

import logging
from typing import Any, Dict, List, Optional, Sequence
from langchain_core.messages import BaseMessage, AIMessageChunk, HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.embeddings import Embeddings
import requests

logger = logging.getLogger(__name__)


class CustomChatOpenAI(BaseChatModel):
    """
    基于 LangChain BaseChatModel 的自定义 OpenAI 兼容聊天模型
    
    使用纯 HTTP 调用 /v1/chat/completions 接口，
    支持 OpenAI、硅基流动、OpenRouter 等所有兼容 API。
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout: int = 120,
        **kwargs
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        super().__init__(**kwargs)
    
    @property
    def _llm_type(self) -> str:
        return "custom-openai-chat"
    
    @property
    def _identifying_params(self) -> Dict:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "base_url": self.base_url
        }
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """调用 OpenAI 兼容的 Chat Completions API"""
        
        api_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                api_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                api_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, AIMessageChunk):
                api_messages.append({"role": "assistant", "content": msg.content})
            else:
                api_messages.append({"role": "user", "content": msg.content})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": api_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        if stop:
            payload["stop"] = stop
        
        payload.update(kwargs)
        
        logger.debug(f"[CustomChatOpenAI] 调用 API, model={self.model}")
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        result = response.json()
        
        content = result["choices"][0]["message"]["content"]
        message = AIMessageChunk(content=content)
        generation = ChatGeneration(message=message)
        
        return ChatResult(generations=[generation])
    
    def bind(self, **kwargs):
        """支持链式绑定参数"""
        new_params = {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
        }
        new_params.update(kwargs)
        return self.__class__(**new_params)


class CustomOpenAIEmbeddings(Embeddings):
    """
    基于 LangChain Embeddings 接口的自定义 OpenAI 兼容嵌入模型
    
    使用纯 HTTP 调用 /v1/embeddings 接口，
    支持批量嵌入和文档嵌入。
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "text-embedding-ada-002",
        timeout: int = 60,
        chunk_size: int = 1000,
        **kwargs
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.chunk_size = chunk_size
        super().__init__(**kwargs)
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """调用 OpenAI 兼容的 Embeddings API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": texts
        }
        
        logger.debug(f"[CustomOpenAIEmbeddings] 调用 API, model={self.model}, count={len(texts)}")
        
        response = requests.post(
            f"{self.base_url}/embeddings",
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        result = response.json()
        
        sorted_results = sorted(result["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in sorted_results]
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入文档列表（批量）"""
        all_embeddings = []
        
        for i in range(0, len(texts), self.chunk_size):
            chunk = texts[i:i + self.chunk_size]
            embeddings = self._get_embeddings(chunk)
            all_embeddings.extend(embeddings)
            
            if i + self.chunk_size < len(texts):
                import time
                time.sleep(0.1)
        
        return all_embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """嵌入查询文本"""
        return self._get_embeddings([text])[0]


def create_langchain_llm(config: Dict) -> BaseChatModel:
    """
    工厂函数：根据配置创建 LangChain ChatModel
    """
    provider = config.get("provider", "openai").lower()
    
    if provider == "openai":
        openai_config = config.get("openai", {})
        return CustomChatOpenAI(
            api_key=openai_config.get("api_key", ""),
            base_url=openai_config.get("base_url", "https://api.openai.com/v1"),
            model=openai_config.get("llm_model", "gpt-3.5-turbo"),
            temperature=0.7,
            max_tokens=2048
        )
    
    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        ollama_config = config.get("ollama", {})
        return ChatOllama(
            base_url=ollama_config.get("base_url", "http://localhost:11434"),
            model=ollama_config.get("llm_model", "qwen2.5:7b"),
            temperature=0.7,
            num_ctx=4096
        )
    
    else:
        raise ValueError(f"不支持的 LLM 提供商: {provider}")


def create_langchain_embeddings(config: Dict) -> Embeddings:
    """
    工厂函数：根据配置创建 LangChain Embeddings
    """
    provider = config.get("provider", "openai").lower()
    
    if provider == "openai":
        openai_config = config.get("openai", {})
        return CustomOpenAIEmbeddings(
            api_key=openai_config.get("api_key", ""),
            base_url=openai_config.get("base_url", "https://api.openai.com/v1"),
            model=openai_config.get("embedding_model", "text-embedding-ada-002")
        )
    
    elif provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        ollama_config = config.get("ollama", {})
        return OllamaEmbeddings(
            base_url=ollama_config.get("base_url", "http://localhost:11434"),
            model=ollama_config.get("embedding_model", "nomic-embed-text")
        )
    
    else:
        raise ValueError(f"不支持的 Embedding 提供商: {provider}")
