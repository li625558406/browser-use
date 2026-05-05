# D:/AI/ai-scout/browser-use/backend/api/browser.py

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Callable

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.response import ApiResponse
from backend.schemas.browser_config import (
    BrowserConfigResponse,
    BrowserStatusResponse,
    ChromeProfileInfo,
)
from backend.services.browser_service import BrowserService
from backend.utils.chrome import get_available_profiles
from backend.utils.logger import logger

router = APIRouter()

@router.get("/ping")
async def ping():
    """Ping endpoint for testing"""
    return {"pong": True}


@router.post("/start-chrome")
async def start_chrome(body: dict | None = None):
    """启动Chrome并启用CDP"""
    import json

    # 解析请求参数
    profile = "Default"
    port = 9222
    reopen_url = None

    if body:
        profile = body.get("profile", "Default")
        port = body.get("port", 9222)
        reopen_url = body.get("reopen_url")

    # 获取Chrome路径
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]

    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break

    if not chrome_path:
        # 尝试通过where命令查找
        try:
            result = subprocess.run(["where", "chrome.exe"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                chrome_path = result.stdout.strip().split('\n')[0]
        except:
            pass

    if not chrome_path:
        return ApiResponse.error(message="无法找到Chrome可执行文件，请确保Chrome已安装")

    # 获取用户数据目录
    user_data_dir = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data")

    # 检查是否已有Chrome在运行
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:{port}/json", timeout=2.0)
            if response.status_code == 200:
                # Chrome已在运行，如果指定了reopen_url，打开新标签页
                if reopen_url:
                    try:
                        # 通过CDP打开新标签页
                        async with httpx.AsyncClient() as client:
                            # 获取可用的target
                            targets_response = await client.get(f"http://localhost:{port}/json", timeout=2.0)
                            if targets_response.status_code == 200:
                                targets = targets_response.json()
                                # 找到第一个可用的page
                                for target in targets:
                                    if target.get('type') == 'page':
                                        # 在这个page中打开新URL
                                        await client.get(f"http://localhost:{port}/json/new?{reopen_url}", timeout=2.0)
                                        break
                    except:
                        pass

                return ApiResponse.success(
                    data={"success": True, "message": f"Chrome已在端口 {port} 上运行", "port": port}
                )
    except:
        pass

    # 启动Chrome
    args = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        f"--profile-directory={profile}",
        "--no-first-run",
        "--no-default-browser-check",
    ]

    # 如果指定了reopen_url，启动时直接打开
    if reopen_url:
        args.append(reopen_url)

    logger.info(f"启动Chrome: {' '.join(args)}")

    try:
        subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True
        )

        # 等待Chrome启动
        await asyncio.sleep(3)

        # 验证CDP是否可用
        import httpx
        max_retries = 10
        for i in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"http://localhost:{port}/json", timeout=2.0)
                    if response.status_code == 200:
                        return ApiResponse.success(
                            data={
                                "success": True,
                                "message": f"Chrome已成功启动，CDP端口: {port}",
                                "port": port,
                                "profile": profile
                            }
                        )
            except:
                if i < max_retries - 1:
                    await asyncio.sleep(1)

        return ApiResponse.error(message="Chrome启动后无法连接到CDP端口")
    except Exception as e:
        logger.error(f"启动Chrome失败: {e}")
        return ApiResponse.error(message=f"启动Chrome失败: {str(e)}")


@router.get("/profiles", response_model=ApiResponse[list[ChromeProfileInfo]])
async def list_profiles():
    """Get available Chrome Profile list"""
    profiles = get_available_profiles()

    response_data = [
        ChromeProfileInfo(
            name=p["name"],
            path=p["path"],
        )
        for p in profiles
    ]

    return ApiResponse.success(data=response_data)


@router.get("/status", response_model=ApiResponse[BrowserStatusResponse])
async def get_browser_status(cdp_port: int = 9242):
    """Get browser status"""
    profiles = get_available_profiles()

    profile_infos = [
        ChromeProfileInfo(
            name=p["name"],
            path=p["path"],
        )
        for p in profiles
    ]

    # Test CDP connection
    is_connected = await BrowserService.test_connection(cdp_port)

    return ApiResponse.success(
        data=BrowserStatusResponse(
            is_connected=is_connected,
            cdp_url=f"http://localhost:{cdp_port}" if is_connected else None,
            profiles=profile_infos,
        )
    )


@router.get("/test-connection")
async def test_connection_get(cdp_port: int = 9242):
    """Test CDP connection (GET)"""
    return await test_connection(cdp_port=cdp_port, start_if_not_running=False)

