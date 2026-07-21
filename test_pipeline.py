import unittest
import os
import json
from analyzer import LyricsAnalyzer
from sub_tokenizer import SubTokenizer
from generator import LyricsGenerator
from dict_data import save_custom_word, load_user_dict, get_kanji_choices_dict

class TestLyricsRegexEditorPhase2(unittest.TestCase):
    def setUp(self):
        self.analyzer = LyricsAnalyzer()
        self.tokenizer = SubTokenizer()
        self.generator = LyricsGenerator()

    def test_phase2_full_pipeline(self):
        # 1. カスタム辞書学習テスト (my_dict.json)
        save_custom_word("概念", "がいねん")
        user_dict = load_user_dict()
        self.assertIn("概念", user_dict)
        self.assertIn("がいねん", user_dict["概念"])

        choices_dict = get_kanji_choices_dict()
        self.assertIn("概念", choices_dict)
        self.assertEqual(choices_dict["概念"][0], "がいねん")

        # 2. 自動装飾（長音母音最適化 & スペーシング）テスト
        lyrics = "[Verse 1]\n概念の波に乗りてー\nそう思うてー"
        nodes = self.analyzer.analyze(lyrics)
        tokens = self.tokenizer.tokenize_nodes(nodes)

        # 「概念」の読みを「がいねん」に選択
        for t in tokens:
            if t.get("text") == "概念":
                t["selected"] = "がいねん"

        # 3. カッコ内演奏指示・コード進行プロンプトの完全保護テスト (ネスト対応・全角半角混在対応)
        code_lyrics = "[Intro]\n(F#maj9 - G#m7/F# - Bm7/F#)\n(A#m7 - D#7(11) - G#m7 - C#7/F)\n（全角コード - D#7(11) - G#m7）\n(半角コード - D#7（11） - G#m7)\n賑やかな ネットの海は"
        code_nodes = self.analyzer.analyze(code_lyrics)
        code_tokens = self.tokenizer.tokenize_nodes(code_nodes)

        # カッコ内ノードが has_choices: False かつ無傷か
        paren_tokens = [t for t in code_tokens if t["type"] == "parenthesized"]
        self.assertEqual(len(paren_tokens), 4)
        self.assertEqual(paren_tokens[0]["text"], "(F#maj9 - G#m7/F# - Bm7/F#)")
        self.assertEqual(paren_tokens[1]["text"], "(A#m7 - D#7(11) - G#m7 - C#7/F)")
        self.assertEqual(paren_tokens[2]["text"], "（全角コード - D#7(11) - G#m7）")
        self.assertEqual(paren_tokens[3]["text"], "(半角コード - D#7（11） - G#m7)")

        code_res = self.generator.generate(code_tokens, auto_spacing=True, vowel_opt=True)
        self.assertIn("(F#maj9 - G#m7/F# - Bm7/F#)", code_res)
        self.assertIn("(A#m7 - D#7(11) - G#m7 - C#7/F)", code_res)
        self.assertIn("（全角コード - D#7(11) - G#m7）", code_res)
        self.assertIn("(半角コード - D#7（11） - G#m7)", code_res)

        # 4. 助詞『は』➔『わ』発音補正テスト (Suno発音最適化)
        ha_lyrics = "君は僕の太陽\n花は綺麗に咲く"
        ha_nodes = self.analyzer.analyze(ha_lyrics)
        ha_tokens = self.tokenizer.tokenize_nodes(ha_nodes)
        ha_res = self.generator.generate(ha_tokens, fix_particle_ha=True)
        self.assertIn("君わ僕の太陽", ha_res)
        self.assertIn("花わ綺麗に咲く", ha_res) # 「花」の「は」は保護され助詞の「は」のみ「わ」に置換

        print("\n✅ フェーズ2生成＆カッコ保護＆助詞発音補正テスト結果:")
        print(code_res)
        print(ha_res)

if __name__ == "__main__":
    unittest.main()
