"""
SolarSathi AI - Solar Agent

Phase 4 specialist agent for solar generation analysis.

This agent currently uses deterministic Python calculations.
AI/Groq reasoning will be added in a later phase.
"""

from tools.energy_tools import (
    calculate_solar_surplus,
    calculate_solar_deficit,
)


def run_solar_agent(
    solar_kw,
    load_kw,
    solar_capacity_kw=None,
):
    """
    Analyze current solar generation.

    Returns a structured dictionary that can later
    be consumed by the Supervisor Agent.
    """

    solar_kw = float(solar_kw)
    load_kw = float(load_kw)

    if solar_kw < 0:
        raise ValueError(
            "Solar generation cannot be negative."
        )

    if load_kw < 0:
        raise ValueError(
            "Load cannot be negative."
        )

    if solar_capacity_kw is not None:

        solar_capacity_kw = float(
            solar_capacity_kw
        )

        if solar_capacity_kw <= 0:
            raise ValueError(
                "Solar capacity must be greater than zero."
            )

    surplus_kw = calculate_solar_surplus(
        solar_kw,
        load_kw,
    )

    deficit_kw = calculate_solar_deficit(
        solar_kw,
        load_kw,
    )

    if solar_kw > load_kw:

        status = "Solar Surplus"

        recommendation = (
            "Solar generation is higher than the current "
            "load. The surplus can potentially be used "
            "for battery charging or export."
        )

    elif solar_kw < load_kw:

        status = "Solar Deficit"

        recommendation = (
            "Solar generation is below the current load. "
            "Battery or grid support may be required."
        )

    else:

        status = "Solar Balanced"

        recommendation = (
            "Solar generation approximately matches "
            "the current load."
        )

    utilization_percent = None

    if solar_capacity_kw:

        utilization_percent = (
            solar_kw / solar_capacity_kw
        ) * 100

    return {
        "agent": "Solar Agent",
        "status": status,
        "solar_generation_kw": round(
            solar_kw,
            2,
        ),
        "load_kw": round(
            load_kw,
            2,
        ),
        "solar_surplus_kw": round(
            surplus_kw,
            2,
        ),
        "solar_deficit_kw": round(
            deficit_kw,
            2,
        ),
        "solar_capacity_kw": solar_capacity_kw,
        "solar_utilization_percent": (
            round(
                utilization_percent,
                2,
            )
            if utilization_percent is not None
            else None
        ),
        "recommendation": recommendation,
    }
