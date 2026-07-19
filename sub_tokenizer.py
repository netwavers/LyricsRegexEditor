import re
from typing import List, Dict, Any
from dict_data import get_kanji_choices, get_english_choices, generate_number_choices

class SubTokenizer:
    """
    アナライザーから受け取ったノードを詳細なトークンに細分化し、
    読みの選択肢 (choices) や選択中アイテム (selected) を付与するクラス。
    """

    # 正規表現パターン
    NUM_PATTERN = re.compile(r'(\d+)')
    ENG_PATTERN = re.compile(r'([A-Za-z]+)')

    def tokenize_nodes(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tokens = []
        token_counter = 0

        for node in nodes:
            # 解析非対象のノード（メタタグ、改行など）
            if not node.get("analyze", False):
                tokens.append({
                    "id": node["id"],
                    "text": node["text"],
                    "type": node["type"],
                    "has_choices": False,
                    "choices": [],
                    "selected": node["text"]
                })
                continue

            # カッコ内テキスト ( ... ) や （ ... ） は演奏指示・コード進行等のプロンプトのため変換対象外（保護）
            if node["type"] == "parenthesized":
                token_counter += 1
                tokens.append({
                    "id": f"sub_p_{token_counter:04d}",
                    "text": node["text"],
                    "type": "parenthesized",
                    "has_choices": False,
                    "choices": [],
                    "selected": node["text"]
                })
                continue

            # 通常テキストノードの解析
            sub_tokens = self._tokenize_text(node["text"], token_counter)
            token_counter += len(sub_tokens)
            tokens.extend(sub_tokens)

        return tokens

    def _tokenize_text(self, text: str, start_index: int) -> List[Dict[str, Any]]:
        """
        テキスト文字列を漢字（辞書ヒット語句）、数字、英語、普通テキストに分割します。
        """
        sub_tokens = []
        counter = start_index

        # まず既知の漢字（多音字）キーワードでマッチング
        # 代表的な漢字キーワードを正規表現パターンにまとめる
        from dict_data import get_kanji_choices_dict
        choices_dict = get_kanji_choices_dict()
        kanji_words = sorted(choices_dict.keys(), key=len, reverse=True)
        kanji_regex_str = "|".join([re.escape(w) for w in kanji_words])
        
        # 漢字・数字・英語・その他でパターン作成
        # 1文字以上の漢字も抽出・カスタム入力対象にする
        if kanji_regex_str:
            pattern = re.compile(rf'({kanji_regex_str}|[\u4e00-\u9fff]+|\d+|[A-Za-z]+)')
        else:
            pattern = re.compile(r'([\u4e00-\u9fff]+|\d+|[A-Za-z]+)')

        parts = pattern.split(text)
        for part in parts:
            if not part:
                continue

            counter += 1
            token_id = f"sub_{counter:04d}"

            # 1. 辞書登録漢字
            if part in choices_dict:
                choices = list(choices_dict[part])
                sub_tokens.append({
                    "id": token_id,
                    "text": part,
                    "type": "kanji",
                    "has_choices": True,
                    "choices": choices,
                    "selected": choices[0]
                })
            # 2. 辞書未登録の漢字連続
            elif re.fullmatch(r'[\u4e00-\u9fff]+', part):
                sub_tokens.append({
                    "id": token_id,
                    "text": part,
                    "type": "kanji",
                    "has_choices": False,
                    "choices": [part, "(カスタム入力)"],
                    "selected": part
                })
            # 2. 数字
            elif self.NUM_PATTERN.fullmatch(part):
                choices = generate_number_choices(part)
                sub_tokens.append({
                    "id": token_id,
                    "text": part,
                    "type": "number",
                    "has_choices": True,
                    "choices": choices,
                    "selected": choices[0]
                })
            # 3. 英単語
            elif self.ENG_PATTERN.fullmatch(part):
                eng_choices = get_english_choices(part)
                if eng_choices:
                    sub_tokens.append({
                        "id": token_id,
                        "text": part,
                        "type": "english",
                        "has_choices": True,
                        "choices": eng_choices,
                        "selected": eng_choices[0]
                    })
                else:
                    # 未登録英単語
                    sub_tokens.append({
                        "id": token_id,
                        "text": part,
                        "type": "english",
                        "has_choices": False,
                        "choices": [],
                        "selected": part
                    })
            # 4. 平文（ひらがな、カタカナ、記号など）
            else:
                sub_tokens.append({
                    "id": token_id,
                    "text": part,
                    "type": "plain",
                    "has_choices": False,
                    "choices": [],
                    "selected": part
                })

        return sub_tokens


if __name__ == "__main__":
    from analyzer import LyricsAnalyzer
    sample = "[Verse 1]\n明日(Yeah)100光年の宇宙へ"
    analyzer = LyricsAnalyzer()
    nodes = analyzer.analyze(sample)
    
    tokenizer = SubTokenizer()
    tokens = tokenizer.tokenize_nodes(nodes)
    import json
    print(json.dumps(tokens, ensure_ascii=False, indent=2))
