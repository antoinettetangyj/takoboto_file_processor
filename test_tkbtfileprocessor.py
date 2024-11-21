from tkbtfileprocessor import get_data, check_kana, get_pos
import pytest


def test_get_data():

    #possible inputs expected by get_data():
    #hiragana (e.g. ちゃくしん) - the basic japanese syllabary, typically used for words of japanese origin. the form is more curved.
    #katakana (e.g. メロディ) - secondary japanese syllabary, typically used to represent foreign words. the form is more angular/sharp.
    #kanji (e.g. 着信) - gives meaning/context to japanese syllables　-　橋 (hashi, bridge)　vs　箸 (hashi, chopsticks). Not all words have kanji.

    #it is possible to mix and match the above three scripts to form compound expressions. this is typically how they appear in japanese text
    #hiragana + katakana - ちゃくしんメロディ
    #kanji + katakana - 着信メロディ
    #kanji + hiragana - 締め上げる

    #for learning, japanese can be also be represented using roman alphabets (romaji).
    #romaji is one of the possible outputs of the extract() function.

    test_cases = {

        "開始": {
            "word": "開始",
            "pr": "-",
            "alt": "-",
            "roma": "-"
        },

        "しがない": {
            "word": "しがない",
            "pr": "-",
            "alt": "-",
            "roma": "shiganai"
            },

        "でか, デカ": {
            "word": "でか",
            "pr": "-",
            "alt": "デカ",
            "roma": "deka"
        },

        "ズキズキ, ずきずき": {
            "word": "ズキズキ",
            "pr": "ずきずき",
            "alt": "ずきずき",
            "roma": "zukizuki"
        },

        "締め上げる, しめあげる, 絞め上げる": {
            "word": "締め上げる",
            "pr": "しめあげる",
            "alt": "絞め上げる",
            "roma": "shimeageru"
            },

        "着信メロディ, ちゃくしんメロディ, 着信メロディー, ちゃくしんメロディー": {
            "word": "着信メロディ",
            "pr": "ちゃくしんめろでぃ",
            "alt": "ちゃくしんメロディ, 着信メロディー, ちゃくしんメロディー",
            "roma": "chakushinmerodei"
            },

    }

    for text in test_cases:
        for mode in test_cases[text]:
            assert get_data(text, mode) == test_cases[text][mode]

    #test sys.exit() for invalid inputs
    exit_cases = ["w", "pro", "al", "rom"]

    for case in exit_cases:
        with pytest.raises(SystemExit):
            get_data("しがない", case)
            get_data("ズキズキ, ずきずき", case)


def test_check_kana():

    true_cases = {
        "hira": {"締め上げる", "しがない", "ちゃくしんメロディー"},
        "kata": {"着信メロディ", "メロディ", "ちゃくしんメロディー"},
    }

    false_cases = {
        "hira": {"ズキズキ", "デカ", "deka"},
        "kata": {"ずきずき", "でか", "deka"},
    }

    #check output for True cases
    for mode in true_cases:
        for word in true_cases[mode]:
            assert check_kana(word, mode) == True

    #check output for False cases
    for mode in false_cases:
        for word in false_cases[mode]:
            assert check_kana(word, mode) == False


def test_get_pos():
    
    """
    In japanese, there are two kinds of adjectives: na- and i-adjectives.
    """

    pos_type = {
        "noun": {"着信メロディ", "霞", "婦警"},
        "verb": {"怒鳴る", "預ける", "尋ねる"},
        "i-adj": {"しがない", "偉い", "そそっかしい"},
        "na-adj": {"肝心", "厄介", "無責任"},
        "expressions": {"お開きにする", "有ろう事か", "覚悟を決める"},
    }

    #check that correct pos data is retrieved for each word
    for pos in pos_type:
        for word in pos_type[pos]:
            assert pos in get_pos(word)