"""
SolarSathi AI - Input Validation

This module validates user/system inputs before they
are passed to energy calculation tools.
"""


def validate_power(
    value: float,
    field_name: str,
) -> None:
    """Validate a power value."""

    if value < 0:
        raise ValueError(
            f"{field_name} cannot be negative."
        )


def validate_voltage(
    voltage: float,
) -> None:
    """Validate battery/system voltage."""

    if voltage <= 0:
        raise ValueError(
            "Voltage must be greater than zero."
        )


def validate_capacity(
    capacity_kwh: float,
) -> None:
    """Validate battery capacity."""

    if capacity_kwh <= 0:
        raise ValueError(
            "Battery capacity must be greater than zero."
        )


def validate_soc(
    soc: float,
) -> None:
    """Validate battery state of charge."""

    if not 0 <= soc <= 100:
        raise ValueError(
            "SOC must be between 0 and 100%."
        )


def validate_temperature(
    temperature_c: float,
) -> None:
    """
    Validate battery temperature.

    This is only a basic input sanity check.
    It is not a battery safety certification.
    """

    if temperature_c < -30 or temperature_c > 80:
        raise ValueError(
            "Temperature must be between -30°C and 80°C "
            "for this simulation."
        )


def validate_battery_capacity(
    rated_capacity_ah: float,
    measured_capacity_ah: float,
) -> None:
    """Validate battery capacity measurements."""

    if rated_capacity_ah <= 0:
        raise ValueError(
            "Rated capacity must be greater than zero."
        )

    if measured_capacity_ah < 0:
        raise ValueError(
            "Measured capacity cannot be negative."
        )
