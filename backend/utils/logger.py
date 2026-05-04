# D:/AI/ai-scout/browser-use/backend/utils/logger.py

import logging
import sys
from pathlib import Path

from backend.config import settings


def setup_logger(name: str = "browser-use-webui") -> logging.Logger:
	"""配置日志"""
	logger = logging.getLogger(name)
	logger.setLevel(getattr(logging, settings.log_level))

	# 清除现有处理器
	logger.handlers.clear()

	# 控制台处理器
	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setLevel(getattr(logging, settings.log_level))

	# 格式化
	formatter = logging.Formatter(
		"%(asctime)s - %(name)s - %(levelname)s - %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S",
	)
	console_handler.setFormatter(formatter)
	logger.addHandler(console_handler)

	# 文件处理器
	log_dir = Path(settings.logs_dir)
	log_dir.mkdir(parents=True, exist_ok=True)

	file_handler = logging.FileHandler(log_dir / "webui.log", encoding="utf-8")
	file_handler.setLevel(getattr(logging, settings.log_level))
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)

	return logger


# 全局日志实例
logger = setup_logger()
