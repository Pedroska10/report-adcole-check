import re


MACHINE_OPTIONS = ("Adcole 911", "Adcole LX", "Adcole 1200DH")
DEFAULT_PART = ""

DEFAULT_MAPPING_TEXT = """# base_regex => secondary_key_pattern
^angleerrortocam1-lobe(\\d+)$ => angleerrorcam1-lobe\\1
^angleofcam1toref$ => angleofcam1toref
^diametromancal([a-g])$ => diametromancal\\1
^diamancal([a-g])$ => diametromancal\\1
^measdiam-([a-g])$ => diametromancal\\1
^cirmancal([a-g])$ => roundness-\\1
"""

VIRABREQUIM_MAPPING_TEXT = """# base_regex => secondary_key_pattern
^diametromancal([a-g])$ => diametromancal\\1
^diamancal([a-g])$ => diametromancal\\1
^measdiam-([a-g])$ => diametromancal\\1
^cirmancal([a-g])$ => roundness-\\1
^angleerrortocam1-lobe(\\d+)$ => angleerrorcam1-lobe\\1
"""

MACHINE_PART_CODES = {
    "Adcole 911": (
        "150991",
        "2960401",
        "2960403",
        "2967762",
        "2967688",
        "2960405",
        "2967686",
        "2960408",
        "2972987",
        "2972988",
        "2972992",
        "2972990",
        "2972989",
        "2972991",
        "2972993",
        "2975310",
        "2975312",
        "2975314",
        "2975316",
        "1865230",
        "2208002",
        "2181766",
        "1832910",
        "2878172",
        "2508549",
        "2903706",
        "3071014",
        "3070996",
        "3073595",
        "3073597",
        "3106033",
        "3069232",
        "3148774",
    ),
    "Adcole LX": ("VR-001", "VR-002", "VR-003"),
    "Adcole 1200DH": ("VR-101", "VR-102", "VR-103"),
}

PART_MAPPING_PRESETS = {
    "EC-001": DEFAULT_MAPPING_TEXT,
    "EC-002": DEFAULT_MAPPING_TEXT,
    "EC-003": DEFAULT_MAPPING_TEXT,
    "EC-004": DEFAULT_MAPPING_TEXT,
    "VR-001": VIRABREQUIM_MAPPING_TEXT,
    "VR-002": VIRABREQUIM_MAPPING_TEXT,
    "VR-003": VIRABREQUIM_MAPPING_TEXT,
    "VR-101": VIRABREQUIM_MAPPING_TEXT,
    "VR-102": VIRABREQUIM_MAPPING_TEXT,
    "VR-103": VIRABREQUIM_MAPPING_TEXT,
    "padrao": DEFAULT_MAPPING_TEXT,
}


def get_part_codes_for_machine(machine_name: str | None) -> tuple[str, ...]:
    if not machine_name:
        return MACHINE_PART_CODES.get("Adcole 911", ())
    return MACHINE_PART_CODES.get(machine_name, MACHINE_PART_CODES.get("Adcole 911", ()))


def normalize_part_name(part_name: str | None) -> str:
    value = (part_name or DEFAULT_PART).strip()
    if value not in PART_MAPPING_PRESETS:
        return "padrao"
    return value


def get_mapping_text_for_selection(part_name: str | None, machine_names: list[str] | tuple[str, ...] | None = None) -> str:
    normalized_part = normalize_part_name(part_name)
    preset = PART_MAPPING_PRESETS.get(
        normalized_part, PART_MAPPING_PRESETS["padrao"])
    if not machine_names:
        return preset
    machines = [m.strip() for m in machine_names if m and m.strip()]
    if not machines:
        return preset
    return preset


def get_mapping_rules_for_selection(part_name: str | None, machine_names: list[str] | tuple[str, ...] | None = None) -> list[tuple[re.Pattern[str], str]]:
    return parse_mapping_rules(
        get_mapping_text_for_selection(part_name, machine_names)
    )


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
