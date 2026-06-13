from french_reader.ocr_service import _assemble_tesseract_lines
from french_reader.text_postprocess import extract_tts_lines, postprocess_french_text


def test_hyphen_merge():
    assert postprocess_french_text("Bon-\njour") == "Bonjour"


def test_whitespace_collapse():
    assert postprocess_french_text("Salut   monde") == "Salut monde"


def test_word_per_line_becomes_flowing_paragraph():
    raw = "\n".join(
        [
            "Papa",
            "rassure",
            "Alice",
            ":",
            "papi",
            "n'aura",
            "plus",
            "soif,",
            "ni",
            "faim.",
        ]
    )
    assert postprocess_french_text(raw) == (
        "Papa rassure Alice : papi n'aura plus soif, ni faim."
    )


def test_punctuation_only_line_attaches():
    assert postprocess_french_text("Alice\n:") == "Alice :"


def test_visual_wraps_do_not_break_sentences():
    raw = "\n".join(
        [
            "Papa rassure Alice :",
            "papi n'aura plus soif,",
            "ni faim, ni froid.",
            "Il ne sera plus heureux.",
        ]
    )
    assert postprocess_french_text(raw) == (
        "Papa rassure Alice : papi n'aura plus soif, ni faim, ni froid.\n"
        "Il ne sera plus heureux."
    )


def test_paragraph_breaks_preserved():
    assert postprocess_french_text("Première bulle.\n\nDeuxième bulle.") == (
        "Première bulle.\n\nDeuxième bulle."
    )


def test_long_speech_bubble_splits_by_sentence_for_tts():
    raw = "\n".join(
        [
            "Papa rassure Alice :",
            "papi n'aura plus soif, ni faim, ni froid, ni chaud, ni mal.",
            "Il ne s'ennuiera plus non plus.",
            "En fait, il ne sera plus heureux ni triste.",
            "Le corps de papi ne sent plus rien, ni les bobos, ni les câlins.",
            "Il est mort, c'est tout.",
        ]
    )
    result = postprocess_french_text(raw)
    assert result.split("\n") == [
        "Papa rassure Alice : papi n'aura plus soif, ni faim, ni froid, ni chaud, ni mal.",
        "Il ne s'ennuiera plus non plus.",
        "En fait, il ne sera plus heureux ni triste.",
        "Le corps de papi ne sent plus rien, ni les bobos, ni les câlins.",
        "Il est mort, c'est tout.",
    ]
    assert extract_tts_lines(result) == result.split("\n")


def test_assemble_tesseract_groups_words_by_line():
    data = {
        "text": ["Papa", "rassure", "Alice", ":", "papi", "n'aura"],
        "conf": [90, 88, 92, 85, 90, 91],
        "block_num": [1, 1, 1, 1, 1, 1],
        "par_num": [1, 1, 1, 1, 1, 1],
        "line_num": [1, 1, 1, 2, 3, 3],
        "word_num": [1, 2, 3, 1, 1, 2],
    }
    lines = _assemble_tesseract_lines(data)
    assert lines[0] == ("Papa rassure Alice", 0.9)
    assert lines[1][0] == ":"
    assert lines[2][0] == "papi n'aura"

    text = postprocess_french_text("\n".join(line for line, _ in lines if line))
    assert text == "Papa rassure Alice : papi n'aura"
