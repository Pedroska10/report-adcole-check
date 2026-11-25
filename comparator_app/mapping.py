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

TEMPLATE_PORTUGUESE_MAPPING_TEXT = r"""# base_regex => secondary_key_pattern
^angleerrortocam11a6-lobe([1-6])$ => erroanguloparareferenciaa6-lobe\1
^angleerrortouz-lobe([1-6])$ => anguloreferuz-lobe\1
^anguloentreassuperficies$ => anguloentreassuperficies
^distanciauparaoeixoderot$ => distanciauparaoeixoderot
^distanciazparaoeixoderot$ => distanciazparaoeixoderot
^bcradiuserror-lobe([1-9]|1[0-5])$ => raiodocirculobase-lobe\1
^bcrunout-lobe([1-9]|1[0-5])$ => desviodocirculobase-lobe\1
^bcvelocityerror-lobe([1-9]|1[0-5])$ => desviodevelocidade-lobe\1
^concaveconvex-lobe([1-9]|1[0-5])$ => concavoconvexo-lobe\1
^cylindricity-([a-g])$ => cylindricity-\1
^liftdifference-lobe([1-9]|1[0-5])$ => liftdifference-lobe\1
^liftdifferencenose-lobe([1-9]|1[0-5])$ => liftdifferencenose-lobe\1
^liftdifferenceramp-lobe([1-9]|1[0-5])$ => liftdifferenceramp-lobe\1
^lifterrorbc-lobe([1-9]|1[0-5])$ => errodeperfildoraiobase-lobe\1
^lifterrorclosingramp-lobe([1-9]|1[0-5])$ => errodeperfilfechamentodoflanco-lobe\1
^lifterrorramp-lobe([1-9]|1[0-5])$ => errodeperfilfechamentodoflanco-lobe\1
^lifterrornose-lobe([1-9]|1[0-5])$ => errodeperfiltopo-lobe\1
^lifterroropeningramp-lobe([1-9]|1[0-5])$ => errodeperfilaberturadoflanco-lobe\1
^measdiamcenter-([a-g])$ => measdiamcenter-\1
^measdiaminf-([a-g])$ => measdiaminf-\1
^measdiamsup-([a-g])$ => measdiamsup-\1
^measdiam-([a-g])$ => measdiam-\1
^parallelism-([a-g])$ => parallelism-\1
^parallelism-lobe([1-9]|1[0-5])$ => paralelismo-lobe\1
^roundness-([a-g])$ => roundness-\1
^roundness([a-g])$ => roundness-\1
^circularidadedm(72|52)$ => circularidadedm\1
^roundnessd(72|52)$ => circularidadedm\1
^diameterdm(72|52)$ => diametrodm\1
^diameterd(72|52)(?:lower|inf)$ => diametrodm\1
^diameterd(72|52)(?:upper|sup)$ => diametrodm\1
^diameterd(72|52)center$ => diametrocentraldm\1
^runoutadj-([a-g])$ => runoutadj-\1
^runoutb-c-([a-g])$ => runoutb-c-\1
^runoute-f-([a-g])$ => runoute-f-\1
^runoutext-([b-f])$ => runoutext-\1
^runoutgage-([a-g])$ => runoutgage-\1
^runout-([a-g])$ => runout-\1
^ecc-refgage-([a-f])$ => ecc-refgage-\1
^ecc-refpart-([a-f])$ => ecc-refpart-\1
^centerdeviation-lobe([1-9]|1[0-5])$ => centerdeviation-lobe\1
^tapererror-lobe([1-9]|1[0-5])$ => tapererror-lobe\1
^angleofcam1toref$ => angleofcam1toref
^angleerrortocam1-lobe([1-9]|1[0-5])$ => angleerrortocam1-lobe\1
^angleerrortopin-lobe([1-9]|1[0-5])$ => angleerrortopin-lobe\1
"""

