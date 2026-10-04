"""
SolarSathi AI - Supervisor Agent

Phase 5

The Supervisor Agent coordinates the specialist agents.

Current version:
- Deterministic Python orchestration
- No Groq/LLM yet
- Delegates tasks to specialist agents
- Collects results
- Performs basic consistency checks
- Generates a structured overall recommendation

Groq/LLM reasoning will be added in Phase 6.
"""

from agents.solar_agent import run_solar_agent
from agents.battery_agent import run_battery_agent
from agents.load_agent import run_load_agent
from agents.grid_agent import run_grid_agent


def create_supervisor_plan(
    solar_kw,
    load_kw,
    grid_available,
    battery_soc,
):
    """
    Decide which specialist agents are relevant
    to the current energy-management request.

    Returns a simple execution plan.
    """

    tasks = []

    # Solar analysis is always useful.
    tasks.append("solar")

    # Load analysis is always useful.
    tasks.append("load")

    # Battery analysis is important when
    # battery information is available.
    tasks.append("battery")

    # Grid analysis is useful when grid status
    # matters.
    tasks.append("grid")

    return {
        "supervisor": "Supervisor Agent",
        "request_type": "Energy Management Analysis",
        "tasks": tasks,
        "reason": (
            "The Supervisor selected Solar, Battery, "
            "Load and Grid specialists because the "
            "energy-management decision depends on "
            "generation, demand, battery condition "
            "and grid availability."
        ),
    }


def validate_agent_results(
    solar_result,
    battery_result,
    load_result,
    grid_result,
):
    """
    Perform basic validation of specialist-agent results.

    This is intentionally simple in Phase 5.
    More advanced validation will be added later.
    """

    required_results = {
        "Solar Agent": solar_result,
        "Battery Agent": battery_result,
        "Load Agent": load_result,
        "Grid Agent": grid_result,
    }

    missing_agents = []

    for agent_name, result in required_results.items():

        if not isinstance(result, dict) or not result:
            missing_agents.append(agent_name)

    if missing_agents:

        return {
            "valid": False,
            "missing_agents": missing_agents,
            "message": (
                "One or more specialist agents did not "
                "return valid results."
            ),
        }

    return {
        "valid": True,
        "missing_agents": [],
        "message": (
            "All specialist agents returned valid results."
        ),
    }


def generate_supervisor_recommendation(
    solar_result,
    battery_result,
    load_result,
    grid_result,
):
    """
    Generate an overall deterministic recommendation
    from specialist-agent results.

    This is NOT an LLM response.
    """

    recommendations = []
    warnings = []

    # -------------------------------------------------
    # Solar logic
    # -------------------------------------------------

    solar_status = solar_result.get(
        "status",
        ""
    )

    solar_surplus = solar_result.get(
        "solar_surplus_kw",
        0.0
    )

    if solar_status == "Solar Surplus":

        recommendations.append(
            "Use available solar generation to supply "
            "the current load first."
        )

        if solar_surplus > 0:

            recommendations.append(
                "Consider using the remaining solar "
                "surplus for battery charging or export."
            )

    elif solar_status == "Solar Deficit":

        recommendations.append(
            "Solar generation is below the current load. "
            "Battery and/or grid support may be required."
        )

    # -------------------------------------------------
    # Battery logic
    # -------------------------------------------------

    battery_status = battery_result.get(
        "status",
        ""
    )

    battery_risk = battery_result.get(
        "risk_level",
        ""
    )

    battery_soc = battery_result.get(
        "soc_percent",
        0.0
    )

    if battery_status == "Healthy":

        recommendations.append(
            "Battery condition appears healthy under "
            "the preliminary screening model."
        )

    elif battery_status == "Good":

        recommendations.append(
            "Battery is currently usable, but continue "
            "regular monitoring."
        )

    elif battery_status == "Needs Attention":

        recommendations.append(
            "Battery shows possible degradation. "
            "Further testing and inspection are recommended."
        )

        warnings.append(
            "Battery health requires attention."
        )

    elif battery_status == "Poor":

        recommendations.append(
            "Battery health appears poor under the "
            "preliminary screening model."
        )

        warnings.append(
            "Professional battery inspection is recommended."
        )

    # Battery SOC warning
    if battery_soc < 20:

        warnings.append(
            "Battery SOC is below the configured minimum "
            "operating threshold."
        )

        recommendations.append(
            "Avoid unnecessary battery discharge and "
            "prioritize essential loads."
        )

    elif battery_soc < 30:

        recommendations.append(
            "Battery SOC is relatively low. "
            "Conserve battery energy."
        )

    # Battery risk
    if battery_risk in [
        "High",
        "Critical Attention",
    ]:

        warnings.append(
            "Battery risk indicators require additional attention."
        )

    # -------------------------------------------------
    # Load logic
    # -------------------------------------------------

    load_status = load_result.get(
        "status",
        ""
    )

    if load_status == "Essential Load Dominant":

        recommendations.append(
            "Essential loads represent most of the "
            "current demand. Protect them during "
            "grid outages or low-energy conditions."
        )

    elif load_status == "Flexible Load Available":

        recommendations.append(
            "Some load appears flexible. Consider "
            "shifting non-essential demand toward "
            "periods of high solar availability."
        )

    # -------------------------------------------------
    # Grid logic
    # -------------------------------------------------

    grid_available = grid_result.get(
        "grid_available",
        False
    )

    grid_import = grid_result.get(
        "recommended_grid_import_kw",
        0.0
    )

    if grid_available:

        if grid_import > 0:

            recommendations.append(
                "Grid support may be required for the "
                "remaining demand after solar and battery contribution."
            )

        else:

            recommendations.append(
                "Current solar and battery contribution "
                "may be sufficient without additional grid import."
            )

    else:

        warnings.append(
            "Grid is currently unavailable."
        )

        recommendations.append(
            "Prioritize essential loads and preserve "
            "battery energy during the outage."
        )

    # -------------------------------------------------
    # Final priority
    # -------------------------------------------------

    if warnings:

        priority = "Attention Required"

    else:

        priority = "Normal"

    return {
        "priority": priority,
        "recommendations": recommendations,
        "warnings": warnings,
    }


