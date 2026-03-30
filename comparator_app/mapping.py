import re


DEFAULT_MAPPING_TEXT = """# base_regex => secondary_key_pattern
^angleerrortocam1-lobe(\\d+)$ => angleerrorcam1-lobe\\1
^angleofcam1toref$ => angleofcam1toref
^diametromancal([a-g])$ => diametromancal\\1
^diamancal([a-g])$ => diametromancal\\1
^measdiam-([a-g])$ => diametromancal\\1
^cirmancal([a-g])$ => roundness-\\1
"""


def parse_mapping_rules(raw_text: str) -> list[tuple[re.Pattern[str], str]]:
    rules: list[tuple[re.Pattern[str], str]] = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=>" not in stripped:
            continue
        left, right = stripped.split("=>", 1)
        left = left.strip()
        right = right.strip()
        try:
            rules.append((re.compile(left), right))
        except re.error as exc:
            raise ValueError(f"Regra invalida: {stripped} ({exc})") from exc
    return rules


def apply_mapping(base_key: str, rules: list[tuple[re.Pattern[str], str]]) -> str:
    for pattern, replacement in rules:
        if pattern.search(base_key):
            return pattern.sub(replacement, base_key)
    return base_key
