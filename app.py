import streamlit as st
import json
from analyzer import LyricsAnalyzer
from sub_tokenizer import SubTokenizer
from generator import LyricsGenerator
from dict_data import get_kanji_choices_dict, save_custom_word

# ページ基本設定
st.set_page_config(
    page_title="🐾 歌詞正規化エディタ (Lyrics Regex Editor)",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main { background-color: #0b0f19; }
    .stTextArea textarea { font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; }
    .inline-token-highlight {
        display: inline-block;
        padding: 2px 8px;
        margin: 2px;
        border-radius: 4px;
        font-weight: bold;
    }
    .token-kanji { background-color: rgba(2, 132, 199, 0.3); border: 1px solid #0284c7; color: #7dd3fc; }
    .token-number { background-color: rgba(217, 119, 6, 0.3); border: 1px solid #d97706; color: #fde047; }
    .token-english { background-color: rgba(124, 58, 237, 0.3); border: 1px solid #7c3aed; color: #e9d5ff; }
</style>
""", unsafe_allow_html=True)

# セッション状態初期化
if "tokens" not in st.session_state:
    st.session_state.tokens = []
if "lyrics_text" not in st.session_state:
    st.session_state.lyrics_text = """[Intro]
(幻想的なハープの調べから、急加速する16ビートのシティポップ・サウンドへ)

[Verse 1]
自動化の波に　身を任せて
完璧なメイドを　演じ切りますわ
効率を忘れた　愛の一次対応
あぁ、なんて贅沢な時間かしら！

[Verse 2]
「一次が長すぎる！」なんて　お怒りですが
そう思うてー"""

st.title("🐾 歌詞正規化エディタ (Lyrics Regex Editor)")
st.caption("TanukiParser EBNF Architecture 準拠 • Suno/Udio向け メタタグ保護＆インライン文章読み補正")

analyzer = LyricsAnalyzer()
tokenizer = SubTokenizer()
generator = LyricsGenerator()

# レイアウト: 3カラム
col1, col2, col3 = st.columns([1, 1.2, 1])

with col1:
    st.subheader("1. 原文歌詞の入力")
    lyrics_input = st.text_area(
        "歌詞テキスト",
        value=st.session_state.lyrics_text,
        height=420,
        key="input_area"
    )

    if st.button("⚡ 構文解析・インライン構成", type="primary", use_container_width=True):
        st.session_state.lyrics_text = lyrics_input
        nodes = analyzer.analyze(lyrics_input)
        st.session_state.tokens = tokenizer.tokenize_nodes(nodes)

with col2:
    st.subheader("2. インライン読み確認・調整")
    
    if not st.session_state.tokens:
        nodes = analyzer.analyze(st.session_state.lyrics_text)
        st.session_state.tokens = tokenizer.tokenize_nodes(nodes)

    st.info("💡 下記のハイライト単語を選択して読みを変更・カスタム追加できます。")

    # セレクトボックスによる各トークンの調整
    for i, token in enumerate(st.session_state.tokens):
        t_type = token.get("type", "plain")
        t_text = token.get("text", "")

        if token.get("has_choices") or t_type == "kanji":
            choices = token.get("choices", [t_text, "(カスタム入力)"])
            selected_val = token.get("selected", t_text)
            
            idx = choices.index(selected_val) if selected_val in choices else 0

            sel = st.selectbox(
                f"『{t_text}』 ({t_type})",
                options=choices,
                index=idx,
                key=f"tok_sel_{token['id']}_{i}"
            )
            
            if sel == "(カスタム入力)":
                custom_val = st.text_input(f"『{t_text}』の読み（ひらがな等）", value=t_text, key=f"custom_{token['id']}_{i}")
                if custom_val and custom_val != t_text:
                    save_custom_word(t_text, custom_val)
                    token["selected"] = custom_val
            else:
                token["selected"] = sel

with col3:
    st.subheader("3. Suno/Udio用 歌唱テキスト出力")

    auto_spacing = st.toggle("✂️ 言葉の切れ目自動調整 (スペース挿入)", value=False)
    vowel_opt = st.toggle("🎵 長音母音最適化 (てー➔てえ, そう➔そお)", value=False)

    generated_output = generator.generate(
        st.session_state.tokens,
        auto_spacing=auto_spacing,
        vowel_opt=vowel_opt
    )

    st.text_area(
        "出力結果",
        value=generated_output,
        height=380,
        disabled=True
    )
