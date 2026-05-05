@echo off
echo ========================================
echo   Chrome CDP 启动助手
echo ========================================
echo.
echo 正在关闭Chrome进程...
taskkill /F /IM chrome.exe >nul 2>&1

echo 等待2秒...
timeout /t 2 /nobreak >nul

echo.
echo 请选择要使用的Chrome账号：
echo 1. Default (默认账号)
echo 2. Profile 1 (第二个账号)
echo 3. Profile 2 (第三个账号)
echo.
set /p choice="请输入选项 (1-3): "

if "%choice%"=="1" (
    set PROFILE=Default
    set PORT=9222
) else if "%choice%"=="2" (
    set PROFILE=Profile 1
    set PORT=9223
) else if "%choice%"=="3" (
    set PROFILE=Profile 2
    set PORT=9224
) else (
    echo 无效选项，使用默认配置
    set PROFILE=Default
    set PORT=9222
)

echo.
echo 正在启动Chrome [Profile: %PROFILE%]...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=%PORT% --profile-directory="%PROFILE%" --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"

echo.
echo ========================================
echo Chrome 已启动！CDP端口: %PORT%
echo.
echo 现在可以：
echo 1. 在Chrome中打开前端: http://localhost:5173
echo 2. 运行任务时会在当前Chrome中打开新标签页
echo.
echo 按任意键关闭此窗口...
pause >nul
