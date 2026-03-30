from dataclasses import dataclass


@dataclass
class MeasurementRow:
    characteristic_name: str
    nominal_value: float | None
    measured_value: float | None
    lower_limit: float | None
    upper_limit: float | None
    deviation: float | None
    exceedance: float | None


@dataclass
class ComparedRow:
    row: MeasurementRow
    status: str
    mismatched_fields: set[str]
    secondary_missing: bool
