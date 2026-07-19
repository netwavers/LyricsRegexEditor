import re
from typing import List, Dict, Any

class LyricsGenerator:
    """
    全トークンの selected（または text）を書き戻し、
    メタタグやカッコを破壊せずに Suno/Udio 向けの歌唱用プレーンテキストを再構築するクラス。
    """

    def generate(self, tokens: List[Dict[str, Any]], auto_spacing: bool = False, vowel_opt: bool = False, fix_particle_ha: bool = False) -> str:
        """
        トークンリストから最終歌唱プロンプト文字列を再構築します。
        auto_spacing: 言葉の切れ目（漢字・数字・英語）にスペースを挿入
        vowel_opt: 長音・母音伸ばし変換ルールを適用
        fix_particle_ha: Suno歌唱向け助詞『は』➔『わ』発音補正
        """
        output_parts = []
        for token in tokens:
            t_type = token.get("type", "plain")
            val = token.get("selected", token.get("text", ""))

            # メタタグ・改行・カッコ内プロンプト（演奏指示・コード進行）以外のテキスト要素に対する装飾
            if t_type not in ["meta_tag", "newline", "parenthesized"]:
                if vowel_opt:
                    val = self.optimize_vowels(val)
                if fix_particle_ha:
                    val = self.fix_particle_ha(val)
                if auto_spacing and t_type in ["kanji", "number", "english"]:
                    val = " " + val + " "

            output_parts.append(val)

        result = "".join(output_parts)

        if fix_particle_ha:
            # トークン境界をまたぐ助詞『は』の全体補正（例: 「君」トークン + 「は」トークン）
            result = self.fix_particle_ha(result)

        if auto_spacing:
            # 連続スペースや改行前後のスペースを整形
            result = re.sub(r'[ \t]+', ' ', result)
            result = re.sub(r' ?\n ?', '\n', result)
            result = result.strip()

        return result

    def fix_particle_ha(self, text: str) -> str:
        """Suno歌唱向け助詞『は』➔『わ』発音補正ロジック"""
        # 1. 漢字・数字・英字の直後に接続する助詞『は』を『わ』に置換（例: 君は, 100年は, AIは）
        res = re.sub(r'(?<=[\u4E00-\u9FFF0-9a-zA-Z])は(?=[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\s\n、。!！?？〜ー,.]|$|［|\[|\(|（)', 'わ', text)
        # 2. ひらがな接続表現 (ては, では, くは, には, ことは, ものは, それは, わたしは, ぼくは) の助詞『は』
        res = re.sub(r'(?<=[てでくに全ともれちれ])は(?=[\s\n、。!！?？〜ー,.]|$|［|\[|\(|（|\u4E00-\u9FFF|\u3040-\u309F|\u30A0-\u30FF)', 'わ', res)
        return res

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
