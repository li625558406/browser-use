# D:/AI/ai-scout/browser-use/backend/utils/init_data.py

"""Initialize default data for the application."""

import asyncio

from backend.database import async_session_maker
from backend.models.llm_config import LLMConfig
from backend.models.prompt import Prompt
from backend.utils.logger import logger


DEFAULT_LLMS = [
    {
        "name": "DeepSeek 聊天",
        "provider": "deepseek",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 4096,
        "is_default": True,
    },
    {
        "name": "Ollama 本地模型",
        "provider": "ollama",
        "base_url": "http://localhost:11434",
        "model": "llama3.2",
        "temperature": 0.7,
        "max_tokens": 4096,
        "is_default": False,
    },
]

DEFAULT_PROMPTS = [
    {
        "name": "通用数据提取",
        "description": "从网页中提取结构化数据",
        "content": """你是一个数据提取助手。你的任务是从提供的网页内容中提取结构化信息。

请分析页面并提取：
1. 主标题/头条
2. 关键数据点（数字、日期、名称等）
3. 重要描述或摘要
4. 任何结构化数据（表格、列表等）

以 Markdown 格式输出提取的数据，使用清晰的章节标题。

目标网址：{{url}}
提取目标：{{target_data}}""",
        "category": "数据提取",
        "variables": ["url", "target_data"],
    },
    {
        "name": "商品信息抓取",
        "description": "从电商页面抓取商品详细信息",
        "content": """你是一个电商商品信息抓取助手。请从页面中提取以下商品信息：

- 商品名称
- 价格
- 库存状态
- 商品描述
- 商品图片（URL）
- 规格/属性
- 客户评价摘要

以 Markdown 格式输出，每个部分使用 ## 标题。

商品页面：{{product_url}}""",
        "category": "电商",
        "variables": ["product_url"],
    },
    {
        "name": "新闻文章摘要",
        "description": "总结新闻文章并提取关键要点",
        "content": """你是一个新闻文章分析助手。请完成以下任务：

1. 用 2-3 句话概括主要内容
2. 以项目符号列表提取关键要点
3. 确定来源、作者和发布日期
4. 提取知名人士的任何引用
5. 确定相关主题或标签

以 Markdown 格式输出。

文章链接：{{article_url}}""",
        "category": "新闻",
        "variables": ["article_url"],
    },
]


async def init_default_data() -> None:
    """Initialize default LLM configs and prompts."""
    async with async_session_maker() as session:
        # Check if data already exists
        from sqlalchemy import select

        result = await session.execute(select(LLMConfig))
        existing_llms = result.scalars().all()

        if not existing_llms:
            logger.info("Initializing default LLM configurations...")
            for llm_data in DEFAULT_LLMS:
                llm = LLMConfig(**llm_data)
                # Don't set api_key for defaults - user must configure
                llm.api_key = None
                session.add(llm)
            await session.commit()
            logger.info(f"Created {len(DEFAULT_LLMS)} default LLM configurations")
        else:
            logger.info(f"LLM configurations already exist ({len(existing_llms)} found)")

        # Check prompts
        result = await session.execute(select(Prompt))
        existing_prompts = result.scalars().all()

        if not existing_prompts:
            logger.info("Initializing default prompt templates...")
            for prompt_data in DEFAULT_PROMPTS:
                prompt = Prompt(**prompt_data)
                session.add(prompt)
            await session.commit()
            logger.info(f"Created {len(DEFAULT_PROMPTS)} default prompt templates")
        else:
            logger.info(f"Prompt templates already exist ({len(existing_prompts)} found)")


async def main() -> None:
    """Main entry point."""
    await init_default_data()


if __name__ == "__main__":
    asyncio.run(main())
