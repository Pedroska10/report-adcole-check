from .mapping import apply_mapping
from .models import ComparedRow, MeasurementRow
from .utils import normalize_key


def values_equal(a: float | None, b: float | None) -> bool:
    if a is None and b is None:
        return True
    if a is None and b is not None and abs(b) < 1e-12:
        return True
    if b is None and a is not None and abs(a) < 1e-12:
        return True
    if a is None or b is None:
        return False
    return abs(a - b) < 1e-12


def compare_rows(
    base_rows: list[MeasurementRow],
    secondary_by_key: dict[str, MeasurementRow],
    mapping_rules,
) -> list[ComparedRow]:
    compared: list[ComparedRow] = []

    field_getters = {
        "nominal_value": lambda row: row.nominal_value,
        "measured_value": lambda row: row.measured_value,
        "lower_limit": lambda row: row.lower_limit,
        "upper_limit": lambda row: row.upper_limit,
    }

    for row in base_rows:
        base_key = normalize_key(row.characteristic_name)
        mapped_key = apply_mapping(base_key, mapping_rules)
        target = secondary_by_key.get(mapped_key)

        if not target:
            compared.append(
                ComparedRow(
                    row=row,
                    status="not ok",
                    mismatched_fields=set(field_getters.keys()),
                    secondary_missing=True,
                )
            )
            continue

        mismatches: set[str] = set()
        for field_name, getter in field_getters.items():
            if not values_equal(getter(row), getter(target)):
                mismatches.add(field_name)

        status = "not ok" if mismatches else "ok"
        compared.append(
            ComparedRow(
                row=row,
                status=status,
                mismatched_fields=mismatches,
                secondary_missing=False,
            )
        )

    return compared
