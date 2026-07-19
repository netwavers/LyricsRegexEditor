import os
import sys
import time
import threading
import urllib.request
from web_server import run_server

DEFAULT_PORT = 8088

def find_active_url(start_port=DEFAULT_PORT):
    """起動済みの Web サーバーまたは空きポートで起動したサーバーの URL を検出"""
    for p in range(start_port, start_port + 10):
        url = f"http://127.0.0.1:{p}"
        try:
            with urllib.request.urlopen(url, timeout=0.5) as resp:
                if resp.status == 200:
                    return url
        except Exception:
            continue
    return None

def start_server_and_wait():
    """Web サーバーを起動し、確実に 200 応答が得られるまで待機"""
    # 既存の起動中サーバーがあればそれを採用
    active_url = find_active_url()
    if active_url:
        return active_url

    # サーバーをバックグラウンドスレッドで自動起動
    server_thread = threading.Thread(target=run_server, kwargs={"port": DEFAULT_PORT}, daemon=True)
    server_thread.start()

    # 最大 5 秒間、サーバーの立ち上がりを待機
    for _ in range(50):
        time.sleep(0.1)
        active_url = find_active_url()
        if active_url:
            return active_url

    return f"http://127.0.0.1:{DEFAULT_PORT}"

def launch_desktop_app():
    """PyWebView または Chrome/Chromium アプリモードで独立ウィンドウを立ち上げる"""
    app_url = start_server_and_wait()
    print(f"🐾 歌詞正規化エディタ デスクトップアプリを起動中... ({app_url})")

    # 1. PyWebView が利用可能な場合
    try:
        import webview
        window = webview.create_window(
            title="🐾 歌詞正規化エディタ (Lyrics Regex Editor)",
            url=app_url,
            width=1320,
            height=860,
            resizable=True,
            min_size=(900, 600)
        )
        webview.start()
        return
    except Exception as e:
        print(f"PyWebView 起動不可 (Chrome アプリモードに切り替えます): {e}")

    # 2. Chrome / Chromium の --app モード（ブラウザ枠のない完全アプリ表示）
    import subprocess
    chrome_cmds = [
        ["google-chrome", f"--app={app_url}", "--window-size=1320,860"],
        ["chromium-browser", f"--app={app_url}", "--window-size=1320,860"],
        ["chromium", f"--app={app_url}", "--window-size=1320,860"],
        ["microsoft-edge", f"--app={app_url}", "--window-size=1320,860"],
    ]

    for cmd in chrome_cmds:
        try:
            subprocess.run(cmd, check=True)
            return
        except Exception:
            continue

    # 3. フォールバック: 標準ブラウザで開く
    import webbrowser
    webbrowser.open(app_url)

if __name__ == "__main__":
    launch_desktop_app()
