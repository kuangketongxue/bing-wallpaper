@echo off
chcp 65001 >nul
echo ========================================
echo 必应壁纸自动更新 - 安装向导
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python
    pause
    exit /b 1
)
echo [OK] Python 已安装

REM 安装依赖
echo.
echo 正在安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [OK] 依赖安装完成

REM 设置开机自启动
echo.
echo 正在设置开机自启动...
python bing_wallpaper.py --install
if errorlevel 1 (
    echo [警告] 自启动设置失败，可手动运行
)

REM 立即更新一次壁纸
echo.
echo 正在下载并设置第一张壁纸...
python bing_wallpaper.py --force

echo.
echo ========================================
echo 安装完成!
echo ========================================
echo.
echo 壁纸程序已设置为开机自启动
echo 每天会自动更新壁纸（偏好：大海/阳光/动漫）
echo.
echo 如需手动更新，运行：python bing_wallpaper.py --force
echo 如需停止自启动，运行：python bing_wallpaper.py --uninstall
echo.
pause
