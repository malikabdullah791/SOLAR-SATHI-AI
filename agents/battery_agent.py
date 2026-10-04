"""
SolarSathi AI - Battery Agent

Phase 4 specialist agent for battery analysis.

The agent consumes deterministic results from
battery_tools.py and provides a structured response.
"""

from tools.battery_tools import (
    analyze_battery_health,
)


def run_battery_agent(
    battery_type,
    voltage_v,
    rated_capacity_ah,
    measured_capacity_ah,
    current_a,
    temperature_c,
    age_years,
    soc,
    symptoms="",
):
    """
    Analyze battery condition using the Phase 3
    battery health tools.
    """

    analysis = analyze_battery_health(

        battery_type=battery_type,

        voltage_v=voltage_v,

        rated_capacity_ah=rated_capacity_ah,

        measured_capacity_ah=measured_capacity_ah,

        current_a=current_a,

        temperature_c=temperature_c,

        age_years=age_years,

        soc=soc,

        symptoms=symptoms,
    )

    health_label = analysis[
        "health_label"
    ]

    risk_level = analysis[
        "risk_level"
    ]

    if health_label == "Healthy":

        recommendation = (
            "Battery condition appears healthy "
            "under this preliminary screening. "
            "Continue monitoring."
        )

    elif health_label == "Good":

        recommendation = (
            "Battery appears usable, but regular "
            "monitoring is recommended."
        )

    elif health_label == "Needs Attention":

        recommendation = (
            "Battery shows possible degradation. "
            "Further testing and inspection are recommended."
        )

    else:

        recommendation = (
            "Battery health is poor under this screening model. "
            "Professional inspection and further testing "
            "are recommended."
        )

    if risk_level in [
        "High",
        "Critical Attention",
    ]:

        recommendation += (
            " Risk indicators require additional attention."
        )

    return {
        "agent": "Battery Agent",

        "status": health_label,

        "risk_level": risk_level,

        "soh_percent": analysis[
            "soh_percent"
        ],

        "soc_percent": analysis[
            "soc_percent"
        ],

        "voltage_v": analysis[
            "voltage_v"
        ],

        "current_a": analysis[
            "current_a"
        ],

        "power_kw": analysis[
            "power_kw"
        ],

        "temperature_c": analysis[
            "temperature_c"
        ],

        "temperature_status": analysis[
            "temperature_status"
        ],

        "age_years": analysis[
            "age_years"
        ],

        "possible_causes": analysis[
            "possible_causes"
        ],

        "risk_warnings": analysis[
            "risk_warnings"
        ],

        "recommendation": recommendation,

        "raw_analysis": analysis,
    }
