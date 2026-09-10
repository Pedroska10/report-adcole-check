import re
from pathlib import Path

import pdfplumber

from .models import MeasurementRow
from .utils import (
    compute_exceedance,
    format_display_name,
    is_numeric_token,
    normalize_key,
    parse_float,
    parse_numeric_tokens,
)


def parse_caracteristicas_pdf(pdf_path: Path) -> list[MeasurementRow]:
    rows: list[MeasurementRow] = []

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                line = " ".join(line.split())
                parts = line.split()

                if len(parts) < 7:
                    continue

                if not parts[0].isdigit():
                    continue

                numeric_tail: list[str] = []
                for token in reversed(parts):
                    if is_numeric_token(token):
                        numeric_tail.append(token)
                    else:
                        break

                numeric_tail.reverse()

                # Handle rows like "... - Lobe 2 0,000 -0,017 ..." where the lobe id
                # is a standalone numeric token right before measured columns.
                numeric_start_index = len(parts) - len(numeric_tail)
                if (
                    numeric_tail
                    and numeric_start_index > 0
                    and parts[numeric_start_index - 1].lower() == "lobe"
                    and re.fullmatch(r"\d+", parts[numeric_start_index] or "")
                ):
                    numeric_start_index += 1
                    numeric_tail = parts[numeric_start_index:]

                if len(numeric_tail) < 5 or len(numeric_tail) > 6:
                    continue

                name_end_index = len(parts) - len(numeric_tail)
                raw_name = " ".join(parts[1:name_end_index]).strip()
                if not raw_name:
                    continue

                name = format_display_name(raw_name)
                nominal = parse_float(numeric_tail[0])
                measured = parse_float(numeric_tail[1])
                lower = parse_float(numeric_tail[2])
                upper = parse_float(numeric_tail[3])
                deviation = parse_float(numeric_tail[4])
                exceedance = parse_float(numeric_tail[5]) if len(numeric_tail) > 5 else None

                rows.append(
                    MeasurementRow(
                        characteristic_name=name,
                        nominal_value=nominal,
                        measured_value=measured,
                        lower_limit=lower,
                        upper_limit=upper,
                        deviation=deviation,
                        exceedance=exceedance,
                    )
                )

    if not rows:
        raise ValueError("Nao foi possivel extrair linhas da tabela de caracteristicas.")

    return rows


