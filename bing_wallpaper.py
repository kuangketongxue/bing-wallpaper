"""
壁纸自动更新程序
- 从本地壁纸图库随机选择图片
- 每小时自动更换桌面壁纸
- 支持开机自启动和后台静默运行
"""
import os
import sys
import json
import time
import ctypes
import hashlib
import random
import requests
from datetime import datetime
from pathlib import Path
import winreg

# 配置
WALLPAPER_LIBRARY = Path(__file__).parent / "壁纸图库"  # 壁纸图库目录
CONFIG_FILE = Path(__file__).parent / "config.json"
HISTORY_FILE = Path(__file__).parent / "history.json"

# 用户偏好关键词（用于网络备用方案）
UNSPASH_KEYWORDS = [
    'ocean sunset', 'beach sunshine', 'sea waves', 'blue ocean', 'tropical beach',
    'anime landscape', 'anime sky', 'anime sea', 'cartoon nature', 'illustration ocean',
    'sunset beach', 'sunrise ocean', 'calm sea', 'crystal water', 'paradise island'
]


class WallpaperManager:
    def __init__(self):
        self.wallpaper_library = WALLPAPER_LIBRARY  # 壁纸图库
        self.config_file = CONFIG_FILE
        self.history_file = HISTORY_FILE
        self.current_wallpaper = None

        # 初始化配置
        self._load_config()
        self._load_history()

    def _load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f'加载配置失败：{e}')
                self.config = {}
        else:
            self.config = {
                'last_update': None,
                'update_interval_hours': 24,
                'auto_start': True
            }
            self._save_config()

    def _save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def _load_history(self):
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f'加载历史记录失败：{e}')
                self.history = {'images': [], 'last_checked': None}
        else:
            self.history = {'images': [], 'last_checked': None}

    def _save_history(self):
        """保存历史记录"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def get_wallpapers(self, days=7):
        """获取壁纸列表（优先从本地图库选择）"""
        # 优先从本地壁纸目录读取
        wallpapers = self._get_local_wallpapers()

        if wallpapers:
            return wallpapers

        # 本地没有壁纸时，尝试在线获取
        print('本地无壁纸，尝试从网络获取...')
        return self._get_unsplash_wallpapers()

    def _get_local_wallpapers(self):
        """从本地壁纸图库读取"""
        wallpapers = []

        try:
            # 扫描壁纸图库目录
            if not self.wallpaper_library.exists():
                print(f'壁纸图库不存在：{self.wallpaper_library}')
                return wallpapers

            image_files = list(self.wallpaper_library.glob("*.jpg")) + list(self.wallpaper_library.glob("*.png")) + list(self.wallpaper_library.glob("*.jpeg")) + list(self.wallpaper_library.glob("*.JPG")) + list(self.wallpaper_library.glob("*.PNG"))

            for img_path in image_files:
                wallpaper_info = {
                    'url': '',
                    'copyright': img_path.stem,
                    'md5': hashlib.md5(img_path.read_bytes()).hexdigest()[:8],
                    'downloaded': True,
                    'local_path': str(img_path),
                    'score': random.randint(5, 10)  # 随机分数用于排序
                }
                wallpapers.append(wallpaper_info)

            if wallpapers:
                print(f'壁纸图库找到 {len(wallpapers)} 张图片')
                # 打乱顺序实现随机选择
                random.shuffle(wallpapers)

        except Exception as e:
            print(f'读取壁纸图库失败：{e}')

        return wallpapers

    def _get_unsplash_wallpapers(self):
        """从网络获取壁纸（当壁纸图库为空时的备用方案）"""
        wallpapers = []

        try:
            keyword = random.choice(UNSPASH_KEYWORDS)
            url = f"https://image.pollinations.ai/prompt/{keyword}?width=1920&height=1080&nologo=true&seed={int(time.time())}"

            print(f'正在获取壁纸 (关键词：{keyword})')
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()

            md5 = hashlib.md5(f"{keyword}_{int(time.time())}".encode()).hexdigest()[:8]
            self.wallpaper_library.mkdir(exist_ok=True)
            local_path = self.wallpaper_library / f"wallpaper_{md5}.jpg"

            with open(local_path, 'wb') as f:
                f.write(response.content)

            print(f'下载完成：{local_path}')

            wallpapers.append({
                'url': url,
                'copyright': f'{keyword} (Pollinations AI)',
                'md5': md5,
                'downloaded': True,
                'local_path': str(local_path),
                'score': 10
            })

        except Exception as e:
            print(f'获取网络壁纸失败：{e}')

        return wallpapers

    def set_as_wallpaper(self, image_path):
        """设置桌面壁纸"""
        try:
            image_path = os.path.abspath(image_path)

            # Windows API 设置壁纸
            SPI_SETDESKWALLPAPER = 20
            SPIF_UPDATEINIFILE = 0x01
            SPIF_SENDCHANGE = 0x02

            result = ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER,
                0,
                image_path,
                SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
            )

            if result:
                print(f'壁纸设置成功：{image_path}')
                self.current_wallpaper = image_path
                self.config['last_update'] = datetime.now().isoformat()
                self._save_config()
                return True
            else:
                print('设置壁纸失败')
                return False

        except Exception as e:
            print(f'设置壁纸异常：{e}')
            return False

    def update_wallpaper(self, force=False):
        """更新壁纸"""
        # 检查是否需要更新
        if not force and self.config.get('last_update'):
            last_update = datetime.fromisoformat(self.config['last_update'])
            hours_since_update = (datetime.now() - last_update).total_seconds() / 3600

            if hours_since_update < self.config.get('update_interval_hours', 24):
                print(f'距离上次更新仅 {hours_since_update:.1f} 小时，跳过更新')
                return False

        print(f'\n=== 开始更新壁纸 [{datetime.now().strftime("%Y-%m-%d %H:%M")}] ===')

        # 获取壁纸列表（优先 Unsplash/Pollinations AI）
        wallpapers = self.get_wallpapers(days=7)

        if not wallpapers:
            print('未获取到任何壁纸')
            return False

        # Unsplash 已经直接下载，直接使用
        best_match = wallpapers[0]
        path = best_match.get('local_path')

        if path and os.path.exists(path):
            print(f'设置壁纸：{best_match["copyright"]}')
            success = self.set_as_wallpaper(path)

            # 更新历史记录
            self.history['images'].append({
                'date': datetime.now().isoformat(),
                'copyright': best_match.get('copyright', ''),
                'score': best_match.get('score', 0),
                'path': path
            })

            # 保留最近 30 条记录
            if len(self.history['images']) > 30:
                self.history['images'] = self.history['images'][-30:]

            self._save_history()

            # 清理旧壁纸
            self.cleanup_old_wallpapers(keep_count=10)

            return success

        return False

    def cleanup_old_wallpapers(self, keep_count=10):
        """清理旧壁纸，保留最近的 N 张（不操作用户自己的壁纸图库）"""
        # 不再自动清理，壁纸图库由用户自己管理
        pass


def set_autostart(enabled=True):
    """设置开机自启动"""
    try:
        key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
        value_name = 'BingWallpaper'

        if enabled:
            script_path = os.path.abspath(sys.argv[0] if sys.argv[0].endswith('.py') else __file__)
            pythonw_path = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
            if not os.path.exists(pythonw_path):
                pythonw_path = sys.executable

            command = f'"{pythonw_path}" "{script_path}" --silent'

            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            print('已设置开机自启动')
        else:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, value_name)
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)
            print('已取消开机自启动')

        return True
    except Exception as e:
        print(f'设置自启动失败：{e}')
        return False


def main():
    silent = '--silent' in sys.argv
    force = '--force' in sys.argv

    if not silent:
        print('=' * 50)
        print('必应壁纸自动更新程序')
        print('=' * 50)

    manager = WallpaperManager()

    # 如果是命令行参数指定 --install，设置自启动
    if '--install' in sys.argv:
        set_autostart(True)
        return

    if '--uninstall' in sys.argv:
        set_autostart(False)
        return

    # 更新壁纸
    success = manager.update_wallpaper(force=force)

    if success:
        print('\n壁纸更新成功!')
    else:
        print('\n壁纸更新失败或无需更新')

    # 静默模式下直接退出，非静默模式等待一下
    if not silent:
        time.sleep(2)


if __name__ == '__main__':
    main()
