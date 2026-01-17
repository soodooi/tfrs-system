@echo off
chcp 65001 >nul
echo ========================================
echo GitHub 推送助手
echo ========================================
echo.

echo 正在尝试推送到 GitHub...
echo.

REM 尝试常见的代理端口
set PORTS=7890 10809 1080 7891 10808 8080 8888

for %%p in (%PORTS%) do (
    echo [尝试] 使用代理端口 %%p...
    git config --global http.proxy http://127.0.0.1:%%p
    git config --global https.proxy http://127.0.0.1:%%p
    
    git push -u origin main 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ========================================
        echo ✓ 推送成功！使用的代理端口: %%p
        echo ========================================
        echo.
        echo 您的代理端口是: %%p
        echo 下次可以直接使用此端口。
        echo.
        pause
        exit /b 0
    )
    
    echo [失败] 端口 %%p 不可用
    echo.
)

echo ========================================
echo ✗ 所有常见端口都失败了
echo ========================================
echo.
echo 请尝试以下方法：
echo.
echo 方法 1: 手动查找代理端口
echo   1. 打开您的代理软件（Clash/V2Ray等）
echo   2. 查找 "HTTP 代理端口" 或 "Port"
echo   3. 记下端口号（如 7890）
echo   4. 运行以下命令：
echo      git config --global http.proxy http://127.0.0.1:端口号
echo      git config --global https.proxy http://127.0.0.1:端口号
echo      git push -u origin main
echo.
echo 方法 2: 使用 GitHub Desktop（推荐）
echo   1. 下载: https://desktop.github.com/
echo   2. 登录 GitHub 账号
echo   3. 添加本地仓库
echo   4. 点击 "Publish repository"
echo.
echo 方法 3: 手动上传
echo   1. 访问: https://github.com/soodooi/tfrs-system
echo   2. 如果仓库不存在，先创建
echo   3. 点击 "uploading an existing file"
echo   4. 拖拽所有文件上传
echo.

REM 清理代理配置
git config --global --unset http.proxy
git config --global --unset https.proxy

pause