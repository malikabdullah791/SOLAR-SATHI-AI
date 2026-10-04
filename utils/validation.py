"""
Input validation utilities for SolarSathi AI.
"""


def validate_power(value, name="Power"):
    value = float(value)

    if value < 0:
        raise ValueError(
            f"{name} cannot be negative."
        )

    return value


def validate_voltage(value, name="Voltage"):
    value = float(value)

    if value <= 0:
        raise ValueError(
            f"{name} must be greater than zero."
        )

    return value


def validate_capacity(value, name="Capacity"):
    value = float(value)

    if value <= 0:
        raise ValueError(
            f"{name} must be greater than zero."
        )

    return value


def validate_soc(value):
    value = float(value)

    if value < 0 or value > 100:
        raise ValueError(
            "SOC must be between 0 and 100%."
        )

    return value


def validate_temperature(value):
    value = float(value)

    if value < -50 or value > 100:
        raise ValueError(
            "Temperature is outside the supported range."
        )

    return value


def validate_battery_capacity(
    rated_capacity,
    measured_capacity
):
    rated_capacity = float(rated_capacity)
    measured_capacity = float(measured_capacity)

    if rated_capacity <= 0:
        raise ValueError(
            "Rated battery capacity must be greater than zero."
        )

    if measured_capacity < 0:
        raise ValueError(
            "Measured battery capacity cannot be negative."
        )

    if measured_capacity > rated_capacity:
        raise ValueError(
            "Measured capacity cannot exceed rated capacity "
            "in this simplified model."
        )

    return True
