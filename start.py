import subprocess
import os
import sys
import time
import threading

# --- 项目子目录配置（相对于当前工作目录）---
BACKEND_DIR = "backend"
ADMIN_DIR = "admin-web"
MOBILE_DIR = "mobile-web"


def get_target_path(dir_name):
    """拼出目标目录绝对路径。"""
    return os.path.join(os.getcwd(), dir_name)


def check_dir(dir_name):
    """检查目标目录是否存在且是文件夹。"""
    target_path = get_target_path(dir_name)
    if not os.path.exists(target_path):
        print(f"❌ 错误：找不到文件夹 '{dir_name}'")
        print(f"   系统在找：{target_path}")
        print(f"   当前目录下有哪些文件：{os.listdir(os.getcwd())}")
        return False
    if not os.path.isdir(target_path):
        print(f"❌ 错误：'{dir_name}' 存在，但它不是一个文件夹！")
        return False
    return True


def run_frontend(step_label, service_label, dir_name):
    """启动前端服务（admin/mobile 共用逻辑）。"""
    if not check_dir(dir_name):
        return

    print(f">>> [{step_label}] 正在启动 {service_label} ({dir_name})...")
    target_path = get_target_path(dir_name)

    # 在 Windows 下使用 shell=True，避免出现 npm 命令找不到
    try:
        subprocess.run("npm run dev", shell=True, cwd=target_path)
    except Exception as e:
        print(f"!!! {service_label}启动出错: {e}")


def run_backend():
    """启动 Flask 后端。"""
    if not check_dir(BACKEND_DIR):
        return

    print(f">>> [1/3] 正在启动后端 ({BACKEND_DIR})...")
    backend_path = get_target_path(BACKEND_DIR)
    subprocess.run([sys.executable, "app.py"], cwd=backend_path)


def run_admin():
    run_frontend("2/3", "PC管理端", ADMIN_DIR)


def run_mobile():
    run_frontend("3/3", "手机用户端", MOBILE_DIR)


def build_threads():
    """创建并返回三个启动线程。"""
    return [
        threading.Thread(target=run_backend, daemon=True),
        threading.Thread(target=run_admin, daemon=True),
        threading.Thread(target=run_mobile, daemon=True),
    ]


def main():
    print("==================================================")
    print("   🚀 Smart Mall 一键启动 (适配横杠版)")
    print(f"   当前工作目录: {os.getcwd()}")
    print("==================================================")

    # 并行启动：后端先启动，前端稍后启动，避免前端请求后端时过早失败
    backend_thread, admin_thread, mobile_thread = build_threads()
    backend_thread.start()
    time.sleep(2)
    admin_thread.start()
    mobile_thread.start()

    print("\n✅ 启动指令已发送。")
    print("🔴 停止方法：点击 PyCharm 下方红色方块按钮")
    print("--------------------------------------------------")

    # 让主线程保持存活，直到手动中断
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("正在停止服务...")


if __name__ == '__main__':
    main()
