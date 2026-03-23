@echo off
chcp 65001 >nul
echo ========================================
echo   墨痕工坊 - 停止服务
echo ========================================
echo.

echo [1/2] 查找占用端口 8080 的进程...
netstat -ano | findstr :8080 >nul
if %errorlevel% neq 0 (
    echo [提示] 端口 8080 未被占用，服务可能已停止
    goto :end
)

echo [2/2] 停止服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    taskkill //F //PID %%a >nul 2>&1
    if %errorlevel% equ 0 (
        echo [成功] 服务已停止 ^(PID: %%a^)
    )
)

:end
echo.
echo ========================================
echo   操作完成
echo ========================================
echo.
pause
