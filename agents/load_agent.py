"""
SolarSathi AI - Load Agent

Phase 4 specialist agent for electrical load analysis.
"""


def run_load_agent(
    current_load_kw,
    essential_load_kw=0.0,
    non_essential_load_kw=0.0,
    peak_load_kw=None,
):
    """
    Analyze current electrical demand.

    The load agent helps prioritize essential loads
    during limited energy availability.
    """

    current_load_kw = float(
        current_load_kw
    )

    essential_load_kw = float(
        essential_load_kw
    )

    non_essential_load_kw = float(
        non_essential_load_kw
    )

    if current_load_kw < 0:
        raise ValueError(
            "Current load cannot be negative."
        )

    if essential_load_kw < 0:
        raise ValueError(
            "Essential load cannot be negative."
        )

    if non_essential_load_kw < 0:
        raise ValueError(
            "Non-essential load cannot be negative."
        )

    if essential_load_kw > current_load_kw:
        raise ValueError(
            "Essential load cannot exceed current load."
        )

    if (
        essential_load_kw
        + non_essential_load_kw
        > current_load_kw
    ):
        raise ValueError(
            "Essential plus non-essential load "
            "cannot exceed current load."
        )

    if peak_load_kw is not None:

        peak_load_kw = float(
            peak_load_kw
        )

        if peak_load_kw < 0:
            raise ValueError(
                "Peak load cannot be negative."
            )

    non_essential_fraction = 0.0

    if current_load_kw > 0:

        non_essential_fraction = (
            non_essential_load_kw
            / current_load_kw
        ) * 100

    essential_fraction = 0.0

    if current_load_kw > 0:

        essential_fraction = (
            essential_load_kw
            / current_load_kw
        ) * 100

    if current_load_kw == 0:

        status = "No Load"

        recommendation = (
            "No current electrical load detected."
        )

    elif (
        essential_load_kw
        / current_load_kw
        >= 0.7
    ):

        status = "Essential Load Dominant"

        recommendation = (
            "Most of the current demand is essential. "
            "During grid outages or low battery SOC, "
            "protect essential loads first."
        )

    else:

        status = "Flexible Load Available"

        recommendation = (
            "Some demand appears flexible or non-essential. "
            "Consider load shifting during periods of "
            "low solar or expensive grid energy."
        )

    peak_ratio = None

    if peak_load_kw and peak_load_kw > 0:

        peak_ratio = (
            current_load_kw
            / peak_load_kw
        ) * 100

    return {

        "agent": "Load Agent",

        "status": status,

        "current_load_kw": round(
            current_load_kw,
            2,
        ),

        "essential_load_kw": round(
            essential_load_kw,
            2,
        ),

        "non_essential_load_kw": round(
            non_essential_load_kw,
            2,
        ),

        "essential_load_percent": round(
            essential_fraction,
            2,
        ),

        "non_essential_load_percent": round(
            non_essential_fraction,
            2,
        ),

        "peak_load_kw": peak_load_kw,

        "peak_utilization_percent": (
            round(
                peak_ratio,
                2,
            )
            if peak_ratio is not None
            else None
        ),

        "recommendation": recommendation,
    }