def run_supervisor_agent(
    solar_kw,
    load_kw,
    grid_available,
    battery_type,
    battery_voltage,
    rated_capacity_ah,
    measured_capacity_ah,
    battery_current,
    temperature_c,
    battery_age,
    battery_soc,
    symptoms="",
    essential_load_kw=0.0,
    non_essential_load_kw=0.0,
    peak_load_kw=None,
    grid_tariff=50.0,
):
    """
    Main Supervisor Agent.

    Workflow:

    1. Create execution plan
    2. Run Solar Agent
    3. Run Battery Agent
    4. Run Load Agent
    5. Run Grid Agent
    6. Validate results
    7. Generate overall recommendation
    8. Return structured result
    """

    # -------------------------------------------------
    # STEP 1: PLAN
    # -------------------------------------------------

    plan = create_supervisor_plan(
        solar_kw=solar_kw,
        load_kw=load_kw,
        grid_available=grid_available,
        battery_soc=battery_soc,
    )

    # -------------------------------------------------
    # STEP 2: SOLAR AGENT
    # -------------------------------------------------

    solar_result = run_solar_agent(
        solar_kw=solar_kw,
        load_kw=load_kw,
    )

    # -------------------------------------------------
    # STEP 3: BATTERY AGENT
    # -------------------------------------------------

    battery_result = run_battery_agent(
        battery_type=battery_type,
        voltage_v=battery_voltage,
        rated_capacity_ah=rated_capacity_ah,
        measured_capacity_ah=measured_capacity_ah,
        current_a=battery_current,
        temperature_c=temperature_c,
        age_years=battery_age,
        soc=battery_soc,
        symptoms=symptoms,
    )

    # -------------------------------------------------
    # STEP 4: LOAD AGENT
    # -------------------------------------------------

    load_result = run_load_agent(
        current_load_kw=load_kw,
        essential_load_kw=essential_load_kw,
        non_essential_load_kw=non_essential_load_kw,
        peak_load_kw=peak_load_kw,
    )

    # -------------------------------------------------
    # STEP 5: GRID AGENT
    # -------------------------------------------------

    # At this phase we use battery power from
    # the Battery Agent.

    battery_to_load_kw = 0.0

    if solar_kw < load_kw and battery_soc > 20:

        battery_to_load_kw = min(
            load_kw - solar_kw,
            5.0,
        )

    grid_result = run_grid_agent(
        grid_available=grid_available,
        load_kw=load_kw,
        solar_kw=solar_kw,
        battery_to_load_kw=battery_to_load_kw,
        tariff_rs_per_kwh=grid_tariff,
    )

    # -------------------------------------------------
    # STEP 6: VALIDATE
    # -------------------------------------------------

    validation = validate_agent_results(
        solar_result=solar_result,
        battery_result=battery_result,
        load_result=load_result,
        grid_result=grid_result,
    )

    if not validation["valid"]:

        return {
            "success": False,
            "supervisor": "Supervisor Agent",
            "plan": plan,
            "validation": validation,
            "message": (
                "Supervisor could not complete the "
                "analysis because one or more agents "
                "returned invalid results."
            ),
        }

    # -------------------------------------------------
    # STEP 7: FINAL RECOMMENDATION
    # -------------------------------------------------

    final_recommendation = (
        generate_supervisor_recommendation(
            solar_result=solar_result,
            battery_result=battery_result,
            load_result=load_result,
            grid_result=grid_result,
        )
    )

    # -------------------------------------------------
    # STEP 8: FINAL RESULT
    # -------------------------------------------------

    return {
        "success": True,
        "supervisor": "Supervisor Agent",

        "workflow": [
            "Request received",
            "Supervisor created execution plan",
            "Solar Agent analyzed generation",
            "Battery Agent analyzed battery condition",
            "Load Agent analyzed demand",
            "Grid Agent analyzed grid condition",
            "Supervisor validated agent results",
            "Supervisor generated final recommendation",
        ],

        "plan": plan,

        "validation": validation,

        "solar_agent": solar_result,

        "battery_agent": battery_result,

        "load_agent": load_result,

        "grid_agent": grid_result,

        "final_recommendation": final_recommendation,
    }
