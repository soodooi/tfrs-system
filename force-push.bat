@echo off
chcp 65001 >nul
echo ========================================
echo 强制推送到 GitHub
echo ========================================
echo.

echo 配置代理...
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

echo.
echo 检查本地提交...
git log --oneline -5

echo.
echo 开始推送...
git push -u origin main --force

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✓ 推送成功！
    echo ========================================
    echo.
    echo 请访问验证：
    echo https://github.com/soodooi/tfrs-system
    echo.
) else (
    echo.
    echo ========================================
    echo ✗ 推送失败
    echo ========================================
    echo.
    echo 可能的原因：
    echo 1. 代理端口不对（当前使用 7890）
    echo 2. GitHub 仓库不存在或无权限
    echo 3. 网络连接问题
    echo.
    echo 建议使用 GitHub Desktop 手动推送
    echo.
)

git config --global --unset http.proxy
git config --global --unset https.proxy

pause