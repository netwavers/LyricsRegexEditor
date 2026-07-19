import re
from typing import List, Dict, Any

class LyricsGenerator:
    """
    全トークンの selected（または text）を書き戻し、
    メタタグやカッコを破壊せずに Suno/Udio 向けの歌唱用プレーンテキストを再構築するクラス。
    """

    def generate(self, tokens: List[Dict[str, Any]], auto_spacing: bool = False, vowel_opt: bool = False) -> str:
        """
        トークンリストから最終歌唱プロンプト文字列を再構築します。
        auto_spacing: 言葉の切れ目（漢字・数字・英語）にスペースを挿入
        vowel_opt: 長音・母音伸ばし変換ルールを適用
        """
        output_parts = []
        for token in tokens:
            t_type = token.get("type", "plain")
            val = token.get("selected", token.get("text", ""))

            # メタタグ・改行・カッコ内プロンプト（演奏指示・コード進行）以外のテキスト要素に対する装飾
            if t_type not in ["meta_tag", "newline", "parenthesized"]:
                if vowel_opt:
                    val = self.optimize_vowels(val)
                if auto_spacing and t_type in ["kanji", "number", "english"]:
                    val = " " + val + " "

            output_parts.append(val)

        result = "".join(output_parts)

        if auto_spacing:
            # 連続スペースや改行前後のスペースを整形
            result = re.sub(r'[ \t]+', ' ', result)
            result = re.sub(r' ?\n ?', '\n', result)
            result = result.strip()

        return result

    def optimize_vowels(self, text: str) -> str:
        """歌唱発声を明瞭にするための長音・母音伸ばし変換"""
        replacements = [
            # 個別・特殊パターンを優先
            (r'てー', 'てえ'),
            (r'ねー', 'ねえ'),
            (r'そう', 'そお'),
            (r'どう', 'どお'),
            (r'ほう', 'ほお'),
            # 五十音段グループごとの長音変換
            (r'([あかさたなはまやらわがざだばぱ])ー', r'\1あ'),
            (r'([いきしちにひみりぎじぢびぴ])ー', r'\1い'),
            (r'([うくすつぬふむゆるぐずづぶぷ])ー', r'\1う'),
            (r'([えけせてねへめれげぜでべぺ])ー', r'\1え'),
            (r'([おこそとのほもよろをごぞどぼぽ])ー', r'\1お'),
        ]
        res = text
        for pat, rep in replacements:
            res = re.sub(pat, rep, res)
        return res


if __name__ == "__main__":
    from analyzer import LyricsAnalyzer
    from sub_tokenizer import SubTokenizer

    sample = "[Verse 1]\n明日(Yeah)100光年の宇宙へ\nそう思うてー"
    nodes = LyricsAnalyzer().analyze(sample)
    tokens = SubTokenizer().tokenize_nodes(nodes)

    for t in tokens:
        if t.get("text") == "宇宙":
            t["selected"] = "そら"

    generator = LyricsGenerator()
    res = generator.generate(tokens, auto_spacing=True, vowel_opt=True)
    print("生成結果 (装飾ON):")
    print(res)