@router.post("/test-connection", response_model=ApiResponse[dict])
async def test_connection(cdp_port: int = 9242, start_if_not_running: bool = False, reopen_url: str = None, use_temp_chrome: bool = True, profile: str = "Default"):
    """Test CDP connection

    Args:
        cdp_port: CDP端口
        start_if_not_running: 如果CDP不可用是否启动Chrome
        reopen_url: Chrome启动后打开的URL
        use_temp_chrome: 是否使用临时Chrome（默认true）。设为false时使用用户自己的Chrome目录
        profile: 使用的Profile名称（Default, Profile 1, Profile 2等）
    """
    logger.info(f"测试CDP连接: 端口={cdp_port}, 启动={start_if_not_running}, 临时Chrome={use_temp_chrome}, Profile={profile}")

    result = await BrowserService.test_connection(cdp_port)

    # 如果连接失败且要求启动Chrome
    if not result and start_if_not_running:
        logger.info("CDP连接失败，准备启动Chrome...")

        # 启动Chrome
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]

        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break

        if not chrome_path:
            try:
                where_result = subprocess.run(["where", "chrome.exe"], capture_output=True, text=True, timeout=5)
                if where_result.returncode == 0:
                    chrome_path = where_result.stdout.strip().split('\n')[0]
            except:
                pass

        if chrome_path:
            logger.info(f"找到Chrome: {chrome_path}")

            if use_temp_chrome:
                # 使用临时用户数据目录
                import tempfile
                user_data_dir = tempfile.mkdtemp(prefix="chrome_cdp_")
                logger.info("使用临时Chrome模式（需要登录网站账号）")
            else:
                # 使用用户自己的Chrome目录
                user_data_dir = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data")
                logger.info(f"使用用户Chrome目录，Profile: {profile}（保留登录状态）")

            args = [
                chrome_path,
                f"--remote-debugging-port={cdp_port}",
                f"--user-data-dir={user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check",
            ]

            # 如果指定了profile且使用用户目录，添加profile参数
            if not use_temp_chrome and profile:
                args.append(f"--profile-directory={profile}")
                logger.info(f"使用Profile: {profile}")

            if reopen_url:
                args.append(reopen_url)

            logger.info(f"启动Chrome命令: {' '.join(args)}")

            try:
                subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
                logger.info("Chrome已启动，等待CDP可用...")
                await asyncio.sleep(5)

                result = await BrowserService.test_connection(cdp_port)
                logger.info(f"Chrome启动后CDP测试: {result}")
            except Exception as e:
                logger.error(f"启动Chrome失败: {e}")

    return ApiResponse.success(
        data={
            "success": result,
            "message": "Connection successful" if result else "Connection failed",
        }
    )

    result = await BrowserService.test_connection(cdp_port)

    # 如果连接失败且要求启动Chrome
    if not result and start_if_not_running:
        logger.info("CDP连接失败，准备启动Chrome...")

        # 启动Chrome的逻辑
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]

        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break

        if not chrome_path:
            # 尝试通过where命令查找
            try:
                where_result = subprocess.run(["where", "chrome.exe"], capture_output=True, text=True, timeout=5)
                if where_result.returncode == 0:
                    chrome_path = where_result.stdout.strip().split('\n')[0]
            except:
                pass

        if chrome_path:
            logger.info(f"找到Chrome路径: {chrome_path}")

            # 创建临时用户数据目录，避免与现有Chrome冲突
            import tempfile
            temp_user_data = tempfile.mkdtemp(prefix="chrome_cdp_")

            user_data_dir = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data")

            # 复制Default profile的基本数据
            import shutil
            default_profile = os.path.join(user_data_dir, "Default")
            temp_profile = os.path.join(temp_user_data, "Default")

            try:
                if os.path.exists(default_profile):
                    # 只复制必要的文件
                    shutil.copytree(default_profile, temp_profile,
                                    ignore=shutil.ignore_patterns(
                                        '*Cache*', '*GPUCache*', '*Code Cache*',
                                        '*Service Worker*', '*Cookies*',
                                        '*History*', '*Top Sites*'
                                    ),
                                    dirs_exist_ok=True)
                    logger.info(f"已复制Chrome Profile到临时目录")
            except Exception as e:
                logger.warning(f"复制Profile失败: {e}")

            args = [
                chrome_path,
                f"--remote-debugging-port={cdp_port}",
                f"--user-data-dir={temp_user_data}",
                "--no-first-run",
                "--no-default-browser-check",
            ]
            if reopen_url:
                args.append(reopen_url)

            logger.info(f"启动Chrome命令: {' '.join(args)}")

            try:
                process = subprocess.Popen(
                    args,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True
                )
                logger.info(f"Chrome进程已启动 (PID: {process.pid})，等待CDP可用...")

                # 等待Chrome启动
                await asyncio.sleep(4)

                # 再次测试连接
                result = await BrowserService.test_connection(cdp_port)
                logger.info(f"Chrome启动后CDP测试结果: {result}")
            except Exception as e:
                logger.error(f"启动Chrome失败: {e}")
        else:
            logger.warning("未找到Chrome可执行文件")
    else:
        logger.info(f"CDP连接成功: {result}")

    return ApiResponse.success(
        data={
            "success": result,
            "message": "Connection successful" if result else "Connection failed",
        }
    )
