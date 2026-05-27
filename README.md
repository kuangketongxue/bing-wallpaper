# 🖼️ 壁纸自动更新

从本地壁纸图库随机选择图片，每天自动更换桌面壁纸。支持开机自启动和后台静默运行。

## ✨ 特性

- **本地图库**：从指定目录读取图片，支持 jpg/png/jpeg 格式
- **随机选择**：每次从图库中随机选取一张
- **自动更新**：每小时自动更换一次壁纸
- **开机自启**：设置为开机自动运行
- **静默运行**：无窗口后台执行，不占用资源
- **历史记录**：保留最近 30 次壁纸更新记录

## 📦 安装

### 方式一：一键安装（推荐）

双击 `一键安装.bat`，自动完成依赖安装和自启动设置。

### 方式二：手动安装

```powershell
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置开机自启动
python bing_wallpaper.py --install
```

## 🚀 使用

### 添加壁纸

将图片放入 `壁纸图库` 目录即可：

```
壁纸自动更新/
├── 壁纸图库/          # ← 把图片放这里
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
├── bing_wallpaper.py
└── ...
```

### 命令列表

```powershell
# 手动更新一次壁纸
python bing_wallpaper.py

# 强制更新（忽略时间间隔检查）
python bing_wallpaper.py --force

# 设置开机自启动
python bing_wallpaper.py --install

# 取消开机自启动
python bing_wallpaper.py --uninstall

# 静默运行（无控制台窗口）
pythonw bing_wallpaper.py --silent
```

## ⚙️ 配置

修改 `bing_wallpaper.py` 中的配置：

| 配置项 | 位置 | 默认值 | 说明 |
|--------|------|--------|------|
| 壁纸图库路径 | `WALLPAPER_LIBRARY` | `./壁纸图库` | 存放壁纸的目录 |
| 更新间隔 | watchdog.py | 1 小时 | 两次更新的最小间隔 |

## 📁 项目结构

```
壁纸自动更新/
├── bing_wallpaper.py    # 主程序
├── watchdog.py          # 看门狗守护进程
├── 一键安装.bat         # 一键安装脚本
├── requirements.txt     # Python 依赖
├── README.md           # 说明文档
├── CLAUDE.md           # 开发文档
├── 壁纸图库/            # 壁纸存储目录
├── config.json         # 配置文件（自动生成）
└── history.json        # 历史记录（自动生成）
```

## 🛠️ 技术栈

- Python 3.7+
- requests (HTTP 请求)
- ctypes (Windows API 调用)

## 📝 注意事项

1. 首次运行需要先往 `壁纸图库` 放入图片
2. 支持的图片格式：jpg, jpeg, png（大小写不敏感）
3. 壁纸会自动缩放到屏幕分辨率
4. 如需更换壁纸，直接往图库添加新图片即可

## 🐛 常见问题

**Q: 壁纸没有自动更新？**  
A: 检查是否设置了开机自启动，运行 `python bing_wallpaper.py --install`

**Q: 如何立即更换壁纸？**  
A: 使用 `--force` 参数强制更新

**Q: 如何停止自动更新？**  
A: 运行 `python bing_wallpaper.py --uninstall` 取消自启动

## 📄 License

MIT License
