Write-Host "正在关闭Chrome进程..."
Get-Process | Where-Object { $_.ProcessName -like "*chrome*" } | Stop-Process -Force

Write-Host "等待2秒..."
Start-Sleep -Seconds 2

$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$arg1 = "--remote-debugging-port=9222"
$arg2 = "--user-data-dir=$env:LOCALAPPDATA\Google\Chrome\User Data"

Write-Host "正在启动Chrome CDP模式..."
Start-Process $chromePath -ArgumentList $arg1, $arg2

Write-Host "Chrome已启动，CDP端口: 9222"
Write-Host "请按任意键关闭此窗口..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
