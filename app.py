import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


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
# DEMO SCENARIOS
# ============================================================

DEMO_SCENARIOS = {
    "Sunny Day": {
        "description": "High solar generation with moderate household demand.",
        "solar_kw": 5.0,
        "load_kw": 3.0,
        "battery_soc": 60.0,
        "battery_capacity_kwh": 10.0,
        "battery_health": 92.0,
        "temperature_c": 29.0,
        "grid_available": True,
        "grid_tariff": 45.0,
        "solar_to_load": 3.0,
        "solar_to_battery": 2.0,
        "battery_to_load": 0.0,
        "grid_to_load": 0.0,
        "grid_to_battery": 0.0,
        "solar_export": 0.0,
    },

    "Evening / Load Shedding": {
        "description": "No solar generation and the grid is unavailable.",
        "solar_kw": 0.0,
        "load_kw": 4.0,
        "battery_soc": 40.0,
        "battery_capacity_kwh": 10.0,
        "battery_health": 88.0,
        "temperature_c": 30.0,
        "grid_available": False,
        "grid_tariff": 45.0,
        "solar_to_load": 0.0,
        "solar_to_battery": 0.0,
        "battery_to_load": 2.5,
        "grid_to_load": 0.0,
        "grid_to_battery": 0.0,
        "solar_export": 0.0,
    },

    "Battery Health Problem": {
        "description": "Battery temperature is high and estimated capacity health is low.",
        "solar_kw": 1.5,
        "load_kw": 3.0,
        "battery_soc": 30.0,
        "battery_capacity_kwh": 10.0,
        "battery_health": 55.0,
        "temperature_c": 43.0,
        "grid_available": True,
        "grid_tariff": 45.0,
        "solar_to_load": 1.5,
        "solar_to_battery": 0.0,
        "battery_to_load": 0.0,
        "grid_to_load": 1.5,
        "grid_to_battery": 0.0,
        "solar_export": 0.0,
    },

    "High Solar Surplus": {
        "description": "Solar generation is much higher than the current load.",
        "solar_kw": 7.0,
        "load_kw": 2.0,
        "battery_soc": 50.0,
        "battery_capacity_kwh": 10.0,
        "battery_health": 95.0,
        "temperature_c": 28.0,
        "grid_available": True,
        "grid_tariff": 45.0,
        "solar_to_load": 2.0,
        "solar_to_battery": 3.0,
        "battery_to_load": 0.0,
        "grid_to_load": 0.0,
        "grid_to_battery": 0.0,
        "solar_export": 2.0,
    },
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_sample_data():
    """Load the sample energy data from the data folder."""

    file_path = Path("data/sample_energy_data.csv")

    if not file_path.exists():
        return None

    try:
        data = pd.read_csv(file_path)
        return data
    except Exception:
        return None


def get_battery_health_label(health):
    """Return a simple battery-health label."""

    if health >= 85:
        return "Healthy"
    elif health >= 70:
        return "Good"
    elif health >= 50:
        return "Needs Attention"
    else:
        return "Poor"


def get_recommendation(scenario):
    """Generate a simple Phase 1 rule-based recommendation.

    This is intentionally simple.
    More advanced deterministic calculations will be added in Phase 2.
    """

    if scenario == "Sunny Day":
        return (
            "☀️ Use solar power for the current load. "
            "The available surplus can be used to charge the battery "
            "and reduce dependence on the grid."
        )

    if scenario == "Evening / Load Shedding":
        return (
            "🔋 Grid power is unavailable. Use the battery carefully "
            "and prioritize essential loads because battery SOC is only 40%."
        )

    if scenario == "Battery Health Problem":
        return (
            "⚠️ Battery health requires attention. High temperature and "
            "low estimated health suggest that aggressive battery cycling "
            "should be avoided. Professional inspection is recommended."
        )

    if scenario == "High Solar Surplus":
        return (
            "☀️ Solar generation is much higher than the current load. "
            "Use solar for the load, charge the battery with suitable surplus, "
            "and consider export or curtailment for remaining generation."
        )

    return "No recommendation available."


def create_energy_flow_chart(data):
    """Create a simple Sankey diagram showing the demo energy flow."""

    labels = [
        "Solar",
        "Grid",
        "Battery",
        "Load",
        "Battery Charging",
        "Export",
    ]

    sources = []
    targets = []
    values = []

    # Solar -> Load
    if data["solar_to_load"] > 0:
        sources.append(0)
        targets.append(3)
        values.append(data["solar_to_load"])

    # Solar -> Battery
    if data["solar_to_battery"] > 0:
        sources.append(0)
        targets.append(4)
        values.append(data["solar_to_battery"])

    # Solar -> Export
    if data["solar_export"] > 0:
        sources.append(0)
        targets.append(5)
        values.append(data["solar_export"])

    # Grid -> Load
    if data["grid_to_load"] > 0:
        sources.append(1)
        targets.append(3)
        values.append(data["grid_to_load"])

    # Battery -> Load
    if data["battery_to_load"] > 0:
        sources.append(2)
        targets.append(3)
        values.append(data["battery_to_load"])

    # Grid -> Battery
    if data["grid_to_battery"] > 0:
        sources.append(1)
        targets.append(4)
        values.append(data["grid_to_battery"])

    figure = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=20,
                    thickness=25,
                    label=labels,
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                ),
            )
        ]
    )

    figure.update_layout(
        title="Energy Flow — Demo Simulation",
        height=450,
        font=dict(size=14),
    )

    return figure


