# D:/AI/ai-scout/browser-use/backend/services/llm_factory.py

from browser_use.llm import ChatAnthropic, ChatOllama, ChatOpenAI

from backend.models.llm_config import LLMConfig


def create_llm(config: LLMConfig):
	"""根据配置创建 LLM 实例"""
	provider = config.provider

	if provider == "deepseek":
		return ChatOpenAI(
			model=config.model,
			api_key=config.api_key or "",
			base_url=config.base_url or "https://api.deepseek.com",
		)

	elif provider == "openai":
		return ChatOpenAI(
			model=config.model,
			api_key=config.api_key or "",
			base_url=config.base_url or "https://api.openai.com/v1",
		)

	elif provider == "anthropic":
		return ChatAnthropic(
			model=config.model,
			api_key=config.api_key or "",
			base_url=config.base_url,
		)

	elif provider == "ollama":
		return ChatOllama(
			model=config.model,
			base_url=config.base_url or "http://localhost:11434",
		)

	elif provider == "openai_compatible":
		return ChatOpenAI(
			model=config.model,
			api_key=config.api_key or "dummy",
			base_url=config.base_url,
		)

	else:
		raise ValueError(f"Unsupported provider: {provider}")
