import os
import json
from typing import List, Dict, Optional

MY_DICT_PATH = os.path.join(os.path.dirname(__file__), "my_dict.json")

def load_user_dict() -> Dict[str, List[str]]:
    """my_dict.json からユーザー定義読み辞書を読み込みます"""
    if os.path.exists(MY_DICT_PATH):
        try:
            with open(MY_DICT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_custom_word(word: str, reading: str) -> List[str]:
    """新しいカスタム読みを my_dict.json に保存・学習します"""
    user_dict = load_user_dict()
    if word not in user_dict:
        user_dict[word] = []
    
    # 重複除去して先頭に挿入
    if reading in user_dict[word]:
        user_dict[word].remove(reading)
    user_dict[word].insert(0, reading)

    try:
        with open(MY_DICT_PATH, "w", encoding="utf-8") as f:
            json.dump(user_dict, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving my_dict.json: {e}")
        
    return get_kanji_choices(word)

# 要注意漢字・多音字・当て字辞書
BASE_KANJI_CHOICES_DICT: Dict[str, List[str]] = {
    "一次": ["ひとつぎ", "いちじ", "一次"],
    "明日": ["あした", "あす", "みょうにち", "明日"],
    "宇宙": ["うちゅう", "そら", "こすも", "宇宙"],
    "未来": ["みらい", "あす", "未来"],
    "運命": ["うんめい", "さだめ", "運命"],
    "永遠": ["えいえん", "とわ", "永遠"],
    "世界": ["せかい", "くに", "世界"],
    "本気": ["ほんき", "マジ", "本気"],
    "理由": ["りゆう", "わけ", "理由"],
    "真実": ["しんじつ", "ほんとう", "真実"],
    "瞬間": ["しゅんかん", "とき", "瞬間"],
    "少女": ["しょうじょ", "おとめ", "少女"],
    "黄金": ["おうごん", "こがね", "きん", "黄金"],
    "今日": ["きょう", "こんにち", "今日"],
    "昨日": ["きのう", "さくじつ", "昨日"],
    "風": ["かぜ", "ふう", "風"],
    "光": ["ひかり", "こう", "光"],
    "空": ["そら", "くう", "空"],
    "海": ["うみ", "かい", "海"],
    "星": ["ほし", "せい", "星"],
    "愛": ["あい", "いとし", "愛"],
}

def get_kanji_choices_dict() -> Dict[str, List[str]]:
    """ユーザーカスタム辞書 (my_dict.json) と基本辞書を統合して最新の辞書を返します"""
    merged = {}
    user_dict = load_user_dict()
    
    # 基本辞書コピー
    for k, v in BASE_KANJI_CHOICES_DICT.items():
        merged[k] = list(v)

    # ユーザー定義で上書き・先頭追加
    for k, v in user_dict.items():
        if k in merged:
            for item in reversed(v):
                if item in merged[k]:
                    merged[k].remove(item)
                merged[k].insert(0, item)
        else:
            merged[k] = list(v) + [k]
            
    return merged

def get_kanji_choices(word: str) -> Optional[List[str]]:
    """漢字単語に対する最新の候補を返します"""
    choices_dict = get_kanji_choices_dict()
    return choices_dict.get(word)

# 英単語・カタカナ/ひらがな変換辞書
ENGLISH_CHOICES_DICT: Dict[str, List[str]] = {
    "yeah": ["yeah", "いぇー", "いぇあ", "やー"],
    "love": ["love", "らぶ", "ラブ"],
    "fly": ["fly", "ふらい", "フライ"],
    "dream": ["dream", "どりーむ", "ドリーム"],
    "heart": ["heart", "はーと", "ハート"],
    "night": ["night", "ないと", "ナイト"],
    "shine": ["shine", "しゃいん", "シャイン"],
    "world": ["world", "わーるど", "ワールド"],
    "go": ["go", "ごー", "ゴー"],
    "baby": ["baby", "べいびー", "ベイベー"],
    "music": ["music", "みゅーじっく", "ミュージック"],
    "life": ["life", "らいふ", "ライフ"],
}

# 数字読みの基本テーブル
DIGIT_JP = ["ぜろ", "いち", "に", "さん", "よん", "ご", "ろく", "なな", "はち", "きゅう"]
DIGIT_EN = ["ぜろ", "わん", "つー", "すりー", "ふぉー", "ふぁいぶ", "しっくす", "せぶん", "えいと", "ないん"]

def get_english_choices(word: str) -> Optional[List[str]]:
    """英単語に対する候補を返します"""
    lower_word = word.lower()
    if lower_word in ENGLISH_CHOICES_DICT:
        return ENGLISH_CHOICES_DICT[lower_word]
    return None


def generate_number_choices(num_str: str) -> List[str]:
    """
    数字文字列（例: "100", "24"）から3パターンの読み候補を自動生成します。
    仕様書 3.3 準拠:
    1. 日本語数え (ひゃく / にじゅうよん)
    2. 英語数え/カタカナ (わんはんどれっど / つーふぉー)
    3. 棒読み (いちぜろぜろ / によん)
    """
    choices = []
    
    # 1. 簡易日本語読み (数値に変換可能な場合)
    try:
        val = int(num_str)
        jp_read = convert_num_to_jp(val)
        choices.append(jp_read)
    except ValueError:
        pass

    # 2. 英語読み / 簡易対応
    if num_str == "100":
        choices.append("わんはんどれっど")
    elif num_str == "1":
        choices.append("わん")
    elif num_str == "2":
        choices.append("つー")
    elif num_str == "3":
        choices.append("すりー")
    else:
        # 桁ごとの英語読み連結
        en_str = "".join([DIGIT_EN[int(d)] for d in num_str if d.isdigit()])
        if en_str:
            choices.append(en_str)

    # 3. 棒読み (各桁の数字読み)
    stick_read = "".join([DIGIT_JP[int(d)] for d in num_str if d.isdigit()])
    if stick_read and stick_read not in choices:
        choices.append(stick_read)

    # 原文も末尾に選択肢として維持
    if num_str not in choices:
        choices.append(num_str)

    # 重複を除去しつつ順序維持
    seen = set()
    unique_choices = []
    for c in choices:
        if c not in seen:
            seen.add(c)
            unique_choices.append(c)

    return unique_choices


def convert_num_to_jp(n: int) -> str:
    """1〜9999までの簡易日本語数え機能"""
    if n == 0:
        return "ぜろ"
    if n == 100:
        return "ひゃく"
    if n == 1000:
        return "せん"
    
    units = ["", "じゅう", "ひゃく", "せん"]
    digits = ["", "いち", "に", "さん", "よん", "ご", "ろく", "なな", "はち", "きゅう"]

    # 100までの簡易変換
    if 1 <= n < 10:
        return digits[n]
    elif 10 <= n < 100:
        ten = n // 10
        one = n % 10
        ten_str = ("じゅう" if ten == 1 else digits[ten] + "じゅう")
        one_str = digits[one]
        return ten_str + one_str
    elif 100 <= n < 1000:
        hundred = n // 100
        rest = n % 100
        h_str = ("ひゃく" if hundred == 1 else ("さんびゃく" if hundred == 3 else ("ろっぴゃく" if hundred == 6 else ("はっぴゃく" if hundred == 8 else digits[hundred] + "ひゃく"))))
        return h_str + (convert_num_to_jp(rest) if rest > 0 else "")
    
    # 棒読みフォールバック
    return "".join([DIGIT_JP[int(d)] for d in str(n)])
