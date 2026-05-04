# D:/AI/ai-scout/browser-use/backend/utils/chrome.py

import platform
from pathlib import Path
from typing import List


def get_chrome_user_data_path() -> Path:
	"""获取 Chrome 用户数据目录"""
	system = platform.system()

	if system == "Windows":
		return Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
	elif system == "Darwin":  # macOS
		return Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
	else:  # Linux
		return Path.home() / ".config" / "google-chrome"


def get_available_profiles() -> List[dict]:
	"""获取可用的 Chrome Profile 列表"""
	user_data_path = get_chrome_user_data_path()

	if not user_data_path.exists():
		return []

	profiles = []

	# 添加 Default Profile
	default_path = user_data_path / "Default"
	if default_path.exists():
		profiles.append({
			"name": "Default",
			"path": str(default_path),
		})

	# 查找其他 Profile (Profile 1, Profile 2, ...)
	for i in range(1, 100):
		profile_name = f"Profile {i}"
		profile_path = user_data_path / profile_name
		if profile_path.exists():
			profiles.append({
				"name": profile_name,
				"path": str(profile_path),
			})
		else:
			break

	return profiles
