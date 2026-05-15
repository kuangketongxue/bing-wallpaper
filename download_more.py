"""
批量下载壁纸脚本
- 下载多种风格的壁纸到本地库
- 运行一次即可建立壁纸库
"""
import os
import requests
import time
from pathlib import Path
import hashlib

# 壁纸目录
WALLPAPER_DIR = Path(__file__).parent / "wallpapers"

# 关键词列表（大海、阳光、动漫风格）
KEYWORDS = [
    # 海洋日落
    'ocean sunset', 'beach sunset', 'sunset over sea', 'golden hour beach',
    'ocean waves', 'blue ocean water', 'tropical paradise', 'palm tree beach',
    # 日出阳光
    'sunrise ocean', 'morning sunlight', 'sun rays through clouds', 'bright sunny day',
    'crystal clear water', 'azure sea', 'white sand beach',
    # 动漫风景
    'anime landscape sky', 'anime summer beach', 'anime sunset background',
    'japanese animation scenery', 'manga style nature', 'anime blue sky clouds',
    # 其他美景
    'peaceful lake reflection', 'mountain lake sunset', 'waterfall jungle',
]


def download_wallpaper(keyword, index):
    """下载单张壁纸"""
    try:
        url = f"https://image.pollinations.ai/prompt/{keyword}?width=1920&height=1080&nologo=true&seed={int(time.time()) + index}"

        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()

        md5 = hashlib.md5(f"{keyword}_{index}".encode()).hexdigest()[:8]
        local_path = WALLPAPER_DIR / f"wallpaper_{md5}.jpg"

        with open(local_path, 'wb') as f:
            f.write(response.content)

        return True, str(local_path)
    except Exception as e:
        return False, str(e)


def main():
    print('=' * 50)
    print('批量下载壁纸')
    print('=' * 50)
    print()

    WALLPAPER_DIR.mkdir(exist_ok=True)

    success_count = 0
    fail_count = 0

    for i, keyword in enumerate(KEYWORDS):
        print(f'[{i+1}/{len(KEYWORDS)}] 下载：{keyword}')
        success, result = download_wallpaper(keyword, i)

        if success:
            print(f'  ✓ {result}')
            success_count += 1
        else:
            print(f'  ✗ 失败：{result}')
            fail_count += 1

        # 避免请求过快
        time.sleep(0.5)

    print()
    print('=' * 50)
    print(f'完成！成功：{success_count}, 失败：{fail_count}')
    print(f'壁纸已保存到：{WALLPAPER_DIR}')
    print('=' * 50)


if __name__ == '__main__':
    main()
