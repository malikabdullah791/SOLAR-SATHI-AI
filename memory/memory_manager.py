"""
SolarSathi AI - Session Memory Manager

Phase 7

Uses Streamlit session_state for short-term memory.

No database is used.

Memory exists only during the current
Streamlit user session.
"""

import streamlit as st


def initialize_memory():
    """
    Create the SolarSathi session-memory structure.

    This function is safe to call multiple times.
    """

    if "solar_sathi_memory" not in st.session_state:

        st.session_state[
            "solar_sathi_memory"
        ] = {

            "system_profile": {},

            "last_analysis": {},

            "analysis_history": [],

            "last_recommendation": "",

            "last_warnings": [],

            "last_ai_report": "",

        }


def get_memory():
    """
    Return the complete session memory.
    """

    initialize_memory()

    return st.session_state[
        "solar_sathi_memory"
    ]


def update_system_profile(
    profile_data
):
    """
    Store or update the user's energy-system profile.
    """

    initialize_memory()

    memory = st.session_state[
        "solar_sathi_memory"
    ]

    memory[
        "system_profile"
    ].update(
        profile_data
    )


def get_system_profile():
    """
    Return the saved system profile.
    """

    initialize_memory()

    return st.session_state[
        "solar_sathi_memory"
    ][
        "system_profile"
    ]


def save_analysis(
    analysis_data
):
    """
    Save the latest analysis and add it
    to the session history.
    """

    initialize_memory()

    memory = st.session_state[
        "solar_sathi_memory"
    ]

    memory[
        "last_analysis"
    ] = analysis_data

    memory[
        "analysis_history"
    ].append(
        analysis_data
    )

    # Keep only the latest 10 analyses.
    memory[
        "analysis_history"
    ] = memory[
        "analysis_history"
    ][-10:]


def save_recommendation(
    recommendation,
    warnings=None,
):
    """
    Save the latest recommendation and warnings.
    """

    initialize_memory()

    memory = st.session_state[
        "solar_sathi_memory"
    ]

    memory[
        "last_recommendation"
    ] = recommendation

    memory[
        "last_warnings"
    ] = warnings or []


def save_ai_report(
    ai_report
):
    """
    Save the latest AI-generated report.
    """

    initialize_memory()

    memory = st.session_state[
        "solar_sathi_memory"
    ]

    memory[
        "last_ai_report"
    ] = ai_report


def get_analysis_history():
    """
    Return previous analyses.
    """

    initialize_memory()

    return st.session_state[
        "solar_sathi_memory"
    ][
        "analysis_history"
    ]


def clear_memory():
    """
    Clear all SolarSathi session memory.
    """

    st.session_state[
        "solar_sathi_memory"
    ] = {

        "system_profile": {},

        "last_analysis": {},

        "analysis_history": [],

        "last_recommendation": "",

        "last_warnings": [],

        "last_ai_report": "",

    }
