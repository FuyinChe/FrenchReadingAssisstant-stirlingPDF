import re

from french_reader.ocr_corrections import apply_ocr_corrections

_FRENCH_PUNCT_ONLY = re.compile(r"^[:;?!…]+$")
_FRENCH_CLOSING_PUNCT = re.compile(r"^[,.\»\)\]!?…]+")
_SENTENCE_BOUNDARY = re.compile(
    r"(?<=[.!?…»\"])\s+(?=[A-ZÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ«\"0-9Il])"
)
_ABBREV_BEFORE_PERIOD = re.compile(
    r"\b(?:M|Mme|Dr|Mlle|etc|vol|p|pp|art|cf|ex|fig)\.\s*$",
    re.IGNORECASE,
)


def _attach_to_previous(previous: str, fragment: str) -> str:
    if _FRENCH_PUNCT_ONLY.match(fragment):
        return f"{previous} {fragment}"
    if fragment and fragment[0] in ",.)»":
        return previous + fragment
    if fragment and fragment[0] in "?:;!":
        return f"{previous} {fragment}"
    return f"{previous} {fragment}"


def _merge_visual_lines(raw_lines: list[str]) -> list[str]:
    """Merge OCR/page line breaks into one continuous flow."""
    merged: list[str] = []
    for raw in raw_lines:
        line = raw.strip()
        if not line:
            continue

        if merged and merged[-1].endswith("-"):
            merged[-1] = merged[-1][:-1] + line
            continue

        if merged and merged[-1] != "":
            if _FRENCH_PUNCT_ONLY.match(line) or (len(line) <= 2 and line in ":;?!"):
                merged[-1] = _attach_to_previous(merged[-1], line)
                continue
            if _FRENCH_CLOSING_PUNCT.match(line):
                merged[-1] = _attach_to_previous(merged[-1], line)
                continue

        merged.append(line)
    return merged


def _split_french_sentences(paragraph: str) -> list[str]:
    """Split flowing text at major French sentence punctuation for TTS pauses."""
    paragraph = re.sub(r"[ \t]+", " ", paragraph.strip())
    if not paragraph:
        return []

    chunks = _SENTENCE_BOUNDARY.split(paragraph)
    if len(chunks) == 1:
        chunks = re.split(r"(?<=[.!?…»\"])\s+", paragraph)

    sentences: list[str] = []
    pending = ""
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        candidate = f"{pending} {chunk}".strip() if pending else chunk
        if _ABBREV_BEFORE_PERIOD.search(candidate) and chunk != chunks[-1]:
            pending = candidate
            continue
        sentences.append(candidate)
        pending = ""

    if pending:
        if sentences:
            sentences[-1] = f"{sentences[-1]} {pending}".strip()
        else:
            sentences.append(pending.strip())

    return sentences or [paragraph]


def _apply_french_typography(text: str) -> str:
    result = re.sub(r"[ \t]+", " ", text)
    result = result.replace("« ", "«").replace(" »", "»")
    result = re.sub(r" ([,.\»\)\]])", r"\1", result)
    return result.strip()


def postprocess_french_text(text: str) -> str:
    """
    Normalize OCR output for reading and TTS.

    A cropped speech-bubble region is treated as one flowing utterance:
    - All visual / Tesseract paragraph wraps are joined with spaces.
    - Line breaks appear only between sentences (. ! ? …) for TTS pauses.
    """
    if not text:
        return ""

    merged = _merge_visual_lines(text.splitlines())
    flowing = apply_ocr_corrections(" ".join(merged))
    sentences = _split_french_sentences(flowing)
    return "\n".join(_apply_french_typography(sentence) for sentence in sentences)


def extract_tts_lines(text: str) -> list[str]:
    """Non-empty lines from postprocessed text, one per sentence/utterance."""
    if not text:
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]
