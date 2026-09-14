import re


MACHINE_OPTIONS = ("Adcole 911", "Adcole LX", "Adcole 1200DH")
DEFAULT_PART = ""

TEMPLATE_68_MAPPING_TEXT = """# base_regex => secondary_key_pattern
^angleerrortocam1-lobe(\\d+)$ => angleerrorcam1-lobe\\1
^angleofcam1toref$ => angleofcam1toref
^diametromancal([a-g])$ => diametromancal\\1
^diamancal([a-g])$ => diametromancal\\1
^measdiam-([a-g])$ => diametromancal\\1
^cirmancal([a-g])$ => roundness-\\1
^diametromancal([a-g])center$ => diametrocentral\\1
^diametromancal([a-g])inf$ => diametroinferior\\1
^diametromancal([a-g])sup$ => diametrosuperior\\1
^erroanguloreferi6i(\\d+)$ => angleerrortocam11a6-lobe\\1
^anguloentreassuperficies$ => nguloentreassuperfcies
^desvioemrelacaoaosmancaisadjace$ => desvioemrelaoaosmancaisadjacentesa
"""

TEMPLATE_63_MAPPING_TEXT = r"""# base_regex => secondary_key_pattern
^angleerrortocam1-lobe((?:[1-9]|10))$ => angleerrorcam1-lobe\1
^angleofcam1toref$ => angleofcam1toref
^diametromancal([a-f])$ => diametromancal\1
^diamancal([a-f])$ => diametromancal\1
^measdiam-([a-f])$ => diametromancal\1
^cirmancal([a-f])$ => roundness-\1
^diametromancal([a-f])center$ => diametrocentral\1
^diametromancal([a-f])inf$ => diametroinferior\1
^diametromancal([a-f])sup$ => diametrosuperior\1
^erroanguloreferi6i((?:[1-9]|10))$ => angleerrortocam11a6-lobe\1
^anguloentreassuperficies$ => nguloentreassuperfcies
^desvioemrelacaoaosmancaisadjace$ => desvioemrelaoaosmancaisadjacentesa
"""

TEMPLATE_500_MAPPING_TEXT = r"""# base_regex => secondary_key_pattern
^angleerrorcam11a6-lobe(\d+)$ => angleerrorcam11a6-lobe\1
^angleerroruz-lobe(\d+)$ => angleerroruz-lobe\1
^angleofcam1toref$ => angleofcam1toref
^bc-radius-error-lobe(\d+)$ => bc-radius-error-lobe\1
^bc-runout-lobe(\d+)$ => bc-runout-lobe\1
^concave/convex-lobe(\d+)$ => concave/convex-lobe\1
^cylindricity-([a-g])$ => cylindricity-\1
^diametro([a-g])\[center\]$ => diametro\1[center]
^diametro([a-g])\[inf\]$ => diametro\1[inf]
^diametro([a-g])\[sup\]$ => diametro\1[sup]
^lift-difference-lobe(\d+)$ => lift-difference-lobe\1
^lift-error-bc-lobe(\d+)$ => lift-error-bc-lobe\1
^lift-error-closing-ramp-lobe(\d+)$ => lift-error-closing-ramp-lobe\1
^lift-error-nose-lobe(\d+)$ => lift-error-nose-lobe\1
^lift-error-opening-ramp-lobe(\d+)$ => lift-error-opening-ramp-lobe\1
^meas-diam-\[center\]-([a-g])$ => meas-diam-[center]-\1
^meas-diam-\[inf\]-([a-g])$ => meas-diam-[inf]-\1
^meas-diam-\[sup\]-([a-g])$ => meas-diam-[sup]-\1
^parallelism-([a-g])$ => parallelism-\1
^parallelism-lobe(\d+)$ => parallelism-lobe\1
^runout-\[(adj|ext|gage)\]-([a-g])$ => runout-[\1]-\2
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
    "1865230": TEMPLATE_68_MAPPING_TEXT,
    "2208002": TEMPLATE_68_MAPPING_TEXT,
    "2181766": TEMPLATE_63_MAPPING_TEXT,
    "1832910": TEMPLATE_63_MAPPING_TEXT,
    "3073595": TEMPLATE_500_MAPPING_TEXT,
    "3070996": TEMPLATE_500_MAPPING_TEXT,
    "3073597": TEMPLATE_500_MAPPING_TEXT,
    "EC-001": TEMPLATE_68_MAPPING_TEXT,
    "EC-002": TEMPLATE_68_MAPPING_TEXT,
    "EC-003": TEMPLATE_68_MAPPING_TEXT,
    "EC-004": TEMPLATE_68_MAPPING_TEXT,
    "VR-001": VIRABREQUIM_MAPPING_TEXT,
    "VR-002": VIRABREQUIM_MAPPING_TEXT,
    "VR-003": VIRABREQUIM_MAPPING_TEXT,
    "VR-101": VIRABREQUIM_MAPPING_TEXT,
    "VR-102": VIRABREQUIM_MAPPING_TEXT,
    "VR-103": VIRABREQUIM_MAPPING_TEXT,
    "padrao": TEMPLATE_68_MAPPING_TEXT,
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
