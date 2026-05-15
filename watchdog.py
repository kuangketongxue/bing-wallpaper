"""
看门狗守护进程 - 监控壁纸更新程序
- 每 24 小时自动唤醒主程序更新壁纸
- 主程序崩溃时自动重启
- 开机自启动
"""
import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
import psutil
import ctypes

# 配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_SCRIPT = os.path.join(SCRIPT_DIR, 'bing_wallpaper.py')
LOCK_FILE = os.path.join(SCRIPT_DIR, '.watchdog.lock')
LAST_RUN_FILE = os.path.join(SCRIPT_DIR, '.last_run.json')

UPDATE_INTERVAL_HOURS = 24  # 更新间隔


def is_already_running():
    """单实例检查"""
    try:
        import msvcrt
        lock_handle = open(LOCK_FILE, 'w')
        msvcrt.locking(lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
        lock_handle.write(str(os.getpid()))
        lock_handle.flush()
        atexit.register(lambda: cleanup_lock(lock_handle, LOCK_FILE))
        return False
    except (IOError, ImportError):
        return True


def cleanup_lock(lock_handle, lock_file):
    try:
        import msvcrt
        msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
        lock_handle.close()
        if os.path.exists(lock_file):
            os.remove(lock_file)
    except:
        pass


def get_last_run_time():
    """获取上次运行时间"""
    if os.path.exists(LAST_RUN_FILE):
        try:
            with open(LAST_RUN_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return datetime.fromisoformat(data['last_run'])
        except:
            pass
    return None


def save_run_time():
    """保存运行时间"""
    with open(LAST_RUN_FILE, 'w', encoding='utf-8') as f:
        json.dump({'last_run': datetime.now().isoformat()}, f)


def run_main_script():
    """运行主脚本"""
    try:
        # 使用 pythonw 静默运行
        pythonw_path = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
        if not os.path.exists(pythonw_path):
            pythonw_path = sys.executable

        # CREATE_NO_WINDOW 标志
        CREATE_NO_WINDOW = 0x08000000

        proc = subprocess.Popen(
            [pythonw_path, MAIN_SCRIPT, '--silent'],
            creationflags=CREATE_NO_WINDOW,
            cwd=SCRIPT_DIR
        )

        print(f'[{datetime.now()}] 启动壁纸更新程序，PID={proc.pid}')
        save_run_time()

        # 等待主程序完成（最多 5 分钟）
        try:
            proc.wait(timeout=300)
            print(f'[{datetime.now()}] 壁纸更新程序已完成')
        except subprocess.TimeoutExpired:
            print(f'[{datetime.now()}] 壁纸更新程序超时，终止进程')
            proc.kill()

        return True

    except Exception as e:
        print(f'[{datetime.now()}] 启动主程序失败：{e}')
        return False


def main_loop():
    """主循环"""
    print(f'[{datetime.now()}] 看门狗启动，更新间隔={UPDATE_INTERVAL_HOURS}小时')

    while True:
        now = datetime.now()
        last_run = get_last_run_time()

        # 检查是否需要运行
        should_run = False

        if last_run is None:
            should_run = True
            print(f'[{now}] 首次运行')
        else:
            hours_since = (now - last_run).total_seconds() / 3600
            if hours_since >= UPDATE_INTERVAL_HOURS:
                should_run = True
                print(f'[{now}] 距离上次运行 {hours_since:.1f} 小时')

        if should_run:
            run_main_script()

        # 每小时检查一次
        time.sleep(3600)


if __name__ == '__main__':
    import json
    import atexit

    if is_already_running():
        print('看门狗程序已在运行')
        sys.exit(0)

    try:
        main_loop()
    except KeyboardInterrupt:
        print('\n看门狗停止')
    except Exception as e:
        print(f'看门狗异常：{e}')
