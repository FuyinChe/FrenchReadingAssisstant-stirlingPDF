from french_reader.ocr_corrections import apply_ocr_corrections


def test_il_pipe_before_est():
    assert apply_ocr_corrections("bobos. || est mort") == "bobos. Il est mort"


def test_il_pipe_mid_sentence():
    assert apply_ocr_corrections("|| est") == "Il est"


def test_alt_misread_1l():
    assert apply_ocr_corrections("fin. 1l est mort") == "fin. Il est mort"


def test_standalone_i_before_est():
    assert apply_ocr_corrections("câlins. I est mort") == "câlins. Il est mort"


def test_caps_il_before_est():
    assert apply_ocr_corrections("bobos. IL est mort") == "bobos. Il est mort"


def test_circumflex_il():
    assert apply_ocr_corrections("Îl est mort") == "Il est mort"
    assert apply_ocr_corrections("fin. îl ne sera plus") == "fin. Il ne sera plus"


def test_i_before_ne():
    assert apply_ocr_corrections("Alice : I n'est plus là") == "Alice : Il n'est plus là"


def test_ils_misread_i_ls():
    assert apply_ocr_corrections("I ls sont bizarres") == "Ils sont bizarres"


def test_ils_misread_i1s():
    assert apply_ocr_corrections("fin. I1s ont peur") == "fin. Ils ont peur"


def test_ils_misread_caps():
    assert apply_ocr_corrections("ILS sont bizarres") == "Ils sont bizarres"


def test_i_before_sont_becomes_ils():
    assert apply_ocr_corrections("I sont bizarres") == "Ils sont bizarres"


def test_realistic_comic_excerpt():
    raw = "En ce moment, I est inquiet. I ls expliquent : papi est malade."
    assert apply_ocr_corrections(raw) == (
        "En ce moment, Il est inquiet. Ils expliquent : papi est malade."
    )


def test_lowercase_il_unchanged():
    assert apply_ocr_corrections("En fait, il ne sera plus heureux.") == (
        "En fait, il ne sera plus heureux."
    )
