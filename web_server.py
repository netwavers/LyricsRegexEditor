import http.server
import socketserver
import json
import os
from analyzer import LyricsAnalyzer
from sub_tokenizer import SubTokenizer
from generator import LyricsGenerator

PORT = 8088

class LyricsRegexEditorHandler(http.server.SimpleHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        clean_path = self.path.split('?')[0]
        if clean_path in ('/', '/index.html'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self._send_cors_headers()
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__), 'index.html'), 'rb') as f:
                self.wfile.write(f.read())
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            req_data = json.loads(body)
        except Exception as e:
            print(f"❌ JSON parse error: {e}")
            req_data = {}

        print(f"📥 POST {self.path} (Body length: {len(body)})")

        # 常に最新モジュールからフレッシュインスタンスを作成
        analyzer = LyricsAnalyzer()
        tokenizer = SubTokenizer()
        generator = LyricsGenerator()

        if self.path == '/api/analyze':
            text = req_data.get('text', '')
            nodes = analyzer.analyze(text)
            tokens = tokenizer.tokenize_nodes(nodes)
            print(f"  └> Analyzed: {len(nodes)} nodes, {len(tokens)} tokens")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            res = json.dumps({"tokens": tokens}, ensure_ascii=False)
            self.wfile.write(res.encode('utf-8'))

        elif self.path == '/api/generate':
            tokens = req_data.get('tokens', [])
            auto_spacing = req_data.get('auto_spacing', False)
            vowel_opt = req_data.get('vowel_opt', False)
            fix_particle_ha = req_data.get('fix_particle_ha', False)

            generated_text = generator.generate(
                tokens,
                auto_spacing=auto_spacing,
                vowel_opt=vowel_opt,
                fix_particle_ha=fix_particle_ha
            )
            print(f"  └> Generated text length: {len(generated_text)}")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            res = json.dumps({"text": generated_text}, ensure_ascii=False)
            self.wfile.write(res.encode('utf-8'))

        elif self.path == '/api/save_custom':
            word = req_data.get('word', '')
            reading = req_data.get('reading', '')

            from dict_data import save_custom_word
            updated_choices = save_custom_word(word, reading)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            res = json.dumps({"status": "ok", "choices": updated_choices}, ensure_ascii=False)
            self.wfile.write(res.encode('utf-8'))

        else:
            self.send_error(404, "Not Found")


ACTIVE_PORT = None

def run_server(port: int = PORT):
    global ACTIVE_PORT
    socketserver.TCPServer.allow_reuse_address = True
    for p in range(port, port + 20):
        try:
            httpd = socketserver.TCPServer(("127.0.0.1", p), LyricsRegexEditorHandler)
            ACTIVE_PORT = p
            print(f"🐾 歌詞正規化エディタ Webサーバー起動成功: http://127.0.0.1:{p}")
            httpd.serve_forever()
            break
        except Exception as e:
            continue

if __name__ == "__main__":
    run_server()
