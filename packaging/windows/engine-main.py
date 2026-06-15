"""PyInstaller entrypoint for the French Reader engine (Windows portable build)."""

from __future__ import annotations

import multiprocessing


def main() -> None:
    import uvicorn

    uvicorn.run(
        "french_reader.main:app",
        host="127.0.0.1",
        port=5002,
        log_level="info",
    )


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
