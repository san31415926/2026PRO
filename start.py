import os
import socket
import subprocess
import sys
import time


BACKEND_DIR = "backend"
ADMIN_DIR = "admin-web"
MOBILE_DIR = "mobile-web"


def project_path(*parts):
    return os.path.join(os.getcwd(), *parts)


def ensure_dir(dir_name):
    target = project_path(dir_name)
    if not os.path.exists(target):
        print(f"[ERROR] 找不到目录: {dir_name}")
        print(f"        期望路径: {target}")
        return False
    if not os.path.isdir(target):
        print(f"[ERROR] 路径不是目录: {target}")
        return False
    return True


def get_backend_python():
    venv_python = project_path(BACKEND_DIR, "venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        return venv_python
    return sys.executable


def wait_for_port(host, port, timeout=20):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            if sock.connect_ex((host, port)) == 0:
                return True
        time.sleep(0.5)
    return False


def launch_backend():
    if not ensure_dir(BACKEND_DIR):
        return None

    backend_python = get_backend_python()
    backend_path = project_path(BACKEND_DIR)
    print(f">>> [1/3] 正在启动后端 ({BACKEND_DIR})...")
    print(f"    使用解释器: {backend_python}")
    return subprocess.Popen([backend_python, "app.py"], cwd=backend_path)


def launch_frontend(step_label, service_label, dir_name):
    if not ensure_dir(dir_name):
        return None

    target_path = project_path(dir_name)
    print(f">>> [{step_label}] 正在启动 {service_label} ({dir_name})...")
    return subprocess.Popen("npm.cmd run dev", shell=True, cwd=target_path)


def main():
    print("==================================================")
    print("    Smart Mall 一键启动")
    print(f"    当前工作目录: {os.getcwd()}")
    print("==================================================")

    backend_process = launch_backend()

    print("等待后端监听 5000 端口...")
    if wait_for_port("127.0.0.1", 5000, timeout=20):
        print("后端启动成功，开始启动前端。")
    else:
        print("后端在 20 秒内未监听 5000 端口。前端启动后可能显示连接失败，请先检查后端。")

    admin_process = launch_frontend("2/3", "PC 管理端", ADMIN_DIR)
    mobile_process = launch_frontend("3/3", "手机用户端", MOBILE_DIR)

    print("启动指令已发送。")
    print("停止方法：在终端按 Ctrl+C。")
    print("--------------------------------------------------")

    try:
        while True:
            if backend_process and backend_process.poll() is not None:
                print("后端进程已退出，请检查 backend/app.py 启动日志。")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("正在停止服务...")
    finally:
        for process in (mobile_process, admin_process, backend_process):
            if process and process.poll() is None:
                process.terminate()


if __name__ == "__main__":
    main()