# ============================================================
# HEADER
# ============================================================

st.title("☀️ SolarSathi AI")

st.subheader("Your Solar System's AI Companion")

st.markdown(
    """
SolarSathi AI is a simulation-based energy management assistant for
homes, small shops and small industrial users.

It combines solar generation, electrical load, battery status and grid
information to provide understandable energy recommendations.
"""
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Demo Controls")

selected_scenario = st.sidebar.selectbox(
    "Select Demo Scenario",
    list(DEMO_SCENARIOS.keys()),
)

scenario_data = DEMO_SCENARIOS[selected_scenario]

st.sidebar.markdown("---")

st.sidebar.write("### Scenario")

st.sidebar.info(scenario_data["description"])

st.sidebar.markdown("---")

st.sidebar.write("### System Parameters")

st.sidebar.write(
    f"☀️ Solar: **{scenario_data['solar_kw']:.1f} kW**"
)

st.sidebar.write(
    f"🏠 Load: **{scenario_data['load_kw']:.1f} kW**"
)

st.sidebar.write(
    f"🔋 Battery SOC: **{scenario_data['battery_soc']:.0f}%**"
)

grid_status = "Available" if scenario_data["grid_available"] else "Unavailable"

st.sidebar.write(
    f"⚡ Grid: **{grid_status}**"
)


# ============================================================
# TOP KPI CARDS
# ============================================================

st.markdown("## 📊 System Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "☀️ Solar Generation",
        f"{scenario_data['solar_kw']:.1f} kW",
    )

with col2:
    st.metric(
        "🔋 Battery SOC",
        f"{scenario_data['battery_soc']:.0f}%",
    )

with col3:
    st.metric(
        "🏠 Current Load",
        f"{scenario_data['load_kw']:.1f} kW",
    )

with col4:
    st.metric(
        "⚡ Grid Status",
        "Available" if scenario_data["grid_available"] else "Load Shedding",
    )

with col5:
    health_label = get_battery_health_label(
        scenario_data["battery_health"]
    )

    st.metric(
        "❤️ Battery Health",
        health_label,
        f"{scenario_data['battery_health']:.0f}%",
    )


# ============================================================
# MAIN TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "🏠 Dashboard",
        "⚡ Energy Manager",
        "🔋 Battery Health Doctor",
        "🤖 AI Agent",
        "📚 Knowledge / RAG",
        "📊 Reports & Insights",
        "⚙️ Settings",
    ]
)


# ============================================================
# DASHBOARD TAB
# ============================================================

