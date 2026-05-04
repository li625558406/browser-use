# D:/AI/ai-scout/browser-use/backend/utils/init_data.py

"""Initialize default data for the application."""

import asyncio

from backend.database import async_session_maker
from backend.models.llm_config import LLMConfig
from backend.models.prompt import Prompt
from backend.utils.logger import logger


DEFAULT_LLMS = [
    {
        "name": "DeepSeek Chat",
        "provider": "deepseek",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 4096,
        "is_default": True,
    },
    {
        "name": "Ollama Local",
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
        "name": "Generic Data Extraction",
        "description": "Extract structured data from web pages",
        "content": """You are a data extraction assistant. Your task is to extract structured information from the provided web page content.

Please analyze the page and extract:
1. Main title/headline
2. Key data points (numbers, dates, names, etc.)
3. Important descriptions or summaries
4. Any structured data (tables, lists, etc.)

Output the extracted data in Markdown format with clear sections.""",
        "category": "extraction",
        "variables": ["url", "target_data"],
    },
    {
        "name": "Product Information Scraper",
        "description": "Scrape product details from e-commerce pages",
        "content": """You are an e-commerce product scraper. Extract the following product information from the page:

- Product name
- Price
- Availability
- Product description
- Product images (URLs)
- Specifications/attributes
- Customer reviews summary

Output in Markdown format with ## headers for each section.""",
        "category": "ecommerce",
        "variables": ["product_url"],
    },
    {
        "name": "News Article Summarizer",
        "description": "Summarize news articles and extract key points",
        "content": """You are a news article analyzer. Please:

1. Summarize the main story in 2-3 sentences
2. Extract key points as a bulleted list
3. Identify the source, author, and publication date
4. Extract any quotes from notable figures
5. Identify related topics or tags

Output in Markdown format.""",
        "category": "news",
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
