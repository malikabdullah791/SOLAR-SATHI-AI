import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from tools.energy_tools import (
    calculate_energy_flow,
    calculate_backup_time,
    calculate_energy_cost,
    check_energy_balance,
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

    .info-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #f5f7fa;
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }

    .warning-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #fff7ed;
        border: 1px solid #fed7aa;
        margin-bottom: 15px;
    }

    .success-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        margin-bottom: 15px;
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
        "temperature_c": 28.0,
        "grid_available": True,
        "grid_tariff": 50.0,
    },

    "Evening / Load Shedding": {
        "solar_kw": 0.0,
        "load_kw": 4.0,
        "battery_soc": 40.0,
        "battery_capacity_kwh": 10.0,
        "battery_health": 88.0,
        "temperature_c": 30.0,
        "grid_available": False,
        "grid_tariff": 50.0,
    },

    "Battery Health Problem": {
        "solar_kw": 1.0,
        "load_kw": 3.0,
        "battery_soc": 30.0,
        "battery_capacity_kwh": 10.0,
        "battery_health": 55.0,
        "temperature_c": 43.0,
        "grid_available": True,
        "grid_tariff": 50.0,
    },

    "High Solar Surplus": {
        "solar_kw": 7.0,
        "load_kw": 2.0,
        "battery_soc": 50.0,
        "battery_capacity_kwh": 10.0,
        "battery_health": 90.0,
        "temperature_c": 29.0,
        "grid_available": True,
        "grid_tariff": 50.0,
    },
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_battery_health_label(health):
    """Convert battery health percentage into a simple label."""

    if health >= 85:
        return "Healthy"
    elif health >= 70:
        return "Good"
    elif health >= 50:
        return "Needs Attention"
    else:
        return "Poor"


def get_recommendation(
    solar_kw,
    load_kw,
    battery_soc,
    battery_health,
    temperature_c,
    grid_available,
):
    """Generate a simple deterministic recommendation."""

    recommendations = []

    # Solar condition
    if solar_kw > load_kw:
        recommendations.append(
            "Solar generation is higher than the current load. "
            "Use the surplus for battery charging where appropriate."
        )

    elif solar_kw < load_kw:
        recommendations.append(
            "Solar generation is below the current load. "
            "Battery or grid support may be required."
        )

    else:
        recommendations.append(
            "Solar generation is approximately matching the current load."
        )

    # Battery SOC
    if battery_soc < 20:
        recommendations.append(
            "Battery SOC is very low. Avoid unnecessary battery discharge."
        )

    elif battery_soc < 40:
        recommendations.append(
            "Battery SOC is relatively low. Prioritize essential loads."
        )

    elif battery_soc > 90:
        recommendations.append(
            "Battery SOC is high. Use available solar surplus carefully."
        )

    # Battery health
    if battery_health < 50:
        recommendations.append(
            "Battery health is poor according to this simplified model. "
            "Consider inspection and further testing."
        )

    elif battery_health < 70:
        recommendations.append(
            "Battery health needs attention. Further testing is recommended."
        )

    # Temperature
    if temperature_c >= 40:
        recommendations.append(
            "Battery temperature is high. Avoid aggressive operation "
            "and have the system checked by a qualified professional."
        )

    # Grid
    if not grid_available:
        recommendations.append(
            "Grid is unavailable. Prioritize essential loads and "
            "preserve battery SOC."
        )

    else:
        recommendations.append(
            "Grid is available. Use it when solar and battery resources "
            "cannot safely meet demand."
        )

    return recommendations


def create_energy_flow_chart(flow):
    """Create Plotly Sankey diagram."""

    labels = [
        "Solar",
        "Battery",
        "Grid",
        "Load",
        "Battery Charging",
        "Solar Export",
        "Unserved Load",
    ]

    solar_to_load = flow["solar_to_load_kw"]
    solar_to_battery = flow["solar_to_battery_kw"]
    battery_to_load = flow["battery_to_load_kw"]
    grid_to_load = flow["grid_to_load_kw"]
    solar_export = flow["solar_export_kw"]
    unserved_load = flow["unserved_load_kw"]

    source = []
    target = []
    value = []

    if solar_to_load > 0:
        source.append(0)
        target.append(3)
        value.append(solar_to_load)

    if solar_to_battery > 0:
        source.append(0)
        target.append(4)
        value.append(solar_to_battery)

    if battery_to_load > 0:
        source.append(1)
        target.append(3)
        value.append(battery_to_load)

    if grid_to_load > 0:
        source.append(2)
        target.append(3)
        value.append(grid_to_load)

    if solar_export > 0:
        source.append(0)
        target.append(5)
        value.append(solar_export)

    if unserved_load > 0:
        source.append(0)
        target.append(6)
        value.append(unserved_load)

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
        font_size=13,
        height=450,
    )

    return fig


