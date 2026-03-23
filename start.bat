@echo off
chcp 65001 >nul
echo ========================================
echo   墨痕工坊 - 启动服务
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] 检查端口 8080 是否被占用...
netstat -ano | findstr :8080 >nul
if %errorlevel% equ 0 (
    echo [警告] 端口 8080 已被占用，正在尝试停止旧服务...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
        taskkill //F //PID %%a >nul 2>&1
    )
    timeout /t 1 /nobreak >nul
)

echo [2/2] 启动 Viewer 服务 ^(含向量搜索 API^)...
echo.
echo ========================================
echo   服务已启动！
echo   访问地址: http://localhost:8080/viewer/
echo   按 Ctrl+C 可停止服务
echo ========================================
echo.

python scripts\viewer_server.py --port 8080
