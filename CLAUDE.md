# 壁纸自动更新 — CLAUDE.md

## 项目概述
自动下载并设置高清壁纸，偏好大海/阳光/动漫风格。使用 Pollinations AI API（AI 生成图片）+ 必应备用。支持开机自启动和后台静默运行。

## 技术栈
- Python 3.7+
- requests (HTTP 请求)
- psutil (进程管理)

## 核心文件
```
bing_wallpaper.py    — 主程序（获取 API、下载、设置壁纸）
watchdog.py          — 看门狗守护进程（每 24 小时唤醒主程序）
wallpapers/          — 壁纸存储目录
config.json          — 配置文件（上次更新时间、更新间隔）
history.json         — 历史记录（最近 30 张壁纸）
一键安装.bat         — 安装依赖 + 设置自启动（推荐入口）
```

## 用户偏好机制
| 关键词类型 | 匹配词 |
|------------|--------|
| 海洋日落 | ocean sunset, beach sunshine, sea waves, blue ocean, tropical beach |
| 日出天堂 | sunset beach, sunrise ocean, calm sea, crystal water, paradise island |
| 动漫风格 | anime landscape, anime sky, anime sea, cartoon nature, illustration ocean |

- 每次随机选择一个关键词，通过 Pollinations AI 生成 1920x1080 壁纸
- AI 根据关键词生成符合主题的图片
- 本地缓存壁纸，保留最近 10 张
- 记录最近 30 次更新历史

## 关键配置位置
| 配置 | 位置 | 默认值 |
|------|------|--------|
| 更新间隔 | `UPDATE_INTERVAL_HOURS` (watchdog.py) | 24 小时 |
| 历史保留数 | `cleanup_old_wallpapers()` | 最近 10 张 |
| 历史记录上限 | `_save_history()` | 最近 30 条 |
| 偏好关键词 | `UNSPASH_KEYWORDS` | 见上方表格 |
| 图片尺寸 | `_get_unsplash_wallpapers()` | 1920x1080 |

## 运行方式
```powershell
# 方式 1: 直接运行（手动更新一次）
python bing_wallpaper.py

# 方式 2: 强制更新（忽略时间检查）
python bing_wallpaper.py --force

# 方式 3: 静默运行（不显示控制台）
pythonw bing_wallpaper.py --silent

# 方式 4: 设置开机自启动
python bing_wallpaper.py --install

# 方式 5: 取消开机自启动
python bing_wallpaper.py --uninstall

# 方式 6: 启动看门狗（推荐，每天自动更新）
pythonw watchdog.py
```

## 验证和调试
```powershell
# 查看进程
tasklist | findstr "pythonw.exe"

# 杀掉进程
taskkill /F /IM pythonw.exe

# 查看配置文件
cat config.json
cat history.json

# 查看壁纸存储
ls wallpapers\
```

## 改完代码后必须做的
1. 杀掉旧进程：`taskkill /F /IM pythonw.exe`
2. 启动看门狗：`start "" pythonw watchdog.py`
3. 验证新进程 PID 已出现

## 禁止事项
- 不创建庆祝/确认类临时文件
- 不写重复的修复报告——有问题直接修

## Windows API 说明
设置壁纸使用 `SystemParametersInfoW` with `SPI_SETDESKWALLPAPER (20)`:
```python
ctypes.windll.user32.SystemParametersInfoW(
    20,  # SPI_SETDESKWALLPAPER
    0,
    image_path,
    0x01 | 0x02  # SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
)
```

## Pollinations AI API
```
GET https://image.pollinations.ai/prompt/{keyword}?width=1920&height=1080&nologo=true&seed={timestamp}
```
- 无需 API Key
- 根据 AI 提示词生成图片
- seed 参数确保每次生成不同图片
- nologo=true 去除水印

## 备用必应 API（被墙，国内可能无法访问）
```
GET https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&days=1&nc=1&pid=hp&mkt=zh-CN
```
返回 JS 格式（内含 JSON），解析后提取 `images[].url`，拼接 `https://www.bing.com` 得到完整 URL。
