#!/bin/bash
# 🐾 歌詞正規化エディタ ワンクリック起動スクリプト (Web App Mode)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "🐾 歌詞正規化エディタ Web サーバーを起動中..."
python3 web_server.py &
SERVER_PID=$!

sleep 1

if command -v xdg-open > /dev/null; then
    xdg-open "http://127.0.0.1:8088"
elif command -v open > /dev/null; then
    open "http://127.0.0.1:8088"
fi

wait $SERVER_PID
