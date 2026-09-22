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
    secondary_name: str | None
    status: str
    mismatched_fields: set[str]
    secondary_missing: bool
    base_missing: bool = False
    adcole_name: str | None = None
    piweb_name: str | None = None
