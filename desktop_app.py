import os
import sys
import time
import threading
import urllib.request
from web_server import run_server

DEFAULT_PORT = 8088
actual_bound_port = None

def start_server_and_wait():
    """Web サーバーを自前で自動起動し、接続確認が取れるまで待機"""
    global actual_bound_port

    def server_runner():
        global actual_bound_port
        import socketserver
        socketserver.TCPServer.allow_reuse_address = True
        from web_server import LyricsRegexEditorHandler
        for p in range(DEFAULT_PORT, DEFAULT_PORT + 20):
            try:
                httpd = socketserver.TCPServer(("127.0.0.1", p), LyricsRegexEditorHandler)
                actual_bound_port = p
                print(f"🐾 歌詞正規化エディタ Webサーバー起動成功: http://127.0.0.1:{p}")
                httpd.serve_forever()
                break
            except OSError:
                continue

    server_thread = threading.Thread(target=server_runner, daemon=True)
    server_thread.start()

    # スレッドがポートにバインドし、HTTP 200 を返すまで待機
    for _ in range(50):
        time.sleep(0.1)
        if actual_bound_port is not None:
            url = f"http://127.0.0.1:{actual_bound_port}"
            try:
                with urllib.request.urlopen(url, timeout=0.5) as resp:
                    if resp.status == 200:
                        return url
            except Exception:
                pass

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
