import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from tools.energy_tools import (
    calculate_energy_flow,
    calculate_backup_time,
    calculate_energy_cost,
    check_energy_balance,
)

from tools.battery_tools import (
    analyze_battery_health,
)

from agents.solar_agent import (
    run_solar_agent,
)

from agents.battery_agent import (
    run_battery_agent,
)

from agents.load_agent import (
    run_load_agent,
)

from agents.grid_agent import (
    run_grid_agent,
)
# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SolarSathi AI",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #666666;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 600;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DEMO SCENARIOS
# ============================================================

DEMO_SCENARIOS = {

    "Sunny Day": {
        "solar_kw": 5.0,
        "load_kw": 3.0,
        "battery_soc": 60.0,
        "battery_capacity_kwh": 10.0,
        "battery_health": 92.0,
        "battery_rated_ah": 200.0,
        "battery_measured_ah": 184.0,
        "battery_voltage": 48.0,
        "battery_current": 10.0,
        "battery_age": 1.5,
        "temperature_c": 28.0,
        "battery_type": "Lead Acid",
        "symptoms": "",
        "grid_available": True,
        "grid_tariff": 50.0,
    },

    "Evening / Load Shedding": {
        "solar_kw": 0.0,
        "load_kw": 4.0,
        "battery_soc": 40.0,
        "battery_capacity_kwh": 10.0,
        "battery_health": 88.0,
        "battery_rated_ah": 200.0,
        "battery_measured_ah": 176.0,
        "battery_voltage": 48.0,
        "battery_current": 80.0,
        "battery_age": 2.0,
        "temperature_c": 30.0,
        "battery_type": "Lead Acid",
        "symptoms": "Short backup during load shedding",
        "grid_available": False,
        "grid_tariff": 50.0,
    },

    "Battery Health Problem": {
        "solar_kw": 1.0,
        "load_kw": 3.0,
        "battery_soc": 30.0,
        "battery_capacity_kwh": 10.0,
        "battery_health": 55.0,
        "battery_rated_ah": 200.0,
        "battery_measured_ah": 110.0,
        "battery_voltage": 48.0,
        "battery_current": 70.0,
        "battery_age": 4.5,
        "temperature_c": 43.0,
        "battery_type": "Lead Acid",
        "symptoms": "Battery heating and short backup",
        "grid_available": True,
        "grid_tariff": 50.0,
    },

    "High Solar Surplus": {
        "solar_kw": 7.0,
        "load_kw": 2.0,
        "battery_soc": 50.0,
        "battery_capacity_kwh": 10.0,
        "battery_health": 90.0,
        "battery_rated_ah": 200.0,
        "battery_measured_ah": 180.0,
        "battery_voltage": 48.0,
        "battery_current": 15.0,
        "battery_age": 1.0,
        "temperature_c": 29.0,
        "battery_type": "Lead Acid",
        "symptoms": "",
        "grid_available": True,
        "grid_tariff": 50.0,
    },
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_recommendation(
    solar_kw,
    load_kw,
    battery_soc,
    battery_health,
    temperature_c,
    grid_available,
):
    """Generate simple deterministic recommendation."""

    recommendations = []

    if solar_kw > load_kw:

        recommendations.append(
            "Solar generation is higher than the current load. "
            "Use suitable solar surplus for battery charging."
        )

    elif solar_kw < load_kw:

        recommendations.append(
            "Solar generation is below the current load. "
            "Battery or grid support may be required."
        )

    else:

        recommendations.append(
            "Solar generation is approximately matching the load."
        )

    if battery_soc < 20:

        recommendations.append(
            "Battery SOC is very low. Avoid unnecessary discharge."
        )

    elif battery_soc < 40:

        recommendations.append(
            "Battery SOC is relatively low. Prioritize essential loads."
        )

    elif battery_soc > 90:

        recommendations.append(
            "Battery SOC is high. Use available solar surplus carefully."
        )

    if battery_health < 50:

        recommendations.append(
            "Battery health is poor according to the preliminary "
            "assessment. Professional inspection is recommended."
        )

    elif battery_health < 70:

        recommendations.append(
            "Battery health needs attention. Further testing is recommended."
        )

    if temperature_c >= 40:

        recommendations.append(
            "Battery temperature is high. Avoid aggressive operation "
            "and seek qualified professional assessment."
        )

    if not grid_available:

        recommendations.append(
            "Grid is unavailable. Prioritize essential loads "
            "and preserve battery SOC."
        )

    else:

        recommendations.append(
            "Grid is available and can support demand when required."
        )

    return recommendations


def create_energy_flow_chart(flow):

    labels = [
        "Solar",
        "Battery",
        "Grid",
        "Load",
        "Battery Charging",
        "Solar Export",
        "Unserved Load",
    ]

    source = []
    target = []
    value = []

    if flow["solar_to_load_kw"] > 0:
        source.append(0)
        target.append(3)
        value.append(flow["solar_to_load_kw"])

    if flow["solar_to_battery_kw"] > 0:
        source.append(0)
        target.append(4)
        value.append(flow["solar_to_battery_kw"])

    if flow["battery_to_load_kw"] > 0:
        source.append(1)
        target.append(3)
        value.append(flow["battery_to_load_kw"])

    if flow["grid_to_load_kw"] > 0:
        source.append(2)
        target.append(3)
        value.append(flow["grid_to_load_kw"])

    if flow["solar_export_kw"] > 0:
        source.append(0)
        target.append(5)
        value.append(flow["solar_export_kw"])

    if flow["unserved_load_kw"] > 0:
        source.append(0)
        target.append(6)
        value.append(flow["unserved_load_kw"])

    fig = go.Figure(
        go.Sankey(
            node=dict(
                pad=20,
                thickness=20,
                label=labels,
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
            ),
        )
    )

    fig.update_layout(
        title="Energy Flow",
        height=450,
    )

    return fig


def load_sample_data():

    data = {
        "Hour": [
            "06:00",
            "08:00",
            "10:00",
            "12:00",
            "14:00",
            "16:00",
            "18:00",
            "20:00",
        ],
        "Solar (kW)": [
            0.2,
            1.5,
            3.2,
            5.0,
            5.5,
            3.8,
            1.0,
            0.0,
        ],
        "Load (kW)": [
            1.5,
            2.0,
            2.5,
            3.0,
            3.2,
            3.5,
            4.0,
            3.0,
        ],
        "Battery SOC (%)": [
            45,
            48,
            55,
            65,
            75,
            80,
            65,
            50,
        ],
    }

    return pd.DataFrame(data)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">☀️ SolarSathi AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Your Solar System's AI Companion"
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ System Configuration")

selected_scenario = st.sidebar.selectbox(
    "Select Demo Scenario",
    list(DEMO_SCENARIOS.keys()),
)

scenario = DEMO_SCENARIOS[selected_scenario]

st.sidebar.markdown("---")

st.sidebar.subheader("Energy System")

solar_kw = st.sidebar.number_input(
    "Solar Generation (kW)",
    min_value=0.0,
    value=float(scenario["solar_kw"]),
    step=0.1,
)

load_kw = st.sidebar.number_input(
    "Current Load (kW)",
    min_value=0.0,
    value=float(scenario["load_kw"]),
    step=0.1,
)

essential_load_kw = st.sidebar.number_input(
    "Essential Load (kW)",
    min_value=0.0,
    value=min(
        load_kw,
        round(load_kw * 0.7, 1)
    ),
    step=0.1,
)

non_essential_load_kw = st.sidebar.number_input(
    "Non-Essential Load (kW)",
    min_value=0.0,
    value=0.0,
    step=0.1,
)

peak_load_kw = st.sidebar.number_input(
    "Peak Load (kW)",
    min_value=0.0,
    value=max(
        load_kw,
        round(load_kw * 1.3, 1)
    ),
    step=0.1,
)
battery_soc = st.sidebar.slider(
    "Battery SOC (%)",
    0.0,
    100.0,
    float(scenario["battery_soc"]),
    1.0,
)

battery_capacity = st.sidebar.number_input(
    "Battery Energy Capacity (kWh)",
    min_value=0.1,
    value=float(scenario["battery_capacity_kwh"]),
    step=0.5,
)

grid_available = st.sidebar.checkbox(
    "Grid Available",
    value=bool(scenario["grid_available"]),
)

grid_tariff = st.sidebar.number_input(
    "Grid Tariff (Rs/kWh)",
    min_value=0.0,
    value=float(scenario["grid_tariff"]),
    step=1.0,
)


# ============================================================
# BATTERY HEALTH INPUTS
# ============================================================

st.sidebar.markdown("---")

st.sidebar.subheader("🔋 Battery Health Inputs")

battery_type = st.sidebar.selectbox(
    "Battery Type",
    [
        "Lead Acid",
        "Lithium-ion",
        "Tubular Lead Acid",
        "AGM",
        "Gel",
        "Other",
    ],
    index=0,
)

battery_voltage = st.sidebar.number_input(
    "Battery Voltage (V)",
    min_value=0.1,
    value=float(scenario["battery_voltage"]),
    step=0.1,
)

rated_capacity_ah = st.sidebar.number_input(
    "Rated Capacity (Ah)",
    min_value=0.1,
    value=float(scenario["battery_rated_ah"]),
    step=1.0,
)

measured_capacity_ah = st.sidebar.number_input(
    "Measured Capacity (Ah)",
    min_value=0.0,
    value=float(scenario["battery_measured_ah"]),
    step=1.0,
)

battery_current = st.sidebar.number_input(
    "Battery Current (A)",
    value=float(scenario["battery_current"]),
    step=1.0,
)

battery_age = st.sidebar.number_input(
    "Battery Age (Years)",
    min_value=0.0,
    value=float(scenario["battery_age"]),
    step=0.1,
)

temperature_c = st.sidebar.number_input(
    "Battery Temperature (°C)",
    min_value=-20.0,
    max_value=100.0,
    value=float(scenario["temperature_c"]),
    step=1.0,
)

symptoms = st.sidebar.text_area(
    "Battery Symptoms",
    value=scenario["symptoms"],
    placeholder=(
        "Example: heating, short backup, voltage dropping..."
    ),
)


# ============================================================
# PHASE 2 CALCULATIONS
# ============================================================

try:

    energy_flow = calculate_energy_flow(
        solar_kw=solar_kw,
        load_kw=load_kw,
        battery_soc=battery_soc,
        grid_available=grid_available,
        min_battery_soc=20.0,
        max_battery_charge_kw=5.0,
        max_battery_discharge_kw=5.0,
    )

    backup_time = calculate_backup_time(
        battery_capacity_kwh=battery_capacity,
        battery_soc=battery_soc,
        load_kw=load_kw,
        min_soc=20.0,
        usable_fraction=0.90,
    )

    estimated_cost = calculate_energy_cost(
        energy_kwh=load_kw,
        tariff_rs_per_kwh=grid_tariff,
    )

    energy_balance = check_energy_balance(
        supply_kw=energy_flow["total_supply_kw"],
        demand_kw=energy_flow["total_demand_kw"],
    )

except ValueError as error:

    st.error(
        f"Energy calculation error: {error}"
    )

    st.stop()


# ============================================================
# PHASE 3 BATTERY ANALYSIS
# ============================================================

try:

    battery_analysis = analyze_battery_health(

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

except ValueError as error:

    st.error(
        f"Battery analysis error: {error}"
    )

    st.stop()

# ============================================================
# PHASE 4 - SPECIALIST AGENTS
# ============================================================

try:

    solar_agent_result = run_solar_agent(
        solar_kw=solar_kw,
        load_kw=load_kw,
    )

    battery_agent_result = run_battery_agent(
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

    load_agent_result = run_load_agent(
        current_load_kw=load_kw,
        essential_load_kw=essential_load_kw,
        non_essential_load_kw=non_essential_load_kw,
        peak_load_kw=peak_load_kw,
    )

    grid_agent_result = run_grid_agent(
        grid_available=grid_available,
        load_kw=load_kw,
        solar_kw=solar_kw,
        battery_to_load_kw=energy_flow[
            "battery_to_load_kw"
        ],
        tariff_rs_per_kwh=grid_tariff,
    )

except ValueError as error:

    st.error(
        f"Agent calculation error: {error}"
    )

    st.stop()
# ============================================================
# MAIN KPI DASHBOARD
# ============================================================

st.markdown(
    '<div class="section-title">📊 System Overview</div>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    st.metric(
        "☀️ Solar",
        f"{solar_kw:.1f} kW",
    )

with col2:

    st.metric(
        "🔋 Battery SOC",
        f"{battery_soc:.0f}%",
    )

with col3:

    st.metric(
        "⚡ Load",
        f"{load_kw:.1f} kW",
    )

with col4:

    st.metric(
        "🔌 Grid",
        "Available"
        if grid_available
        else "Unavailable",
    )

with col5:

    st.metric(
        "❤️ Battery SOH",
        f"{battery_analysis['soh_percent']:.1f}%",
    )


# ============================================================
# BATTERY HEALTH STATUS
# ============================================================

health_label = battery_analysis["health_label"]

if health_label == "Healthy":

    st.success(
        f"🔋 Battery Health: **{health_label}** "
        f"({battery_analysis['soh_percent']:.1f}%)"
    )

elif health_label == "Good":

    st.info(
        f"🔋 Battery Health: **{health_label}** "
        f"({battery_analysis['soh_percent']:.1f}%)"
    )

elif health_label == "Needs Attention":

    st.warning(
        f"🔋 Battery Health: **{health_label}** "
        f"({battery_analysis['soh_percent']:.1f}%)"
    )

else:

    st.error(
        f"🔋 Battery Health: **{health_label}** "
        f"({battery_analysis['soh_percent']:.1f}%)"
    )


# ============================================================
# TABS
# ============================================================

tabs = st.tabs(
    [
        "📊 Dashboard",
        "⚡ Energy Manager",
        "🔋 Battery Health Doctor",
        "🤖 AI Agent",
        "📚 Knowledge / RAG",
        "📄 Reports & Insights",
        "⚙️ Settings",
    ]
)


# ============================================================
# TAB 1 — DASHBOARD
# ============================================================

with tabs[0]:

    st.markdown(
        '<div class="section-title">Energy Flow</div>',
        unsafe_allow_html=True,
    )

    col_chart, col_summary = st.columns(
        [2, 1]
    )

    with col_chart:

        st.plotly_chart(
            create_energy_flow_chart(
                energy_flow
            ),
            use_container_width=True,
        )

    with col_summary:

        st.subheader("Energy Summary")

        st.write(
            f"Solar → Load: "
            f"**{energy_flow['solar_to_load_kw']:.2f} kW**"
        )

        st.write(
            f"Solar → Battery: "
            f"**{energy_flow['solar_to_battery_kw']:.2f} kW**"
        )

        st.write(
            f"Battery → Load: "
            f"**{energy_flow['battery_to_load_kw']:.2f} kW**"
        )

        st.write(
            f"Grid → Load: "
            f"**{energy_flow['grid_to_load_kw']:.2f} kW**"
        )

        st.write(
            f"Solar Export: "
            f"**{energy_flow['solar_export_kw']:.2f} kW**"
        )

        st.write(
            f"Unserved Load: "
            f"**{energy_flow['unserved_load_kw']:.2f} kW**"
        )

        if energy_balance["balanced"]:

            st.success(
                "✅ Energy balance is approximately balanced."
            )

        else:

            st.warning(
                "⚠️ Energy balance has a difference."
            )


# ============================================================
# TAB 2 — ENERGY MANAGER
# ============================================================

with tabs[1]:

    st.markdown(
        '<div class="section-title">⚡ Energy Manager</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "SolarSathi uses deterministic Python tools to "
        "calculate the current energy flow."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Solar Surplus",
            f"{energy_flow['solar_surplus_kw']:.2f} kW",
        )

    with col2:

        st.metric(
            "Solar Deficit",
            f"{energy_flow['solar_deficit_kw']:.2f} kW",
        )

    with col3:

        if backup_time == float("inf"):

            backup_text = "N/A"

        else:

            backup_text = f"{backup_time:.2f} h"

        st.metric(
            "Estimated Backup",
            backup_text,
        )

    flow_df = pd.DataFrame(
        {
            "Energy Path": [
                "Solar → Load",
                "Solar → Battery",
                "Battery → Load",
                "Grid → Load",
                "Solar Export",
                "Unserved Load",
            ],
            "Power (kW)": [
                energy_flow["solar_to_load_kw"],
                energy_flow["solar_to_battery_kw"],
                energy_flow["battery_to_load_kw"],
                energy_flow["grid_to_load_kw"],
                energy_flow["solar_export_kw"],
                energy_flow["unserved_load_kw"],
            ],
        }
    )

    st.dataframe(
        flow_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Estimated Cost")

    st.write(
        f"Current estimated energy cost: "
        f"**Rs {estimated_cost:,.2f}**"
    )


# ============================================================
# TAB 3 — BATTERY HEALTH DOCTOR
# ============================================================

with tabs[2]:

    st.markdown(
        '<div class="section-title">'
        "🔋 Battery Health Doctor"
        "</div>",
        unsafe_allow_html=True,
    )

    st.info(
        "This is a preliminary screening tool. "
        "It does not replace professional battery testing "
        "or manufacturer specifications."
    )

    # --------------------------------------------------------
    # Battery Overview
    # --------------------------------------------------------

    st.subheader("Battery Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Battery Type",
            battery_analysis["battery_type"],
        )

    with col2:

        st.metric(
            "Voltage",
            f"{battery_analysis['voltage_v']:.1f} V",
        )

    with col3:

        st.metric(
            "Current",
            f"{battery_analysis['current_a']:.1f} A",
        )

    with col4:

        st.metric(
            "Power",
            f"{battery_analysis['power_kw']:.2f} kW",
        )

    # --------------------------------------------------------
    # Capacity Analysis
    # --------------------------------------------------------

    st.subheader("Capacity & SOH Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Rated Capacity",
            f"{battery_analysis['rated_capacity_ah']:.1f} Ah",
        )

    with col2:

        st.metric(
            "Measured Capacity",
            f"{battery_analysis['measured_capacity_ah']:.1f} Ah",
        )

    with col3:

        st.metric(
            "Capacity Health / SOH",
            f"{battery_analysis['soh_percent']:.1f}%",
        )

    # --------------------------------------------------------
    # Health status
    # --------------------------------------------------------

    if health_label == "Healthy":

        st.success(
            "🟢 Battery assessment: HEALTHY"
        )

    elif health_label == "Good":

        st.info(
            "🔵 Battery assessment: GOOD"
        )

    elif health_label == "Needs Attention":

        st.warning(
            "🟠 Battery assessment: NEEDS ATTENTION"
        )

    else:

        st.error(
            "🔴 Battery assessment: POOR"
        )

    # --------------------------------------------------------
    # Battery Condition
    # --------------------------------------------------------

    st.subheader("Battery Condition")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write(
            "**SOC Status**"
        )

        st.write(
            battery_analysis["soc_status"]
        )

        st.caption(
            battery_analysis["soc_message"]
        )

    with col2:

        st.write(
            "**Temperature Status**"
        )

        st.write(
            battery_analysis["temperature_status"]
        )

        st.caption(
            battery_analysis["temperature_message"]
        )

    with col3:

        st.write(
            "**Age Status**"
        )

        st.write(
            battery_analysis["age_status"]
        )

        st.caption(
            battery_analysis["age_message"]
        )

    # --------------------------------------------------------
    # Risk Assessment
    # --------------------------------------------------------

    st.subheader("Risk Assessment")

    risk_level = battery_analysis["risk_level"]

    if risk_level == "Low":

        st.success(
            f"🟢 Risk Level: **{risk_level}**"
        )

    elif risk_level == "Moderate":

        st.info(
            f"🔵 Risk Level: **{risk_level}**"
        )

    elif risk_level == "High":

        st.warning(
            f"🟠 Risk Level: **{risk_level}**"
        )

    else:

        st.error(
            f"🔴 Risk Level: **{risk_level}**"
        )

    st.write(
        f"Risk screening score: "
        f"**{battery_analysis['risk_score']}**"
    )

    if battery_analysis["risk_warnings"]:

        st.write("**Risk factors:**")

        for warning in battery_analysis["risk_warnings"]:

            st.write(
                f"• {warning}"
            )

    # --------------------------------------------------------
    # Possible Causes
    # --------------------------------------------------------

    st.subheader("Possible Causes / Factors")

    for cause in battery_analysis["possible_causes"]:

        st.write(
            f"• {cause}"
        )

    # --------------------------------------------------------
    # Symptoms
    # --------------------------------------------------------

    st.subheader("Reported Symptoms")

    if symptoms.strip():

        st.write(
            symptoms
        )

    else:

        st.write(
            "No symptoms provided."
        )

    st.caption(
        "The listed causes are preliminary possibilities, "
        "not confirmed faults."
    )


# ============================================================
# TAB 4 — SPECIALIST AGENTS
# ============================================================

with tabs[3]:

    st.markdown(
        '<div class="section-title">'
        "🤖 Specialist Agents"
        "</div>",
        unsafe_allow_html=True,
    )

    st.info(
        "Phase 4 uses deterministic specialist agents. "
        "Groq-based reasoning and the Supervisor Agent "
        "will be added in later phases."
    )

    # ========================================================
    # AGENT STATUS
    # ========================================================

    st.subheader("Agent Status")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.success(
            "☀️ Solar Agent\n\n"
            "Completed"
        )

    with col2:

        st.success(
            "🔋 Battery Agent\n\n"
            "Completed"
        )

    with col3:

        st.success(
            "⚡ Load Agent\n\n"
            "Completed"
        )

    with col4:

        st.success(
            "🔌 Grid Agent\n\n"
            "Completed"
        )

    # ========================================================
    # SOLAR AGENT
    # ========================================================

    st.subheader("☀️ Solar Agent")

    solar_col1, solar_col2, solar_col3 = st.columns(3)

    with solar_col1:

        st.metric(
            "Solar Generation",
            f"{solar_agent_result['solar_generation_kw']:.2f} kW",
        )

    with solar_col2:

        st.metric(
            "Solar Surplus",
            f"{solar_agent_result['solar_surplus_kw']:.2f} kW",
        )

    with solar_col3:

        st.metric(
            "Solar Deficit",
            f"{solar_agent_result['solar_deficit_kw']:.2f} kW",
        )

    st.write(
        f"**Status:** "
        f"{solar_agent_result['status']}"
    )

    st.write(
        f"**Recommendation:** "
        f"{solar_agent_result['recommendation']}"
    )

    # ========================================================
    # BATTERY AGENT
    # ========================================================

    st.subheader("🔋 Battery Agent")

    battery_col1, battery_col2, battery_col3, battery_col4 = (
        st.columns(4)
    )

    with battery_col1:

        st.metric(
            "SOH",
            f"{battery_agent_result['soh_percent']:.1f}%",
        )

    with battery_col2:

        st.metric(
            "SOC",
            f"{battery_agent_result['soc_percent']:.1f}%",
        )

    with battery_col3:

        st.metric(
            "Temperature",
            f"{battery_agent_result['temperature_c']:.1f} °C",
        )

    with battery_col4:

        st.metric(
            "Risk",
            battery_agent_result["risk_level"],
        )

    st.write(
        f"**Status:** "
        f"{battery_agent_result['status']}"
    )

    st.write(
        f"**Recommendation:** "
        f"{battery_agent_result['recommendation']}"
    )

    # ========================================================
    # LOAD AGENT
    # ========================================================

    st.subheader("⚡ Load Agent")

    load_col1, load_col2, load_col3 = st.columns(3)

    with load_col1:

        st.metric(
            "Current Load",
            f"{load_agent_result['current_load_kw']:.2f} kW",
        )

    with load_col2:

        st.metric(
            "Essential Load",
            f"{load_agent_result['essential_load_kw']:.2f} kW",
        )

    with load_col3:

        st.metric(
            "Non-Essential Load",
            f"{load_agent_result['non_essential_load_kw']:.2f} kW",
        )

    st.write(
        f"**Status:** "
        f"{load_agent_result['status']}"
    )

    st.write(
        f"**Recommendation:** "
        f"{load_agent_result['recommendation']}"
    )

    # ========================================================
    # GRID AGENT
    # ========================================================

    st.subheader("🔌 Grid Agent")

    grid_col1, grid_col2, grid_col3 = st.columns(3)

    with grid_col1:

        st.metric(
            "Grid Status",
            grid_agent_result["grid_status"],
        )

    with grid_col2:

        st.metric(
            "Recommended Import",
            f"{grid_agent_result['recommended_grid_import_kw']:.2f} kW",
        )

    with grid_col3:

        st.metric(
            "Estimated Cost",
            f"Rs {grid_agent_result['estimated_cost_rs']:.2f}",
        )

    st.write(
        f"**Recommendation:** "
        f"{grid_agent_result['recommendation']}"
    )

    # ========================================================
    # AGENT SUMMARY
    # ========================================================

    st.subheader("📋 Specialist Agent Summary")

    agent_summary = pd.DataFrame(
        [
            [
                "☀️ Solar Agent",
                solar_agent_result["status"],
                solar_agent_result["recommendation"],
            ],
            [
                "🔋 Battery Agent",
                battery_agent_result["status"],
                battery_agent_result["recommendation"],
            ],
            [
                "⚡ Load Agent",
                load_agent_result["status"],
                load_agent_result["recommendation"],
            ],
            [
                "🔌 Grid Agent",
                grid_agent_result["grid_status"],
                grid_agent_result["recommendation"],
            ],
        ],
        columns=[
            "Agent",
            "Status",
            "Recommendation",
        ],
    )

    st.dataframe(
        agent_summary,
        use_container_width=True,
        hide_index=True,
    )

# ============================================================
# TAB 5 — KNOWLEDGE / RAG
# ============================================================

with tabs[4]:

    st.markdown(
        '<div class="section-title">📚 Knowledge / RAG</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "RAG will be implemented after the agent architecture "
        "and Groq integration."
    )

    st.write(
        """
        Planned knowledge sources:

        • Battery maintenance
        • Battery safety
        • Lead-acid batteries
        • Lithium-ion batteries
        • Solar PV
        • Inverters
        • Energy management
        • DER hosting capacity
        """
    )


# ============================================================
# TAB 6 — REPORTS
# ============================================================

with tabs[5]:

    st.markdown(
        '<div class="section-title">📄 Reports & Insights</div>',
        unsafe_allow_html=True,
    )

    report_data = {

        "Parameter": [

            "Scenario",

            "Solar Generation",

            "Current Load",

            "Battery Type",

            "Battery Voltage",

            "Rated Capacity",

            "Measured Capacity",

            "Battery SOC",

            "Battery SOH",

            "Health Label",

            "Battery Current",

            "Battery Power",

            "Temperature",

            "Battery Age",

            "Risk Level",

            "Grid Status",

        ],

        "Value": [

            selected_scenario,

            f"{solar_kw:.2f} kW",

            f"{load_kw:.2f} kW",

            battery_analysis["battery_type"],

            f"{battery_analysis['voltage_v']:.2f} V",

            f"{battery_analysis['rated_capacity_ah']:.2f} Ah",

            f"{battery_analysis['measured_capacity_ah']:.2f} Ah",

            f"{battery_analysis['soc_percent']:.1f}%",

            f"{battery_analysis['soh_percent']:.1f}%",

            battery_analysis["health_label"],

            f"{battery_analysis['current_a']:.2f} A",

            f"{battery_analysis['power_kw']:.2f} kW",

            f"{battery_analysis['temperature_c']:.1f} °C",

            f"{battery_analysis['age_years']:.1f} years",

            battery_analysis["risk_level"],

            "Available"
            if grid_available
            else "Unavailable",
        ],
    }

    report_df = pd.DataFrame(
        report_data
    )

    st.dataframe(
        report_df,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    st.subheader("Energy Recommendations")

    recommendations = get_recommendation(
        solar_kw=solar_kw,
        load_kw=load_kw,
        battery_soc=battery_soc,
        battery_health=battery_analysis["soh_percent"],
        temperature_c=temperature_c,
        grid_available=grid_available,
    )

    for recommendation in recommendations:

        st.write(
            f"• {recommendation}"
        )

    # --------------------------------------------------------
    # Historical data
    # --------------------------------------------------------

    st.subheader("Sample Historical Energy Data")

    sample_df = load_sample_data()

    st.dataframe(
        sample_df,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    csv_data = report_df.to_csv(
        index=False
    )

    st.download_button(
        label="⬇️ Download Battery & Energy Report",
        data=csv_data,
        file_name="solarsathi_phase3_report.csv",
        mime="text/csv",
    )


# ============================================================
# TAB 7 — SETTINGS
# ============================================================

with tabs[6]:

    st.markdown(
        '<div class="section-title">⚙️ Settings</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Battery Health Thresholds")

    st.write(
        "Healthy: **≥ 85% SOH**"
    )

    st.write(
        "Good: **70–84% SOH**"
    )

    st.write(
        "Needs Attention: **50–69% SOH**"
    )

    st.write(
        "Poor: **< 50% SOH**"
    )

    st.caption(
        "These are demonstration thresholds and should not "
        "be treated as universal manufacturer limits."
    )

    st.subheader("Phase Status")

    status_df = pd.DataFrame(
        [
            ["Phase 1", "Streamlit Dashboard", "Completed"],
            ["Phase 2", "Energy Calculation Tools", "Completed"],
            ["Phase 3", "Battery Health Tools", "Completed"],
            ["Phase 4", "Solar/Battery/Load/Grid Agents", "Next"],
            ["Phase 5", "Supervisor Agent", "Planned"],
            ["Phase 6", "Groq Integration", "Planned"],
            ["Phase 7", "Session Memory", "Planned"],
            ["Phase 8", "RAG", "Planned"],
            ["Phase 9", "Agentic RAG", "Planned"],
            ["Phase 10", "Workflow & Automation", "Planned"],
        ],
        columns=[
            "Phase",
            "Feature",
            "Status",
        ],
    )

    st.dataframe(
        status_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# SAFETY DISCLAIMER
# ============================================================

st.markdown("---")

st.warning(
    """
    ⚠️ **Safety Disclaimer**

    SolarSathi AI provides simulation-based and informational
    recommendations. It does not directly control electrical
    equipment.

    Electrical installations, battery servicing, grid connections,
    inverter configuration, protection-system changes, and other
    electrical work must be performed or verified by qualified
    professionals.

    Battery health results are preliminary screening results and
    must not be treated as certified battery diagnostics.
    """
)

st.caption(
    "SolarSathi AI — Agentic Solar + Battery Energy Manager & Battery Health Doctor"
)