def load_sample_data():
    """Create sample historical energy data."""

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

scenario_data = DEMO_SCENARIOS[selected_scenario]

st.sidebar.markdown("---")

st.sidebar.subheader("Current System")

solar_kw = st.sidebar.number_input(
    "Solar Generation (kW)",
    min_value=0.0,
    value=float(scenario_data["solar_kw"]),
    step=0.1,
)

load_kw = st.sidebar.number_input(
    "Current Load (kW)",
    min_value=0.0,
    value=float(scenario_data["load_kw"]),
    step=0.1,
)

battery_soc = st.sidebar.slider(
    "Battery SOC (%)",
    min_value=0.0,
    max_value=100.0,
    value=float(scenario_data["battery_soc"]),
    step=1.0,
)

battery_capacity = st.sidebar.number_input(
    "Battery Capacity (kWh)",
    min_value=0.1,
    value=float(scenario_data["battery_capacity_kwh"]),
    step=0.5,
)

battery_health = st.sidebar.slider(
    "Battery Health (%)",
    min_value=0.0,
    max_value=100.0,
    value=float(scenario_data["battery_health"]),
    step=1.0,
)

temperature_c = st.sidebar.number_input(
    "Battery Temperature (°C)",
    min_value=-20.0,
    max_value=100.0,
    value=float(scenario_data["temperature_c"]),
    step=1.0,
)

grid_available = st.sidebar.checkbox(
    "Grid Available",
    value=bool(scenario_data["grid_available"]),
)

grid_tariff = st.sidebar.number_input(
    "Grid Tariff (Rs/kWh)",
    min_value=0.0,
    value=float(scenario_data["grid_tariff"]),
    step=1.0,
)


# ============================================================
# CALCULATIONS
# ============================================================

