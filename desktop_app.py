import os
import sys
import time
import threading
import urllib.request
from web_server import run_server

DEFAULT_PORT = 8088

def start_server_and_wait():
    """Web サーバーを自動起動し、接続確認が取れるまで待機"""
    import web_server

    # サーバーをバックグラウンドスレッドで自動起動
    server_thread = threading.Thread(target=web_server.run_server, kwargs={"port": DEFAULT_PORT}, daemon=True)
    server_thread.start()

    # スレッドがポートにバインドし、HTTP 200 を返すまで待機（最大 5 秒）
    for _ in range(50):
        time.sleep(0.1)
        port = web_server.ACTIVE_PORT
        if port is not None:
            url = f"http://127.0.0.1:{port}"
            try:
                with urllib.request.urlopen(url, timeout=0.5) as resp:
                    if resp.status == 200:
                        return url
            except Exception:
                pass

    active_port = web_server.ACTIVE_PORT or DEFAULT_PORT
    return f"http://127.0.0.1:{active_port}"

def launch_desktop_app():
    """PyWebView または Chrome/Chromium アプリモードで独立ウィンドウを立ち上げる"""
    base_url = start_server_and_wait()
    # 物理キャッシュバスター（ミリ秒タイムスタンプ）
    app_url = f"{base_url}/index.html?v={int(time.time() * 1000)}"
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
        webview.start(private_mode=True)
        return
    except Exception as e:
        print(f"PyWebView 起動不可 (Chrome アプリモードに切り替えます): {e}")

    # 2. Chrome / Chromium の --app モード（ブラウザ枠のない完全アプリ表示）
    import subprocess
    chrome_cmds = [
        ["google-chrome", f"--app={app_url}", "--window-size=1320,860", "--disk-cache-dir=/dev/null"],
        ["chromium-browser", f"--app={app_url}", "--window-size=1320,860", "--disk-cache-dir=/dev/null"],
        ["chromium", f"--app={app_url}", "--window-size=1320,860", "--disk-cache-dir=/dev/null"],
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
