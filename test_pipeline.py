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

        # 3. カッコ内演奏指示・コード進行プロンプトの完全保護テスト
        code_lyrics = "[Intro]\n(F#maj9 - G#m7/F# - Bm7/F#)\n賑やかな ネットの海は"
        code_nodes = self.analyzer.analyze(code_lyrics)
        code_tokens = self.tokenizer.tokenize_nodes(code_nodes)

        # カッコ内ノードが has_choices: False かつ無傷か
        paren_token = next(t for t in code_tokens if t["type"] == "parenthesized")
        self.assertFalse(paren_token["has_choices"])
        self.assertEqual(paren_token["text"], "(F#maj9 - G#m7/F# - Bm7/F#)")

        code_res = self.generator.generate(code_tokens, auto_spacing=True, vowel_opt=True)
        self.assertIn("(F#maj9 - G#m7/F# - Bm7/F#)", code_res)
        self.assertNotIn("きゅう", code_res)
        self.assertNotIn("なな", code_res)

        print("\n✅ フェーズ2生成＆カッコ保護テスト結果:")
        print(code_res)

if __name__ == "__main__":
    unittest.main()
