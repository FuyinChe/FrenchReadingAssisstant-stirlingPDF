from typing import Literal

ExplainMode = Literal["translate", "vocabulary", "grammar"]

_TARGET_LABELS = {
    "zh": "Simplified Chinese",
    "en": "English",
    "fr": "French",
}


def target_language_label(code: str) -> str:
    return _TARGET_LABELS.get(code.lower(), code)


def build_messages(
    text: str,
    mode: ExplainMode,
    target_lang: str = "zh",
) -> list[dict[str, str]]:
    target = target_language_label(target_lang)
    cleaned = text.strip()

    if mode == "translate":
        system = (
            "You are a professional French translator for comics, bandes dessinées, "
            "and literary PDFs. Translate faithfully and naturally. "
            "Preserve dialogue tone. Output ONLY the translation."
        )
        user = f"Translate the following French text into {target}.\n\nFrench:\n{cleaned}"
    elif mode == "vocabulary":
        system = (
            "You help French learners reading PDFs. For each difficult or unfamiliar word "
            f"or idiom in the excerpt, give a concise note in {target}. "
            "Always include French IPA pronunciation (International Phonetic Alphabet) "
            "for every headword. Use this format, one item per line:\n"
            "• **word** /ipa/ — meaning\n"
            "For multi-word expressions, put IPA after the whole phrase. "
            "Do not skip pronunciation. Output only the vocabulary list."
        )
        user = (
            f"List difficult vocabulary from this French excerpt. "
            f"Include IPA for each word, then explain in {target}:\n\n{cleaned}"
        )
    else:
        system = (
            "You help French learners. Explain notable grammar patterns briefly "
            f"in {target}. Use short bullet points when helpful."
        )
        user = f"Explain grammar in this French excerpt:\n\n{cleaned}"

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