def parse_secondary_pdf(pdf_path: Path) -> dict[str, MeasurementRow]:
    lines: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                normalized = " ".join(line.split())
                if normalized:
                    lines.append(normalized)

    data: dict[str, MeasurementRow] = {}

    journal_nominal: float | None = None
    journal_tols: list[float] | None = None
    cam_tol_pos: list[float] | None = None
    cam_tol_neg: list[float] | None = None

    for i, line in enumerate(lines):
        if line.startswith("Nom:"):
            values = parse_numeric_tokens(line)
            if values:
                value = values[0]
                if value > 50 and journal_nominal is None:
                    journal_nominal = value

        if line.startswith("Tol:"):
            values = parse_numeric_tokens(line)
            if len(values) <= 4 and not journal_tols:
                journal_tols = values
            elif len(values) >= 10 and not cam_tol_pos:
                cam_tol_pos = values
                if i + 1 < len(lines):
                    neg_values = parse_numeric_tokens(lines[i + 1])
                    if len(neg_values) >= 10:
                        cam_tol_neg = neg_values

    if cam_tol_neg and cam_tol_pos and len(cam_tol_neg) == len(cam_tol_pos):
        adjusted: list[float] = []
        for pos, neg in zip(cam_tol_pos, cam_tol_neg):
            if neg > 0 and abs(neg - pos) < 1e-12:
                adjusted.append(-pos)
            elif neg > 0 and pos > 0 and neg <= pos:
                adjusted.append(-abs(neg))
            else:
                adjusted.append(neg)
        cam_tol_neg = adjusted

    angle_ref_pattern = re.compile(
        r"Angle of cam number 1 to reference \(\s*([\d,.-]+)\s*--\s*([\d,.-]+)\)\s*([\d,.-]+)"
    )

    for line in lines:
        match = angle_ref_pattern.search(line)
        if match:
            lower = parse_float(match.group(1))
            upper = parse_float(match.group(2))
            measured = parse_float(match.group(3))
            nominal = (lower + upper) / 2.0 if lower is not None and upper is not None else None
            deviation = measured - nominal if measured is not None and nominal is not None else None
            exceedance = compute_exceedance(measured, lower, upper)
            row = MeasurementRow(
                characteristic_name="Angle of cam number 1 to reference",
                nominal_value=nominal,
                measured_value=measured,
                lower_limit=lower,
                upper_limit=upper,
                deviation=deviation,
                exceedance=exceedance,
            )
            data[normalize_key("angleofcam1toref")] = row
            break

    for line in lines:
        match = re.match(r"^([A-G])\s+(.*)$", line)
        if not match:
            continue

        journal_id = match.group(1)
        nums = parse_numeric_tokens(match.group(2))
        if len(nums) < 8:
            continue

        max_dia, min_dia, meas_dia, diameter_error, roundness, ecc_gage, axis_part, runout = nums[:8]

        diam_row = MeasurementRow(
            characteristic_name=f"Diametro Mancal {journal_id}",
            nominal_value=journal_nominal,
            measured_value=meas_dia,
            lower_limit=min_dia,
            upper_limit=max_dia,
            deviation=diameter_error,
            exceedance=compute_exceedance(meas_dia, min_dia, max_dia),
        )
        data[normalize_key(f"diametromancal{journal_id}")] = diam_row

        round_upper = journal_tols[0] if journal_tols and len(journal_tols) >= 1 else None
        part_upper = journal_tols[1] if journal_tols and len(journal_tols) >= 2 else None
        runout_upper = journal_tols[2] if journal_tols and len(journal_tols) >= 3 else None

        data[normalize_key(f"roundness-{journal_id}")] = MeasurementRow(
            characteristic_name=f"Roundness-{journal_id}",
            nominal_value=0.0,
            measured_value=roundness,
            lower_limit=0.0,
            upper_limit=round_upper,
            deviation=roundness,
            exceedance=compute_exceedance(roundness, 0.0, round_upper),
        )

        data[normalize_key(f"ecc-ref[gage]-{journal_id}")] = MeasurementRow(
            characteristic_name=f"Ecc-Ref[Gage]-{journal_id}",
            nominal_value=0.0,
            measured_value=ecc_gage,
            lower_limit=0.0,
            upper_limit=None,
            deviation=ecc_gage,
            exceedance=None,
        )

        data[normalize_key(f"ecc-ref[part]-{journal_id}")] = MeasurementRow(
            characteristic_name=f"Ecc-Ref[Part]-{journal_id}",
            nominal_value=0.0,
            measured_value=axis_part,
            lower_limit=0.0,
            upper_limit=part_upper,
            deviation=axis_part,
            exceedance=compute_exceedance(axis_part, 0.0, part_upper),
        )

        data[normalize_key(f"runout-{journal_id}")] = MeasurementRow(
            characteristic_name=f"Runout-{journal_id}",
            nominal_value=0.0,
            measured_value=runout,
            lower_limit=0.0,
            upper_limit=runout_upper,
            deviation=runout,
            exceedance=compute_exceedance(runout, 0.0, runout_upper),
        )

    tol_metric_order = [
        "angleerrortopin",
        "angleerrorcam1",
        "bcradiuserror",
        "bcrunout",
        "bcvelocityerror",
        "lifterrornose",
        "lifterrorramp",
        "liftdifferencenose",
        "liftdifferenceramp",
        "centerdeviation",
        "tapererror",
        "parallelism",
    ]

    metric_token_map = {
        "angleerrortopin": 1,
        "angleerrorcam1": 2,
        "bcradiuserror": 3,
        "bcrunout": 4,
        "bcvelocityerror": 5,
        "lifterrornose": 6,
        "lifterrorramp": 8,
        "liftdifferencenose": 10,
        "liftdifferenceramp": 12,
        "centerdeviation": 14,
        "tapererror": 15,
        "parallelism": 16,
    }

    one_sided_zero_lower = {
        "bcrunout",
        "bcvelocityerror",
        "lifterrornose",
        "lifterrorramp",
        "liftdifferencenose",
        "liftdifferenceramp",
    }

    cam_row_pattern = re.compile(r"^(\d+)\s+([AI]\d)\s+(EXH|INT)\s+(.+)$")

    for line in lines:
        match = cam_row_pattern.match(line)
        if not match:
            continue

        lobe = int(match.group(1))
        values = parse_numeric_tokens(match.group(4))
        if len(values) < 16:
            continue

        for metric in tol_metric_order:
            token_index = metric_token_map[metric] - 1
            measured = values[token_index]

            tol_index = tol_metric_order.index(metric)
            pos_tol = cam_tol_pos[tol_index] if cam_tol_pos and len(cam_tol_pos) > tol_index else None
            neg_tol = cam_tol_neg[tol_index] if cam_tol_neg and len(cam_tol_neg) > tol_index else None

            nominal = 0.0
            if metric in one_sided_zero_lower:
                lower = 0.0
            else:
                lower = neg_tol if neg_tol is not None else (-pos_tol if pos_tol is not None else None)

            upper = pos_tol
            deviation = measured - nominal
            exceedance = compute_exceedance(measured, lower, upper)

            key = normalize_key(f"{metric}-lobe{lobe}")
            data[key] = MeasurementRow(
                characteristic_name=f"{metric}-lobe{lobe}",
                nominal_value=nominal,
                measured_value=measured,
                lower_limit=lower,
                upper_limit=upper,
                deviation=deviation,
                exceedance=exceedance,
            )

    # Fallback/augmentation for the Portuguese report layout.
    pt_data = _parse_secondary_pdf_portuguese(lines)
    for key, row in pt_data.items():
        if key not in data:
            data[key] = row

    if not data:
        raise ValueError("Nao foi possivel extrair informacoes da tabela secundaria.")

    return data


