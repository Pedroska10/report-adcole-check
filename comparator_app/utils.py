import re
import unicodedata


def normalize_key(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text)
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    raw = folded.lower().strip()
    raw = raw.replace("[", "").replace("]", "")
    raw = raw.replace("_", "")
    raw = raw.replace(".", "")
    raw = raw.replace(" ", "")
    raw = re.sub(r"[^a-z0-9\-]", "", raw)
    return raw


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None

    token = value.strip()
    if not token:
        return None

    if token.startswith("-,"):
        token = "-0" + token[1:]
    elif token.startswith(","):
        token = "0" + token

    token = token.replace(".", "") if token.count(".") > 1 else token
    token = token.replace(",", ".")

    try:
        return float(token)
    except ValueError:
        return None


def parse_numeric_tokens(text: str) -> list[float]:
    tokens = re.findall(r"-?,\d+|-?\d+,\d+|-?\d+", text)
    parsed: list[float] = []
    for token in tokens:
        if token.startswith("-,"):
            token = "-0" + token[1:]
        elif token.startswith(","):
            token = "0" + token
        token = token.replace(",", ".")
        try:
            parsed.append(float(token))
        except ValueError:
            continue
    return parsed


def compute_exceedance(measured: float | None, lower: float | None, upper: float | None) -> float | None:
    if measured is None or lower is None or upper is None:
        return None
    if measured < lower:
        return measured - lower
    if measured > upper:
        return measured - upper
    return 0.0


def format_display_name(raw_name: str) -> str:
    text = raw_name
    text = text.replace("_", " ")
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    text = text.replace("-Lobe", " - Lobe ")
    text = text.replace("-", " - ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_numeric_token(token: str) -> bool:
    return bool(re.fullmatch(r"-?(?:\d+[.,]\d+|\d+|,\d+)", token))


def safe_filename_token(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "", text)
    return cleaned or "resultado"
