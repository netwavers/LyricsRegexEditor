import os
import sys
import re
from typing import List, Dict, Any

from lyrics_lexer import LyricsLexer
from lyrics_parser import LyricsParser, TokenType

class LyricsAnalyzer:
    """
    EBNF構文解析器 (LyricsParser) を用いて、歌詞テキストを
    「メタタグ [...]」「カッコ ( ... )」「改行」「一般テキスト」に構造分離する公式アナライザー。
    """

    def analyze(self, text: str) -> List[Dict[str, Any]]:
        nodes = []
        node_counter = 0

        lines = text.splitlines(keepends=True)

        for line in lines:
            if line == '\n' or line == '\r\n':
                node_counter += 1
                nodes.append({
                    "id": f"node_{node_counter:03d}",
                    "text": line,
                    "type": "newline",
                    "analyze": False
                })
                continue

            line_text = line
            line_ending = ""
            if line_text.endswith('\r\n'):
                line_ending = '\r\n'
                line_text = line_text[:-2]
            elif line_text.endswith('\n'):
                line_ending = '\n'
                line_text = line_text[:-1]

            parsed_chunks = self._split_line_ebnf(line_text)
            for chunk_text, chunk_type in parsed_chunks:
                node_counter += 1
                if chunk_type == "meta_tag":
                    nodes.append({
                        "id": f"node_{node_counter:03d}",
                        "text": chunk_text,
                        "type": "meta_tag",
                        "analyze": False
                    })
                elif chunk_type == "parenthesized":
                    nodes.append({
                        "id": f"node_{node_counter:03d}",
                        "text": chunk_text,
                        "type": "parenthesized",
                        "analyze": True
                    })
                else:
                    nodes.append({
                        "id": f"node_{node_counter:03d}",
                        "text": chunk_text,
                        "type": "text",
                        "analyze": True
                    })

            if line_ending:
                node_counter += 1
                nodes.append({
                    "id": f"node_{node_counter:03d}",
                    "text": line_ending,
                    "type": "newline",
                    "analyze": False
                })

        return nodes

    def _split_line_ebnf(self, line_text: str) -> List[tuple]:
        if not line_text:
            return []

        chunks = []
        raw_tags = []
        try:
            lexer = LyricsLexer(line_text)
            parser = LyricsParser(lexer)

            def tag_h(tag_text, tag_type):
                t_type = "meta_tag" if tag_type == "B" else "parenthesized"
                raw_tags.append((tag_text, t_type))
                return ""

            parser.tag_handler = tag_h
            parser.token = lexer.get_token()

            current_text = []

            while parser.token and parser.token.token_type is not None:
                tt = parser.token.token_type
                if tt in (TokenType.OPEN_BRACKET, TokenType.OPEN_BRACKET_FULL, TokenType.OPEN_PAREN, TokenType.OPEN_PAREN_FULL, TokenType.ANGLE_LEFT):
                    if current_text:
                        chunks.append((''.join(current_text), 'text'))
                        current_text.clear()

                    raw_tags.clear()
                    prev_pos = lexer.token_pos
                    res = parser.tag()
                    if res is None or lexer.token_pos == prev_pos:
                        current_text.append(parser.token.content)
                        parser.token = lexer.get_token()
                    elif raw_tags:
                        top_tag_text, top_tag_type = raw_tags[-1]
                        chunks.append((top_tag_text, top_tag_type))
                else:
                    current_text.append(parser.token.content)
                    parser.token = lexer.get_token()

            if current_text:
                chunks.append((''.join(current_text), 'text'))

        except Exception as e:
            chunks = [(line_text, 'text')]

        return chunks


if __name__ == "__main__":
    sample = "AIさんの指先が　魔法をかけるわ\n(A#m7 - D#7(11) - G#m7 - C#7/F)\n(A#m7 - D#7（11） - G#m7 - C#7/F)\nけれど気づいたときには　お財布は空っぽ"
    analyzer = LyricsAnalyzer()
    res = analyzer.analyze(sample)
    import json
    print(json.dumps(res, ensure_ascii=False, indent=2))
