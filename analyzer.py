import re
from typing import List, Dict, Any

class LyricsAnalyzer:
    """
    歌詞テキストを「メタタグ [...]」「カッコ ( ... )」「改行」「一般テキスト」に構造分離するアナライザー。
    仕様書 2.1 / 3.1 準拠
    """

    # メタタグ [Verse 1] や ［Chorus］ などをマッチするパターン
    META_PATTERN = re.compile(r'(\[[^\]\r\n]+\]|［[^］\r\n]+］)')
    # カッコ (Yeah) や （コーラス） などをマッチするパターン
    PAREN_PATTERN = re.compile(r'(\([^\)\r\n]+\)|（[^）\r\n]+）)')

    def analyze(self, text: str) -> List[Dict[str, Any]]:
        """
        歌詞文字列を解析し、初期ノードリストを作成します。
        """
        nodes = []
        node_counter = 0

        # 改行でまず行単位、またはToken単位に分解する
        lines = text.splitlines(keepends=True)

        for line in lines:
            # 改行のみの行
            if line == '\n' or line == '\r\n':
                node_counter += 1
                nodes.append({
                    "id": f"node_{node_counter:03d}",
                    "text": line,
                    "type": "newline",
                    "analyze": False
                })
                continue

            # 改行コードを末尾から分離
            line_text = line
            line_ending = ""
            if line_text.endswith('\r\n'):
                line_ending = '\r\n'
                line_text = line_text[:-2]
            elif line_text.endswith('\n'):
                line_ending = '\n'
                line_text = line_text[:-1]

            # 行内を メタタグ [...] で分割
            parts = self.META_PATTERN.split(line_text)
            for part in parts:
                if not part:
                    continue

                if self.META_PATTERN.fullmatch(part):
                    # メタタグノード（編集不可・解析対象外）
                    node_counter += 1
                    nodes.append({
                        "id": f"node_{node_counter:03d}",
                        "text": part,
                        "type": "meta_tag",
                        "analyze": False
                    })
                else:
                    # カッコ ( ... ) でさらに分割
                    sub_parts = self.PAREN_PATTERN.split(part)
                    for sub_part in sub_parts:
                        if not sub_part:
                            continue
                        
                        if self.PAREN_PATTERN.fullmatch(sub_part):
                            # カッコ内ノード
                            # カッコ記号自体は保護しつつ内部のテキストを細分化できるよう分離処理するか、
                            # ノードとして登録
                            node_counter += 1
                            nodes.append({
                                "id": f"node_{node_counter:03d}",
                                "text": sub_part,
                                "type": "parenthesized",
                                "analyze": True # カッコ内テキストも読み補正の対象
                            })
                        else:
                            # 通常テキストノード（解析対象）
                            node_counter += 1
                            nodes.append({
                                "id": f"node_{node_counter:03d}",
                                "text": sub_part,
                                "type": "text",
                                "analyze": True
                            })

            # 改行ノード
            if line_ending:
                node_counter += 1
                nodes.append({
                    "id": f"node_{node_counter:03d}",
                    "text": line_ending,
                    "type": "newline",
                    "analyze": False
                })

        return nodes


if __name__ == "__main__":
    sample = "[Verse 1]\n明日(Yeah)100光年の宇宙へ\n[Chorus]\nFly away!"
    analyzer = LyricsAnalyzer()
    res = analyzer.analyze(sample)
    import json
    print(json.dumps(res, ensure_ascii=False, indent=2))
