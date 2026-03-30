import os
import re
from datetime import datetime
from pathlib import Path

import pdfplumber

from .utils import safe_filename_token


def get_desktop_dir() -> Path:
    candidates = []

    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        profile = Path(user_profile)
        candidates.extend(
            [
                profile / "Desktop",
                profile / "Área de Trabalho",
                profile / "OneDrive" / "Desktop",
                profile / "OneDrive" / "Área de Trabalho",
            ]
        )

    home = Path.home()
    candidates.extend(
        [
            home / "Desktop",
            home / "Área de Trabalho",
            home / "OneDrive" / "Desktop",
            home / "OneDrive" / "Área de Trabalho",
        ]
    )

    for path in candidates:
        if path.exists() and path.is_dir():
            return path

    return Path.cwd()


def program_prefix_from_pdf(pdf_path: Path) -> str | None:
    pattern = re.compile(r"Program:\s*([^\s]+)", re.IGNORECASE)

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                match = pattern.search(line)
                if match:
                    raw = match.group(1).strip()
                    return raw[:11]
    return None


def suggested_output_name(secondary_pdf_path: Path | None = None) -> str:
    now_suffix = datetime.now().strftime("%H%M%S")
    prefix = "resultado"

    if secondary_pdf_path and secondary_pdf_path.exists():
        extracted = program_prefix_from_pdf(secondary_pdf_path)
        if extracted:
            prefix = extracted

    prefix = safe_filename_token(prefix)
    return f"{prefix}{now_suffix}.xlsx"
