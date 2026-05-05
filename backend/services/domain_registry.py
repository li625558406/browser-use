# D:/AI/ai-scout/browser-use/backend/services/domain_registry.py

"""Registry of domains that have been successfully logged in."""

import json
from datetime import datetime
from pathlib import Path

from backend.utils.logger import logger

REGISTRY_PATH = Path("data") / "logged_in_domains.json"


def _load_registry() -> dict:
	"""Load the domain registry from disk."""
	if not REGISTRY_PATH.exists():
		return {}
	try:
		with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
			return json.load(f)
	except Exception as e:
		logger.warning(f"Failed to load domain registry: {e}")
		return {}


def _save_registry(registry: dict):
	"""Save the domain registry to disk."""
	REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
	with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
		json.dump(registry, f, ensure_ascii=False, indent=2)


def is_domain_logged_in(domain: str) -> bool:
	"""Check if a domain has been previously logged in."""
	registry = _load_registry()
	entry = registry.get(domain)
	if entry:
		logger.info(f"Domain '{domain}' was previously logged in at {entry.get('logged_in_at')}")
		return True
	logger.info(f"Domain '{domain}' is NOT in logged-in registry")
	return False


def mark_domain_logged_in(domain: str):
	"""Mark a domain as successfully logged in."""
	registry = _load_registry()
	registry[domain] = {
		"logged_in_at": datetime.now().isoformat(),
	}
	_save_registry(registry)
	logger.info(f"Domain '{domain}' marked as logged in")


def remove_domain(domain: str):
	"""Remove a domain from the registry (e.g., after login expires)."""
	registry = _load_registry()
	registry.pop(domain, None)
	_save_registry(registry)
	logger.info(f"Domain '{domain}' removed from registry")
