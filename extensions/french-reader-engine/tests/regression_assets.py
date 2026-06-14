from __future__ import annotations

from pathlib import Path


def regression_assets_dir() -> Path | None:
    candidates = [
        Path(__file__).resolve().parent / "fixtures" / "regression",
        Path.home()
        / ".cursor"
        / "projects"
        / "Users-fuyinche-Documents-GitHub-FrenchPdfReader"
        / "assets",
    ]
    for path in candidates:
        if path.is_dir() and any(path.glob("Screenshot_2026-06-14_at_7.*.png")):
            return path
    return None
