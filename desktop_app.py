import os
import sys
import time
import threading
import urllib.request
from web_server import run_server

PORT = 8088
APP_URL = f"http://localhost:{PORT}"

def start_server_in_thread():
    """Webサーバーをバックグラウンドスレッドで自動起動"""
    server_thread = threading.Thread(target=run_server, kwargs={"port": PORT}, daemon=True)
    server_thread.start()

    # サーバーの立ち上がりを待機
    for _ in range(20):
        try:
            with urllib.request.urlopen(APP_URL) as response:
                if response.status == 200:
                    break
        except Exception:
            time.sleep(0.2)

def launch_desktop_app():
    """PyWebView または Chrome/Chromium アプリモードで独立ウィンドウを立ち上げる"""
    start_server_in_thread()
    print(f"🐾 歌詞正規化エディタ デスクトップアプリを起動中... ({APP_URL})")

    # 1. PyWebView が利用可能な場合
    try:
        import webview
        window = webview.create_window(
            title="🐾 歌詞正規化エディタ (Lyrics Regex Editor)",
            url=APP_URL,
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
        ["google-chrome", f"--app={APP_URL}", "--window-size=1320,860"],
        ["chromium-browser", f"--app={APP_URL}", "--window-size=1320,860"],
        ["chromium", f"--app={APP_URL}", "--window-size=1320,860"],
        ["microsoft-edge", f"--app={APP_URL}", "--window-size=1320,860"],
    ]

    for cmd in chrome_cmds:
        try:
            subprocess.run(cmd, check=True)
            return
        except Exception:
            continue

    # 3. フォールバック: 標準ブラウザで開く
    import webbrowser
    webbrowser.open(APP_URL)

if __name__ == "__main__":
    launch_desktop_app()