TEMPLATE_500_MAPPING_TEXT = r"""# base_regex => secondary_key_pattern
^angleerrortocam11a6(?:-?process)?-lobe([1-6])$ => angleerrortocam11a6-lobe\1
^angleerrortouz-lobe([1-5])$ => angleerrortouz-lobe\1
^angleofcam1toref$ => angleofcam1toref
^bc-radius-error-lobe(\d+)$ => bc-radius-error-lobe\1
^bc-runout-lobe(\d+)$ => bc-runout-lobe\1
^circlebaserunout-?process-lobe([1-5])$ => runoutgage-lobe\1
^concave/convex-lobe(\d+)$ => concave/convex-lobe\1
^cylindricity-([a-g])$ => cylindricity-\1
^diameter([a-g])center$ => diametro\1center
^diameter([a-g])inf$ => diametro\1inf
^diameter([a-g])sup$ => diametro\1sup
^diameterd(52|72)lower$ => diametrod\1inf
^diameterd(52|72)center$ => diametrod\1center
^diameterd(52|72)upper$ => diametrod\1sup
^parallelismd52$ => parallellitetmotnarligandeejritningskrav-d52
^overunderparallelismd52$ => parallelitetover-underejritningskrav-d52
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
^roundnessprocess-lobe1$ => cirmancal-a
^roundnessprocess-lobe2$ => cirmancal-b
^roundnessprocess-lobe3$ => cirmancal-c
^roundnessprocess-lobe4$ => cirmancal-d
^roundnessprocess-lobe5$ => cirmancal-e
^roundnessprocess-lobe6lower$ => cirmancal-f
^roundnessprocess-lobe6upper$ => cirmancal-g
^roundness(d52|d72)$ => roundness-\1
^runout-?(adj|ext|gage)(?:-?process)?-?([a-g])$ => runout\1-\2
^runout-?(adj|gage)(?:-?process)?-?(d52|d72)$ => runout\1-\2
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
    "150991": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2960401": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2960403": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2967762": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2967688": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2960405": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2967686": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2960408": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2972987": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2972988": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2972992": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2972990": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2972989": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2972991": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2972993": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2975310": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2975312": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2975314": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2975316": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "1865230": TEMPLATE_68_MAPPING_TEXT,
    "2208002": TEMPLATE_68_MAPPING_TEXT,
    "2181766": TEMPLATE_63_MAPPING_TEXT,
    "1832910": TEMPLATE_63_MAPPING_TEXT,
    "2878172": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2508549": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "2903706": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "3071014": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "3073595": TEMPLATE_500_MAPPING_TEXT,
    "3070996": TEMPLATE_500_MAPPING_TEXT,
    "3073597": TEMPLATE_500_MAPPING_TEXT,
    "3106033": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "3069232": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
    "3148774": TEMPLATE_PORTUGUESE_MAPPING_TEXT,
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

PART_TEMPLATE_IDS = {
    "150991": "67",
    "2960401": "67",
    "2960403": "67",
    "2967762": "67",
    "2967688": "67",
    "2960405": "67",
    "2967686": "67",
    "2960408": "67",
    "2972987": "67",
    "2972988": "64",
    "2972992": "64",
    "2972990": "64",
    "2972989": "64",
    "2972991": "64",
    "2972993": "64",
    "2975310": "67",
    "2975312": "67",
    "2975314": "67",
    "2975316": "67",
    "1865230": "68",
    "2208002": "68",
    "2181766": "63",
    "1832910": "63",
    "2878172": "004",
    "2508549": "157",
    "2903706": "156",
    "3071014": "1400",
    "3070996": "500",
    "3073595": "500",
    "3073597": "500",
    "3106033": "370",
    "3069232": "5",
    "3148774": "158",
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


def get_template_id_for_part(part_name: str | None) -> str | None:
    if not part_name:
        return None
    return PART_TEMPLATE_IDS.get(part_name.strip())


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