try:

    calculated_flow = calculate_energy_flow(
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

    estimated_energy_cost = calculate_energy_cost(
        energy_kwh=load_kw,
        tariff_rs_per_kwh=grid_tariff,
    )

    energy_balance = check_energy_balance(
        supply_kw=calculated_flow["total_supply_kw"],
        demand_kw=calculated_flow["total_demand_kw"],
    )

except ValueError as error:

    st.error(
        f"Input validation error: {error}"
    )

    st.stop()


# ============================================================
# KPI DASHBOARD
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

    grid_status = (
        "Available"
        if grid_available
        else "Unavailable"
    )

    st.metric(
        "🔌 Grid",
        grid_status,
    )

with col5:

    st.metric(
        "❤️ Battery Health",
        f"{battery_health:.0f}%",
    )


# ============================================================
# BATTERY STATUS
# ============================================================

health_label = get_battery_health_label(
    battery_health
)

if health_label == "Healthy":
    st.success(
        f"🔋 Battery Status: **{health_label}** ({battery_health:.0f}%)"
    )

elif health_label == "Good":
    st.info(
        f"🔋 Battery Status: **{health_label}** ({battery_health:.0f}%)"
    )

elif health_label == "Needs Attention":
    st.warning(
        f"🔋 Battery Status: **{health_label}** ({battery_health:.0f}%)"
    )

else:
    st.error(
        f"🔋 Battery Status: **{health_label}** ({battery_health:.0f}%)"
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
# TAB 1 - DASHBOARD
# ============================================================

with tabs[0]:

    st.markdown(
        '<div class="section-title">Energy Flow</div>',
        unsafe_allow_html=True,
    )

    chart_col, summary_col = st.columns(
        [2, 1]
    )

    with chart_col:

        fig = create_energy_flow_chart(
            calculated_flow
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with summary_col:

        st.subheader("Energy Summary")

        st.write(
            f"Solar → Load: "
            f"**{calculated_flow['solar_to_load_kw']:.2f} kW**"
        )

        st.write(
            f"Solar → Battery: "
            f"**{calculated_flow['solar_to_battery_kw']:.2f} kW**"
        )

        st.write(
            f"Battery → Load: "
            f"**{calculated_flow['battery_to_load_kw']:.2f} kW**"
        )

        st.write(
            f"Grid → Load: "
            f"**{calculated_flow['grid_to_load_kw']:.2f} kW**"
        )

        st.write(
            f"Solar Export: "
            f"**{calculated_flow['solar_export_kw']:.2f} kW**"
        )

        st.write(
            f"Unserved Load: "
            f"**{calculated_flow['unserved_load_kw']:.2f} kW**"
        )

        st.divider()

        if energy_balance["balanced"]:
            st.success(
                "✅ Energy balance is approximately balanced."
            )
        else:
            st.warning(
                "⚠️ Energy balance has a small difference."
            )


# ============================================================
# TAB 2 - ENERGY MANAGER
# ============================================================

with tabs[1]:

    st.markdown(
        '<div class="section-title">⚡ Energy Manager</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "The Energy Manager uses deterministic Python calculations "
        "to estimate how solar, battery, and grid resources can "
        "serve the current load."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Solar Surplus",
            f"{calculated_flow['solar_surplus_kw']:.2f} kW",
        )

    with col2:

        st.metric(
            "Solar Deficit",
            f"{calculated_flow['solar_deficit_kw']:.2f} kW",
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

    st.subheader("Calculated Energy Flow")

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
                calculated_flow["solar_to_load_kw"],
                calculated_flow["solar_to_battery_kw"],
                calculated_flow["battery_to_load_kw"],
                calculated_flow["grid_to_load_kw"],
                calculated_flow["solar_export_kw"],
                calculated_flow["unserved_load_kw"],
            ],
        }
    )

    st.dataframe(
        flow_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Estimated Grid Cost")

    st.write(
        f"Current estimated load energy cost: "
        f"**Rs {estimated_energy_cost:,.2f}**"
    )

    st.caption(
        "This is a simplified calculation based on current load "
        "and configured tariff."
    )


# ============================================================
# TAB 3 - BATTERY HEALTH DOCTOR
# ============================================================

with tabs[2]:

    st.markdown(
        '<div class="section-title">🔋 Battery Health Doctor</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "This preliminary battery assessment uses the current "
        "demo parameters. It is intended for decision support "
        "and does not replace professional battery testing."
    )

    health_col1, health_col2 = st.columns(2)

    with health_col1:

        st.metric(
            "Battery Health",
            f"{battery_health:.0f}%",
        )

        st.metric(
            "Battery Temperature",
            f"{temperature_c:.1f} °C",
        )

        st.metric(
            "Battery SOC",
            f"{battery_soc:.0f}%",
        )

    with health_col2:

        st.subheader("Assessment")

        if battery_health >= 85:
            st.success(
                "Healthy: preliminary indication is good."
            )

        elif battery_health >= 70:
            st.info(
                "Good: battery appears usable, "
                "but monitoring is recommended."
            )

        elif battery_health >= 50:
            st.warning(
                "Needs Attention: further testing and "
                "maintenance assessment are recommended."
            )

        else:
            st.error(
                "Poor: inspection and further testing "
                "are strongly recommended."
            )

        if temperature_c >= 40:

            st.warning(
                "⚠️ Battery temperature is relatively high. "
                "Avoid aggressive operation and consult a "
                "qualified professional."
            )

        elif temperature_c >= 35:

            st.info(
                "Battery temperature is elevated. "
                "Continue monitoring."
            )

        else:

            st.success(
                "Battery temperature is within the "
                "configured demo range."
            )

    st.subheader("Possible Factors")

    possible_factors = []

    if battery_health < 70:
        possible_factors.append(
            "Possible capacity degradation or aging."
        )

    if temperature_c >= 40:
        possible_factors.append(
            "Possible effect of elevated operating temperature."
        )

    if battery_soc < 20:
        possible_factors.append(
            "Very low state of charge."
        )

    if not possible_factors:
        possible_factors.append(
            "No major warning factor detected by this "
            "simplified assessment."
        )

    for factor in possible_factors:
        st.write(f"• {factor}")

    st.caption(
        "Health thresholds are demonstration thresholds and "
        "should be configured according to battery chemistry, "
        "manufacturer specifications, operating conditions, "
        "and professional testing."
    )


# ============================================================
# TAB 4 - AI AGENT
# ============================================================

with tabs[3]:

    st.markdown(
        '<div class="section-title">🤖 AI Agent</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "AI agent integration will be added in the next phase "
        "using the Groq API. The current phase uses deterministic "
        "Python calculations."
    )

    st.subheader("Current Agentic Architecture")

    st.write(
        """
        **Future workflow:**

        User Request
        ↓
        Supervisor Agent
        ↓
        ├── Solar Agent
        ├── Battery Agent
        ├── Load Agent
        └── Grid Agent
        ↓
        Energy Calculation Tools
        ↓
        Supervisor Review
        ↓
        Final Recommendation
        """
    )

    st.subheader("Current Activity")

    activity = [
        "✓ Streamlit dashboard loaded",
        "✓ Scenario parameters validated",
        "✓ Energy calculation tool executed",
        "✓ Energy flow calculated",
        "✓ Battery backup estimate calculated",
        "✓ Energy balance checked",
        "✓ Preliminary recommendation generated",
    ]

    for item in activity:
        st.write(item)


# ============================================================
# TAB 5 - KNOWLEDGE / RAG
# ============================================================

with tabs[4]:

    st.markdown(
        '<div class="section-title">📚 Knowledge / RAG</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "Retrieval-Augmented Generation (RAG) will be implemented "
        "in a later phase."
    )

    st.write(
        """
        Planned knowledge sources:

        • Solar PV basics
        • Battery charging and maintenance
        • Battery safety
        • Inverter fundamentals
        • Energy management
        • DER / distributed energy resources
        • Solar + battery troubleshooting
        """
    )

    st.subheader("Planned Agentic RAG Flow")

    st.write(
        """
        User Question
        ↓
        Supervisor Agent
        ↓
        Retrieve Relevant Knowledge
        ↓
        Observe Retrieved Information
        ↓
        Decide if Information is Sufficient
        ↓
        Retrieve Again if Necessary
        ↓
        Battery / Solar / Grid Agent
        ↓
        Final Answer + Sources
        """
    )


# ============================================================
# TAB 6 - REPORTS & INSIGHTS
# ============================================================

with tabs[5]:

    st.markdown(
        '<div class="section-title">📄 Reports & Insights</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Current System Report")

    report_data = {
        "Parameter": [
            "Scenario",
            "Solar Generation",
            "Current Load",
            "Battery SOC",
            "Battery Capacity",
            "Battery Health",
            "Battery Temperature",
            "Grid Status",
            "Grid Tariff",
            "Estimated Backup",
            "Estimated Load Cost",
        ],
        "Value": [
            selected_scenario,
            f"{solar_kw:.2f} kW",
            f"{load_kw:.2f} kW",
            f"{battery_soc:.1f}%",
            f"{battery_capacity:.2f} kWh",
            f"{battery_health:.1f}%",
            f"{temperature_c:.1f} °C",
            "Available" if grid_available else "Unavailable",
            f"Rs {grid_tariff:.2f}/kWh",
            (
                "N/A"
                if backup_time == float("inf")
                else f"{backup_time:.2f} hours"
            ),
            f"Rs {estimated_energy_cost:,.2f}",
        ],
    }

    report_df = pd.DataFrame(report_data)

    st.dataframe(
        report_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Recommendation")

    recommendations = get_recommendation(
        solar_kw=solar_kw,
        load_kw=load_kw,
        battery_soc=battery_soc,
        battery_health=battery_health,
        temperature_c=temperature_c,
        grid_available=grid_available,
    )

    for recommendation in recommendations:
        st.write(
            f"• {recommendation}"
        )

    st.subheader("Sample Historical Data")

    sample_df = load_sample_data()

    st.dataframe(
        sample_df,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = report_df.to_csv(
        index=False
    )

    st.download_button(
        label="⬇️ Download Current Report CSV",
        data=csv_data,
        file_name="solarsathi_energy_report.csv",
        mime="text/csv",
    )


# ============================================================
# TAB 7 - SETTINGS
# ============================================================

with tabs[6]:

    st.markdown(
        '<div class="section-title">⚙️ Settings</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Simulation Settings")

    st.write(
        "Minimum battery SOC: **20%**"
    )

    st.write(
        "Maximum demo battery charging power: **5 kW**"
    )

    st.write(
        "Maximum demo battery discharge power: **5 kW**"
    )

    st.write(
        "Battery usable fraction for backup estimate: **90%**"
    )

    st.subheader("Project Status")

    status_items = [
        ("Phase 1", "Streamlit dashboard", "Completed"),
        ("Phase 2", "Energy calculation engine", "Completed"),
        ("Phase 3", "Battery health tools", "Next"),
        ("Phase 4", "Specialized agents", "Planned"),
        ("Phase 5", "Supervisor agent", "Planned"),
        ("Phase 6", "Groq integration", "Planned"),
        ("Phase 7", "Session memory", "Planned"),
        ("Phase 8", "RAG", "Planned"),
        ("Phase 9", "Agentic RAG", "Planned"),
        ("Phase 10", "Workflow & reports", "Planned"),
    ]

    status_df = pd.DataFrame(
        status_items,
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

    The calculations shown by this application are simplified
    demonstrations and should not be treated as industrial-grade
    protection, control, battery diagnostics, or electrical design.
    """
)

st.caption(
    "SolarSathi AI — Agentic Solar + Battery Energy Manager & Battery Health Doctor"
)