with tab1:

    st.markdown("## 🏠 Energy Dashboard")

    st.info(
        f"Current demonstration scenario: **{selected_scenario}**"
    )

    left, right = st.columns([1.3, 1])

    with left:

        st.plotly_chart(
            create_energy_flow_chart(scenario_data),
            use_container_width=True,
        )

    with right:

        st.markdown("### 💡 Current Recommendation")

        st.success(
            get_recommendation(selected_scenario)
        )

        st.markdown("### 🔎 System Status")

        if scenario_data["battery_health"] >= 85:
            st.success("🟢 Battery health is currently healthy.")
        elif scenario_data["battery_health"] >= 70:
            st.info("🔵 Battery health is currently good.")
        elif scenario_data["battery_health"] >= 50:
            st.warning("🟠 Battery health needs attention.")
        else:
            st.error("🔴 Battery health is poor.")

        if scenario_data["temperature_c"] >= 40:
            st.error(
                f"⚠️ High battery temperature detected: "
                f"{scenario_data['temperature_c']:.1f} °C"
            )

        if scenario_data["battery_soc"] <= 30:
            st.warning(
                "Battery SOC is low. Avoid unnecessary discharge."
            )

        if not scenario_data["grid_available"]:
            st.warning(
                "Grid is unavailable. Essential loads should be prioritized."
            )


# ============================================================
# ENERGY MANAGER TAB
# ============================================================

