import os
import socket
import subprocess
import sys
import threading
import time


BACKEND_DIR = "backend"
ADMIN_DIR = "admin-web"
MOBILE_DIR = "mobile-web"


def get_target_path(dir_name):
    return os.path.join(os.getcwd(), dir_name)


def check_dir(dir_name):
    target_path = get_target_path(dir_name)
    if not os.path.exists(target_path):
        print(f"[ERROR] 找不到目录: {dir_name}")
        print(f"        期望路径: {target_path}")
        return False
    if not os.path.isdir(target_path):
        print(f"[ERROR] 路径不是目录: {target_path}")
        return False
    return True


def get_backend_python():
    venv_python = os.path.join(get_target_path(BACKEND_DIR), "venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        return venv_python
    return sys.executable


def wait_for_port(host, port, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            if sock.connect_ex((host, port)) == 0:
                return True
        time.sleep(0.5)
    return False


def run_frontend(step_label, service_label, dir_name):
    if not check_dir(dir_name):
        return

    print(f">>> [{step_label}] 正在启动 {service_label} ({dir_name})...")
    target_path = get_target_path(dir_name)
    npm_command = "npm.cmd run dev" if os.name == "nt" else "npm run dev"
    try:
        subprocess.run(npm_command, shell=True, cwd=target_path)
    except Exception as exc:
        print(f"!!! {service_label} 启动失败: {exc}")


def run_backend():
    if not check_dir(BACKEND_DIR):
        return

    backend_path = get_target_path(BACKEND_DIR)
    backend_python = get_backend_python()
    print(f">>> [1/3] 正在启动后端 ({BACKEND_DIR})...")
    print(f"    使用解释器: {backend_python}")

    try:
        subprocess.run([backend_python, "app.py"], cwd=backend_path)
    except Exception as exc:
        print(f"!!! 后端启动失败: {exc}")


def run_admin():
    run_frontend("2/3", "PC 管理端", ADMIN_DIR)


def run_mobile():
    run_frontend("3/3", "手机用户端", MOBILE_DIR)


def build_threads():
    return [
        threading.Thread(target=run_backend, daemon=True),
        threading.Thread(target=run_admin, daemon=True),
        threading.Thread(target=run_mobile, daemon=True),
    ]


def main():
    print("==================================================")
    print("    Smart Mall 一键启动")
    print(f"    当前工作目录: {os.getcwd()}")
    print("==================================================")

    backend_thread, admin_thread, mobile_thread = build_threads()
    backend_thread.start()

    print("等待后端监听 5000 端口...")
    if wait_for_port("127.0.0.1", 5000, timeout=20):
        print("后端启动成功，开始启动前端。")
    else:
        print("后端在 20 秒内未监听 5000 端口。前端启动后可能显示连接失败，请先检查后端日志。")

    admin_thread.start()
    mobile_thread.start()

    print("启动指令已发送。")
    print("停止方法：点击 PyCharm 下方红色停止按钮，或在终端按 Ctrl+C。")
    print("--------------------------------------------------")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("正在停止服务...")


if __name__ == "__main__":
    main()