def _parse_row_numbers_pt(numbers: list[float]) -> MeasurementRow:
    if len(numbers) >= 5:
        nominal, lower, upper, measured, deviation = numbers[:5]
    elif len(numbers) == 4:
        nominal, lower, upper, measured = numbers
        deviation = measured - nominal
    else:
        nominal = numbers[0] if len(numbers) > 0 else None
        lower = numbers[1] if len(numbers) > 1 else None
        upper = numbers[2] if len(numbers) > 2 else None
        measured = None
        deviation = None

    exceedance = compute_exceedance(measured, lower, upper)
    return MeasurementRow(
        characteristic_name="",
        nominal_value=nominal,
        measured_value=measured,
        lower_limit=lower,
        upper_limit=upper,
        deviation=deviation,
        exceedance=exceedance,
    )


def _parse_secondary_pdf_portuguese(lines: list[str]) -> dict[str, MeasurementRow]:
    data: dict[str, MeasurementRow] = {}
    current_section = ""

    header_prefixes = (
        "Scania Brazil",
        "Model ",
        "Date:",
        "Time:",
        "Oper.:",
        "Part :",
        "Serial:",
        "S e r i a l",
        "Nome ",
        "Mínimo",
        "M�nimo",
        "Message #",
        "Remove 4.5\"",
        "Journal Roundness",
        "Base circle radius",
    )

    section_aliases = {
        "errounguloparareferenciai6": "erroanguloparareferenciai6",
    }

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith(header_prefixes):
            continue

        if "Datatable:" in line or "Program:" in line:
            continue

        mancal_match = re.match(r"^Mancal\s+([A-G])\s+(.+)$", line, flags=re.IGNORECASE)
        i_match = re.match(r"^(I\d+)\b(?:\s*\(@[^)]*\))?\s+(.+)$", line, flags=re.IGNORECASE)
        dm_match = re.match(r"^(DM\d+)\s+(.+)$", line, flags=re.IGNORECASE)

        if mancal_match:
            mancal = mancal_match.group(1).upper()
            numbers = parse_numeric_tokens(mancal_match.group(2))
            if len(numbers) < 3:
                continue

            row = _parse_row_numbers_pt(numbers)
            section = current_section or "Mancal"

            candidate_names = [
                f"{section} [{mancal}]",
                f"{section} - {mancal}",
                f"Mancal {mancal}",
            ]

            if "diametro" in normalize_key(section):
                candidate_names.extend(
                    [
                        f"Diametro Mancal {mancal}",
                        f"Dia Mancal {mancal}",
                        f"Meas Diam - {mancal}",
                    ]
                )

            if "cilindricidade" in normalize_key(section):
                candidate_names.extend([f"Cilindricidade [{mancal}]", f"Cylindricity - {mancal}"])

            if "paralelismo" in normalize_key(section):
                candidate_names.append(f"Parallelism [{mancal}]")

            for name in candidate_names:
                key = normalize_key(name)
                data[key] = MeasurementRow(
                    characteristic_name=name,
                    nominal_value=row.nominal_value,
                    measured_value=row.measured_value,
                    lower_limit=row.lower_limit,
                    upper_limit=row.upper_limit,
                    deviation=row.deviation,
                    exceedance=row.exceedance,
                )
            continue

        if i_match:
            i_label = i_match.group(1).upper()
            idx = int(i_label[1:])
            numbers = parse_numeric_tokens(i_match.group(2))
            if len(numbers) < 3:
                continue

            row = _parse_row_numbers_pt(numbers)
            section = current_section or "I"
            normalized_section = normalize_key(section)
            normalized_section = section_aliases.get(normalized_section, normalized_section)

            alias_names = [
                f"{section} [{i_label}]",
                f"{section} - Lobe {idx}",
            ]

            if normalized_section == "anguloreferuz":
                alias_names.append(f"Angulo Refer. UZ [{i_label}]")
            if normalized_section == "erroanguloparareferenciai6":
                alias_names.append(f"Angle error to Cam 11 A6 - Lobe {idx}")
            if normalized_section == "raiodocirculobase":
                alias_names.append(f"BC Radius Error - Lobe {idx}")
            if normalized_section == "desviodocirculobase":
                alias_names.append(f"BC Runout - Lobe {idx}")
            if normalized_section == "concavoconvexo":
                alias_names.extend([f"Concavo/Convexo [{i_label}]", f"Concave/Convex - Lobe {idx}"])
            if normalized_section == "desviodevelocidade":
                alias_names.append(f"BC Velocity Error - Lobe {idx}")
            if normalized_section == "errodeperfiltopo":
                alias_names.append(f"Lift Error Nose - Lobe {idx}")
            if normalized_section == "errodeperfilfechamentodoflanco":
                alias_names.append(f"Lift Error Ramp - Lobe {idx}")
            if normalized_section == "errodeperfilaberturadoflanco":
                alias_names.append(f"Lift Difference Ramp - Lobe {idx}")

            for name in alias_names:
                key = normalize_key(name)
                data[key] = MeasurementRow(
                    characteristic_name=name,
                    nominal_value=row.nominal_value,
                    measured_value=row.measured_value,
                    lower_limit=row.lower_limit,
                    upper_limit=row.upper_limit,
                    deviation=row.deviation,
                    exceedance=row.exceedance,
                )
            continue

        if dm_match:
            dm_label = dm_match.group(1).upper()
            numbers = parse_numeric_tokens(dm_match.group(2))
            if len(numbers) < 3:
                continue
            row = _parse_row_numbers_pt(numbers)
            name = f"{current_section} [{dm_label}]" if current_section else dm_label
            key = normalize_key(name)
            data[key] = MeasurementRow(
                characteristic_name=name,
                nominal_value=row.nominal_value,
                measured_value=row.measured_value,
                lower_limit=row.lower_limit,
                upper_limit=row.upper_limit,
                deviation=row.deviation,
                exceedance=row.exceedance,
            )
            continue

        # Freeform metric line with values directly on the same line.
        first_num_match = re.search(r"-?(?:\d+,\d+|,\d+|\d+)", line)
        if first_num_match:
            metric_name = line[: first_num_match.start()].strip()
            numbers = parse_numeric_tokens(line[first_num_match.start() :])
            if metric_name and len(numbers) >= 3:
                row = _parse_row_numbers_pt(numbers)
                key = normalize_key(metric_name)
                data[key] = MeasurementRow(
                    characteristic_name=metric_name,
                    nominal_value=row.nominal_value,
                    measured_value=row.measured_value,
                    lower_limit=row.lower_limit,
                    upper_limit=row.upper_limit,
                    deviation=row.deviation,
                    exceedance=row.exceedance,
                )
                continue

        # Non-data line: treat as current section label.
        current_section = line

    return data