with tab2:

    st.markdown("## ⚡ Energy Manager")

    st.write(
        "This section provides a basic visualization of the current "
        "solar, load, battery and grid situation."
    )

    energy_data = pd.DataFrame(
        {
            "Source": [
                "Solar → Load",
                "Solar → Battery",
                "Battery → Load",
                "Grid → Load",
                "Grid → Battery",
                "Solar → Export",
            ],
            "Power (kW)": [
                scenario_data["solar_to_load"],
                scenario_data["solar_to_battery"],
                scenario_data["battery_to_load"],
                scenario_data["grid_to_load"],
                scenario_data["grid_to_battery"],
                scenario_data["solar_export"],
            ],
        }
    )

    st.dataframe(
        energy_data,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Current Operating Mode")

    if scenario_data["solar_kw"] > scenario_data["load_kw"]:
        st.success(
            "☀️ Solar generation is higher than the current load. "
            "This is a solar-surplus condition."
        )
    elif scenario_data["solar_kw"] > 0:
        st.info(
            "☀️ Solar is contributing to the current load."
        )
    else:
        st.warning(
            "🌙 Solar generation is currently unavailable."
        )


# ============================================================
# BATTERY HEALTH TAB
# ============================================================

with tab3:

    st.markdown("## 🔋 Battery Health Doctor")

    st.write(
        "This is a preliminary simulation-based battery health assessment."
    )

    battery_col1, battery_col2 = st.columns(2)

    with battery_col1:

        st.metric(
            "Battery SOC",
            f"{scenario_data['battery_soc']:.0f}%",
        )

        st.metric(
            "Estimated Health",
            f"{scenario_data['battery_health']:.0f}%",
        )

    with battery_col2:

        st.metric(
            "Battery Temperature",
            f"{scenario_data['temperature_c']:.1f} °C",
        )

        st.metric(
            "Battery Capacity",
            f"{scenario_data['battery_capacity_kwh']:.1f} kWh",
        )

    st.markdown("### Preliminary Status")

    if scenario_data["battery_health"] >= 85:
        st.success("🟢 Healthy")
    elif scenario_data["battery_health"] >= 70:
        st.info("🔵 Good")
    elif scenario_data["battery_health"] >= 50:
        st.warning("🟠 Needs Attention")
    else:
        st.error("🔴 Poor")

    if scenario_data["temperature_c"] >= 40:
        st.warning(
            "Possible temperature-related battery stress detected. "
            "Further testing is recommended."
        )

    st.caption(
        "These thresholds are demonstration values only. "
        "Actual battery assessment should follow the manufacturer's "
        "specifications and qualified technical testing."
    )


# ============================================================
# AI AGENT TAB
# ============================================================

with tab4:

    st.markdown("## 🤖 AI Agent")

    st.info(
        "AI agents will be connected in Phase 4–6. "
        "This tab is reserved for the Supervisor Agent and "
        "specialized Solar, Battery, Load and Grid agents."
    )

    st.markdown("### Planned Agent Workflow")

    workflow_steps = [
        "1. User submits an energy question",
        "2. Supervisor Agent understands the request",
        "3. Solar Agent analyzes solar generation",
        "4. Load Agent analyzes demand",
        "5. Battery Agent analyzes battery condition",
        "6. Grid Agent analyzes grid availability",
        "7. Python tools perform deterministic calculations",
        "8. Supervisor combines results",
        "9. Safety checks the recommendation",
        "10. Final recommendation is shown",
    ]

    for step in workflow_steps:
        st.write(step)


# ============================================================
# KNOWLEDGE / RAG TAB
# ============================================================

with tab5:

    st.markdown("## 📚 Knowledge / RAG")

    st.info(
        "The RAG knowledge system will be implemented in Phase 8. "
        "It will retrieve relevant solar and battery technical guidance "
        "before generating AI explanations."
    )

    st.markdown("### Planned Knowledge Sources")

    knowledge_sources = [
        "Solar PV Basics",
        "Battery Charging Guidelines",
        "Battery Safety",
        "Battery Maintenance",
        "Inverter Basics",
        "Energy Management",
        "Distributed Energy Resources",
    ]

    for source in knowledge_sources:
        st.write(f"📄 {source}")


# ============================================================
# REPORTS TAB
# ============================================================

with tab6:

    st.markdown("## 📊 Reports & Insights")

    st.info(
        "Automated daily and weekly reports will be implemented "
        "in Phase 10."
    )

    sample_data = load_sample_data()

    if sample_data is not None:

        st.markdown("### Sample Energy Dataset")

        st.dataframe(
            sample_data,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Solar vs Load")

        figure = go.Figure()

        figure.add_trace(
            go.Scatter(
                x=sample_data["time"],
                y=sample_data["solar_kw"],
                mode="lines+markers",
                name="Solar (kW)",
            )
        )

        figure.add_trace(
            go.Scatter(
                x=sample_data["time"],
                y=sample_data["load_kw"],
                mode="lines+markers",
                name="Load (kW)",
            )
        )

        figure.update_layout(
            xaxis_title="Time",
            yaxis_title="Power (kW)",
            height=400,
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
        )

        st.markdown("### Battery SOC")

        battery_chart = go.Figure()

        battery_chart.add_trace(
            go.Scatter(
                x=sample_data["time"],
                y=sample_data["battery_soc"],
                mode="lines+markers",
                name="Battery SOC (%)",
            )
        )

        battery_chart.update_layout(
            xaxis_title="Time",
            yaxis_title="SOC (%)",
            yaxis_range=[0, 100],
            height=400,
        )

        st.plotly_chart(
            battery_chart,
            use_container_width=True,
        )

    else:

        st.warning(
            "Sample data file was not found. "
            "Please check data/sample_energy_data.csv."
        )


# ============================================================
# SETTINGS TAB
# ============================================================

with tab7:

    st.markdown("## ⚙️ Settings")

    st.markdown("### Current Phase")

    st.success(
        "Phase 1 — Basic Dashboard + Sample Data"
    )

    st.markdown("### Planned System")

    settings_data = {
        "Feature": [
            "Streamlit Dashboard",
            "Python Energy Tools",
            "Multi-Agent System",
            "Groq LLM",
            "Session Memory",
            "RAG",
            "Agentic RAG",
            "Automated Reports",
            "Safety Guardrails",
        ],
        "Status": [
            "✅ Active",
            "🔜 Phase 2",
            "🔜 Phase 4–5",
            "🔜 Phase 6",
            "🔜 Phase 7",
            "🔜 Phase 8",
            "🔜 Phase 9",
            "🔜 Phase 10",
            "🔜 Phase 11",
        ],
    }

    st.table(
        pd.DataFrame(settings_data)
    )


# ============================================================
# SAFETY DISCLAIMER
# ============================================================

st.markdown("---")

st.warning(
    """
⚠️ **Safety Disclaimer**

SolarSathi AI provides simulation-based and informational
recommendations. It does not directly control electrical equipment.

Electrical installations, battery servicing, grid connections,
and protection-system changes must be performed or verified
by qualified professionals.
"""
)

st.caption(
    "SolarSathi AI — Final Hackathon Project | Phase 1"
)
