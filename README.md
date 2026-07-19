# 🐾 歌詞正規化エディタ (Lyrics Regex Editor)

**Lyrics Regex Editor** は、Suno / Udio などの AI 歌唱モデル向けに歌詞プロンプトの読みを自動解析・調整し、視覚的なインライン UI で確認・カスタム学習できる正規化＆プロンプト最適化エディタです。

---

## ✨ 主な特徴

- 📖 **インライン文章風 UI**
  - 改行や構造（`[Verse 1]` やカッコ内の演奏指示）を完全に維持したままテキスト紙面スタイルで表示。
  - 多音字や英数字などの補正候補がある単語は、文章内でスマートなマーカー下線ハイライト表示。
  - ハイライト単語をクリックすると、直下にポップオーバー選択メニューが出現。
- 🔒 **演奏指示・コード進行プロンプトの完全保護**
  - 角カッコ `[...]` のメタタグに加え、丸カッコ `(...)` や `（...）` 内のコード進行・演奏指示（例: `(F#maj9 - G#m7/F#)`）は誤変換されず無傷で自動保護。
- 💾 **`my_dict.json` によるカスタム読みの自動学習・永続化**
  - ユーザーが登録した読み（ひらがな等）は `my_dict.json` に永久保存され、次回解析時に選択肢の先頭に優先ロード。
- 🎵 **歌唱 AI 向け自動装飾機能**
  - **✂️ 言葉の切れ目自動調整 (`auto_spacing`)**: 単語間に自動でスペースを挿入し、AIの単語認識率を向上。
  - **🎵 長音母音最適化 (`vowel_opt`)**: `てー` ➔ `てえ`, `そう` ➔ `そお` 等の長音・母音伸ばし変換でAI歌唱の発声を明瞭化。
- 🔊 **TTS 音声試聴機能**
  - Web Speech API を活用し、演奏指示プロンプトを除外した「純歌詞プロンプト」のみをスムーズに音声試聴。
- 💻 **マルチ OS 対応・独立デスクトップアプリ環境**
  - Linux / Windows / macOS でブラウザ枠のない専用デスクトップアプリケーションとしてワンクリック起動。

---

## 📁 ファイル構成

```text
LyricsRegexEditor/
├── dict_data.py           # 基本辞書および my_dict.json 読み込み・保存層
├── my_dict.json           # ユーザー定義カスタム読みの永続化辞書
├── analyzer.py            # AST/EBNF 歌詞構造構文解析器
├── sub_tokenizer.py       # 詳細トークナイザー（漢字・数字・英語・保護ノード分離）
├── generator.py           # 歌唱 AI 向けプロンプト再構築・自動装飾エンジン
├── web_server.py          # 軽量 HTTP API サーバー (Port: 8088)
├── index.html             # インライン文章 UI フロントエンド
├── app.py                 # Streamlit 版 UI
├── desktop_app.py         # 専用デスクトップアプリランチャー
├── launch_desktop.sh      # Linux 用ワンクリック起動スクリプト
├── launch_desktop.bat     # Windows 用ワンクリック起動スクリプト
├── launch_desktop.command # macOS 用ワンクリック起動スクリプト
├── test_pipeline.py       # パイプライン全自動結合アサートテスト
├── README.md              # 本ドキュメント
└── USER_MANUAL.md         # ユーザーマニュアル（操作説明書）
```

---

## 🚀 起動方法

依存関係は Python 標準ライブラリのみで構成されているため、特別なインストールなしで即座に動作します！

### Web アプリケーションとして起動（推奨）

ワンクリックで Web サーバーが起動し、自動的に既定のブラウザでアプリが開きます。

- **Linux**: `./launch_desktop.sh` または `python3 web_server.py`
- **Windows**: `launch_desktop.bat` をダブルクリック、または `python web_server.py`
- **macOS**: `launch_desktop.command` をダブルクリック、または `python3 web_server.py`

ブラウザアクセスURL: `http://127.0.0.1:8088`

```bash
python3 web_server.py
```
起動後、ブラウザで [http://localhost:8088](http://localhost:8088) にアクセスしてください。

---

## 🧪 テストの実行

```bash
python3 test_pipeline.py
```
全自動結合テスト（カスタム辞書学習・AI歌唱装飾・カッコ内プロンプト保護）が実行されます。
