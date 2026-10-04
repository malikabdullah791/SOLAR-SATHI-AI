"""
SolarSathi AI - Grid Agent

Phase 4 specialist agent for grid availability,
grid import and electricity cost analysis.
"""

from tools.energy_tools import (
    calculate_grid_import,
    calculate_energy_cost,
)


def run_grid_agent(
    grid_available,
    load_kw,
    solar_kw,
    battery_to_load_kw=0.0,
    tariff_rs_per_kwh=50.0,
):
    """
    Analyze grid condition and potential grid requirement.
    """

    load_kw = float(load_kw)
    solar_kw = float(solar_kw)
    battery_to_load_kw = float(
        battery_to_load_kw
    )
    tariff_rs_per_kwh = float(
        tariff_rs_per_kwh
    )

    if load_kw < 0:
        raise ValueError(
            "Load cannot be negative."
        )

    if solar_kw < 0:
        raise ValueError(
            "Solar generation cannot be negative."
        )

    if battery_to_load_kw < 0:
        raise ValueError(
            "Battery contribution cannot be negative."
        )

    if tariff_rs_per_kwh < 0:
        raise ValueError(
            "Tariff cannot be negative."
        )

    potential_grid_import = calculate_grid_import(
        load_kw=load_kw,
        solar_kw=solar_kw,
        battery_to_load_kw=battery_to_load_kw,
    )

    if grid_available:

        grid_status = "Available"

        recommendation = (
            "Grid is available and can support remaining "
            "load after solar and battery contribution."
        )

        grid_import_kw = potential_grid_import

    else:

        grid_status = "Unavailable"

        recommendation = (
            "Grid is unavailable. Preserve battery energy "
            "and prioritize essential loads."
        )

        grid_import_kw = 0.0

    estimated_cost = calculate_energy_cost(
        energy_kwh=grid_import_kw,
        tariff_rs_per_kwh=tariff_rs_per_kwh,
    )

    return {

        "agent": "Grid Agent",

        "grid_status": grid_status,

        "grid_available": bool(
            grid_available
        ),

        "potential_grid_import_kw": round(
            potential_grid_import,
            2,
        ),

        "recommended_grid_import_kw": round(
            grid_import_kw,
            2,
        ),

        "tariff_rs_per_kwh": round(
            tariff_rs_per_kwh,
            2,
        ),

        "estimated_cost_rs": round(
            estimated_cost,
            2,
        ),

        "recommendation": recommendation,
    }
