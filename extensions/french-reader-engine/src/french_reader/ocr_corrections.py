import re

# Verb fragments strongly suggesting subject "il".
_IL_VERBS = (
    r"est|était|sera|serait|"
    r"a|avait|aura|aurait|"
    r"ne|n'|n\u2019|"
    r"se|s'|s\u2019|"
    r"l'|l\u2019|"
    r"lui|va|vient|faut|fallait|"
    r"dit|disait|fait|faisait|"
    r"peut|pouvait|doit|devait|"
    r"semble|semblait|reste|restait|"
    r"devient|devenait|trouve|trouvait|"
    r"veut|voulait|sait|savait|"
    r"voit|voyait|entend|entendait|"
    r"comprend|comprenait|explique|expliquait"
)

# Verb forms that strongly suggest subject "ils" (exclude ambiguous n'/se/s'/l').
_ILS_UNIQUE_VERBS = (
    r"sont|étaient|seront|seraient|"
    r"ont|avaient|auront|auraient|"
    r"leur|les|"
    r"vont|allaient|viennent|venaient|"
    r"disent|disaient|font|faisaient|"
    r"peuvent|pouvaient|doivent|devaient|"
    r"semblent|semblaient|restent|restaient|"
    r"trouvent|trouvaient|veulent|voulaient|"
    r"expliquent|expliquaient|inquiètent|inquiétaient"
)

_ILS_ALL_VERBS = (
    _ILS_UNIQUE_VERBS
    + r"|ne|n'|n\u2019|se|s'|s\u2019|l'|l\u2019"
)

# OCR misreads for "Il" (not plain lowercase "il").
_IL_MISREAD = r"(?:\|\||\|l|1l|lI|I1|iI|Ii|l1|\|I|IL)"

_IL_CONTEXT = rf"(^|[.!?…»\"]\s*|\n\s*)({_IL_MISREAD})\s+(?={_IL_VERBS}\b)"
_IL_BEFORE_VERB = re.compile(_IL_CONTEXT, re.MULTILINE)

# Uppercase I alone (missing "l") before a singular verb.
_I_ALONE = re.compile(rf"(^|[.!?…»\"]\s*|\n\s*|\s)I\s+(?={_IL_VERBS}\b)", re.MULTILINE)

# Circumflex on I (Î / î / Îl) — invalid for French "il".
_IL_CIRCUMFLEX = re.compile(r"(?:[Îî]|I\u0302)l\b")

_ILS_MISREAD = r"(?:I1s|1ls|\|ls|lls|ILS|I\s+ls)"
_ILS_CONTEXT = rf"(^|[.!?…»\"]\s*|\n\s*|\s)({_ILS_MISREAD})\s+(?={_ILS_ALL_VERBS}\b)"
_ILS_BEFORE_VERB = re.compile(_ILS_CONTEXT, re.IGNORECASE | re.MULTILINE)

# Uppercase I alone before a clearly plural verb.
_I_BEFORE_ILS = re.compile(
    rf"(^|[.!?…»\"]\s*|\n\s*|\s)I\s+(?={_ILS_UNIQUE_VERBS}\b)",
    re.MULTILINE,
)


def apply_ocr_corrections(text: str) -> str:
    if not text:
        return ""

    corrected = text
    corrected = _ILS_BEFORE_VERB.sub(r"\1Ils ", corrected)
    corrected = _I_BEFORE_ILS.sub(r"\1Ils ", corrected)
    corrected = _IL_CIRCUMFLEX.sub("Il", corrected)
    corrected = _IL_BEFORE_VERB.sub(r"\1Il ", corrected)
    corrected = _I_ALONE.sub(r"\1Il ", corrected)
    return corrected
