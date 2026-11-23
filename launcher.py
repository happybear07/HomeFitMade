"""
홈핏 메이트 실행기 (윈도우 앱처럼 실행)

서버를 켜고, 주소창 없는 앱 창(Edge 또는 Chrome 앱 모드)으로 화면을 띄운다.
이 검은 창을 닫으면 프로그램이 종료된다.
"""
import os
import shutil
import socket
import subprocess
import threading
import time
import webbrowser

from werkzeug.serving import make_server

from app import app


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def find_app_browser():
    """주소창 없이 앱처럼 띄울 수 있는 브라우저(Edge, Chrome)를 찾는다."""
    candidates = [
        r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
        r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
        r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
        r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
        r"%LocalAppData%\Google\Chrome\Application\chrome.exe",
    ]
    for c in candidates:
        path = os.path.expandvars(c)
        if os.path.isfile(path):
            return path
    return shutil.which("msedge") or shutil.which("chrome")


def open_window(url):
    browser = find_app_browser()
    if browser:
        subprocess.Popen([browser, f"--app={url}", "--window-size=440,880"])
    else:
        webbrowser.open(url)


def main():
    port = free_port()
    url = f"http://127.0.0.1:{port}/"
    server = make_server("127.0.0.1", port, app, threaded=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    print("=" * 44)
    print("  홈핏 메이트가 실행 중이에요")
    print(f"  창이 안 뜨면 브라우저에서 {url} 접속")
    print("  이 창을 닫으면 프로그램이 종료돼요")
    print("=" * 44)
    time.sleep(0.5)
    open_window(url)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
