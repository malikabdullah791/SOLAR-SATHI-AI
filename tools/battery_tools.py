"""
SolarSathi AI - Battery Health Tools

Phase 3:
Battery health, capacity, SOH, power, temperature,
SOC and preliminary risk assessment.

IMPORTANT:
These calculations are simplified decision-support calculations.
They are NOT industrial-grade battery diagnostics.
"""


# ============================================================
# BASIC VALIDATION
# ============================================================

def _number(value, name):
    """Convert a value to float and validate it."""

    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a number.")

    return value


def validate_soc(soc):
    """Validate State of Charge."""

    soc = _number(soc, "SOC")

    if soc < 0 or soc > 100:
        raise ValueError("SOC must be between 0 and 100%.")

    return soc


def validate_temperature(temperature_c):
    """Validate battery temperature."""

    temperature_c = _number(
        temperature_c,
        "Battery temperature"
    )

    if temperature_c < -50 or temperature_c > 100:
        raise ValueError(
            "Battery temperature must be between "
            "-50°C and 100°C."
        )

    return temperature_c


# ============================================================
# CAPACITY HEALTH
# ============================================================

def calculate_capacity_health(
    rated_capacity_ah,
    measured_capacity_ah
):
    """
    Calculate battery capacity health.

    Formula:

        Capacity Health (%) =
        Measured Capacity / Rated Capacity × 100

    Example:

        Rated = 100 Ah
        Measured = 80 Ah

        Health = 80%
    """

    rated_capacity_ah = _number(
        rated_capacity_ah,
        "Rated capacity"
    )

    measured_capacity_ah = _number(
        measured_capacity_ah,
        "Measured capacity"
    )

    if rated_capacity_ah <= 0:
        raise ValueError(
            "Rated capacity must be greater than zero."
        )

    if measured_capacity_ah < 0:
        raise ValueError(
            "Measured capacity cannot be negative."
        )

    if measured_capacity_ah > rated_capacity_ah:
        raise ValueError(
            "Measured capacity cannot exceed rated capacity "
            "in this simplified model."
        )

    health = (
        measured_capacity_ah
        / rated_capacity_ah
    ) * 100

    return round(health, 2)


# ============================================================
# BATTERY SOH
# ============================================================

def calculate_battery_soh(
    rated_capacity_ah,
    measured_capacity_ah
):
    """
    Calculate preliminary State of Health (SOH).

    In this simplified model SOH is based on capacity retention.
    """

    capacity_health = calculate_capacity_health(
        rated_capacity_ah,
        measured_capacity_ah
    )

    return round(capacity_health, 2)


# ============================================================
# HEALTH CLASSIFICATION
# ============================================================

def classify_battery_health(soh):
    """
    Classify battery health.

    Demonstration thresholds:

        >= 85%  → Healthy
        70-84%  → Good
        50-69%  → Needs Attention
        < 50%   → Poor

    These thresholds are configurable demonstration values.
    """

    soh = _number(soh, "SOH")

    if soh < 0 or soh > 100:
        raise ValueError(
            "SOH must be between 0 and 100%."
        )

    if soh >= 85:
        return "Healthy"

    elif soh >= 70:
        return "Good"

    elif soh >= 50:
        return "Needs Attention"

    else:
        return "Poor"


# ============================================================
# BATTERY POWER
# ============================================================

def calculate_battery_power(
    voltage_v,
    current_a
):
    """
    Calculate electrical battery power.

    Formula:

        P(kW) = V × I / 1000

    Positive current:
        Discharge / output assumption

    Negative current:
        Charging / input assumption
    """

    voltage_v = _number(
        voltage_v,
        "Battery voltage"
    )

    current_a = _number(
        current_a,
        "Battery current"
    )

    if voltage_v <= 0:
        raise ValueError(
            "Battery voltage must be greater than zero."
        )

    power_kw = (
        voltage_v * current_a
    ) / 1000

    return round(power_kw, 3)


# ============================================================
# TEMPERATURE CHECK
# ============================================================

def check_battery_temperature(
    temperature_c,
    warning_temperature_c=35.0,
    high_temperature_c=40.0
):
    """
    Check battery temperature.

    Demonstration thresholds:

        < 35°C  → Normal
        35-39.9 → Elevated
        >= 40°C → High

    Actual limits depend on battery chemistry and manufacturer.
    """

    temperature_c = validate_temperature(
        temperature_c
    )

    if temperature_c >= high_temperature_c:

        return {
            "status": "High",
            "temperature_c": temperature_c,
            "message": (
                "Battery temperature is high. "
                "Avoid aggressive operation and "
                "consider professional inspection."
            )
        }

    elif temperature_c >= warning_temperature_c:

        return {
            "status": "Elevated",
            "temperature_c": temperature_c,
            "message": (
                "Battery temperature is elevated. "
                "Continue monitoring."
            )
        }

    else:

        return {
            "status": "Normal",
            "temperature_c": temperature_c,
            "message": (
                "Battery temperature is within "
                "the configured demonstration range."
            )
        }


# ============================================================
# SOC CHECK
# ============================================================

def check_battery_soc(
    soc,
    low_soc=20.0,
    warning_soc=40.0,
    high_soc=90.0
):
    """
    Check battery state of charge.
    """

    soc = validate_soc(soc)

    if soc <= low_soc:

        return {
            "status": "Low",
            "soc": soc,
            "message": (
                "Battery SOC is low. "
                "Avoid unnecessary discharge."
            )
        }

    elif soc < warning_soc:

        return {
            "status": "Moderate",
            "soc": soc,
            "message": (
                "Battery SOC is relatively low. "
                "Prioritize important loads."
            )
        }

    elif soc >= high_soc:

        return {
            "status": "High",
            "soc": soc,
            "message": (
                "Battery SOC is high."
            )
        }

    else:

        return {
            "status": "Normal",
            "soc": soc,
            "message": (
                "Battery SOC is within the configured "
                "demonstration range."
            )
        }


# ============================================================
# BATTERY AGE CHECK
# ============================================================

def check_battery_age(
    age_years,
    warning_age_years=3.0,
    high_age_years=5.0
):
    """
    Basic age-based indicator.

    This is only a screening indicator.
    Battery life depends on chemistry, cycling,
    temperature, maintenance and manufacturer.
    """

    age_years = _number(
        age_years,
        "Battery age"
    )

    if age_years < 0:
        raise ValueError(
            "Battery age cannot be negative."
        )

    if age_years >= high_age_years:

        return {
            "status": "High",
            "message": (
                "Battery age is relatively high. "
                "Further testing is recommended."
            )
        }

    elif age_years >= warning_age_years:

        return {
            "status": "Elevated",
            "message": (
                "Battery age may contribute to "
                "capacity degradation."
            )
        }

    else:

        return {
            "status": "Normal",
            "message": (
                "Battery age is within the configured "
                "screening range."
            )
        }


# ============================================================
# SYMPTOM ANALYSIS
# ============================================================

def analyze_battery_symptoms(symptoms):
    """
    Analyze user-provided battery symptoms.

    This does NOT provide a confirmed diagnosis.
    """

    if symptoms is None:
        symptoms = ""

    symptoms = symptoms.strip().lower()

    possible_causes = []

    if not symptoms:
        return {
            "symptoms_provided": False,
            "possible_causes": []
        }

    if (
        "heat" in symptoms
        or "hot" in symptoms
        or "heating" in symptoms
        or "temperature" in symptoms
    ):
        possible_causes.append(
            "Possible elevated temperature, charging stress, "
            "ventilation issue, aging, or excessive current."
        )

    if (
        "swelling" in symptoms
        or "bulging" in symptoms
        or "bloated" in symptoms
    ):
        possible_causes.append(
            "Physical swelling requires professional inspection."
        )

    if (
        "low backup" in symptoms
        or "backup" in symptoms
        or "short backup" in symptoms
    ):
        possible_causes.append(
            "Possible reduced capacity, high load, "
            "aging, or operating-condition issue."
        )

    if (
        "voltage drop" in symptoms
        or "voltage dropping" in symptoms
    ):
        possible_causes.append(
            "Possible high internal resistance, weak cells, "
            "low SOC, connection issue, or load-related voltage drop."
        )

    if (
        "leak" in symptoms
        or "leakage" in symptoms
    ):
        possible_causes.append(
            "Possible physical or electrolyte-related issue. "
            "Professional inspection is recommended."
        )

    if (
        "not charging" in symptoms
        or "charge problem" in symptoms
    ):
        possible_causes.append(
            "Possible charger, connection, battery, "
            "temperature, or charging-condition issue."
        )

    if (
        "corrosion" in symptoms
        or "terminal" in symptoms
    ):
        possible_causes.append(
            "Possible terminal/connection maintenance issue."
        )

    if not possible_causes:
        possible_causes.append(
            "No specific rule-based cause was identified. "
            "Further testing may be required."
        )

    return {
        "symptoms_provided": True,
        "possible_causes": possible_causes
    }


# ============================================================
# RISK ASSESSMENT
# ============================================================

def check_battery_risk(
    soh,
    temperature_c,
    soc,
    age_years,
    symptoms=""
):
    """
    Generate a preliminary battery risk assessment.

    Risk levels:

        Low
        Moderate
        High
        Critical Attention

    This is a screening model, not a certified diagnosis.
    """

    soh = _number(soh, "SOH")
    temperature_c = validate_temperature(
        temperature_c
    )
    soc = validate_soc(soc)
    age_years = _number(
        age_years,
        "Battery age"
    )

    risk_score = 0
    warnings = []

    # SOH
    if soh < 50:

        risk_score += 3

        warnings.append(
            "Battery SOH is below 50%."
        )

    elif soh < 70:

        risk_score += 2

        warnings.append(
            "Battery SOH indicates possible degradation."
        )

    elif soh < 85:

        risk_score += 1

        warnings.append(
            "Battery SOH is below the healthy threshold."
        )

    # Temperature
    if temperature_c >= 40:

        risk_score += 3

        warnings.append(
            "Battery temperature is high."
        )

    elif temperature_c >= 35:

        risk_score += 1

        warnings.append(
            "Battery temperature is elevated."
        )

    # SOC
    if soc <= 20:

        risk_score += 2

        warnings.append(
            "Battery SOC is very low."
        )

    elif soc < 40:

        risk_score += 1

        warnings.append(
            "Battery SOC is relatively low."
        )

    # Age
    if age_years >= 5:

        risk_score += 2

        warnings.append(
            "Battery age is relatively high."
        )

    elif age_years >= 3:

        risk_score += 1

        warnings.append(
            "Battery age may contribute to degradation."
        )

    # Symptoms
    symptom_result = analyze_battery_symptoms(
        symptoms
    )

    if symptom_result["symptoms_provided"]:

        risk_score += 1

        warnings.append(
            "User-reported symptoms require consideration."
        )

    # Final risk
    if risk_score >= 7:

        risk_level = "Critical Attention"

    elif risk_score >= 5:

        risk_level = "High"

    elif risk_score >= 3:

        risk_level = "Moderate"

    else:

        risk_level = "Low"

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "warnings": warnings
    }


# ============================================================
# POSSIBLE CAUSES
# ============================================================

def generate_possible_causes(
    soh,
    temperature_c,
    age_years,
    symptoms=""
):
    """
    Generate preliminary possible causes.

    These are possibilities, not confirmed faults.
    """

    soh = _number(soh, "SOH")
    temperature_c = validate_temperature(
        temperature_c
    )
    age_years = _number(
        age_years,
        "Battery age"
    )

    causes = []

    if soh < 70:
        causes.append(
            "Possible capacity degradation or battery aging."
        )

    if temperature_c >= 40:
        causes.append(
            "Possible impact of elevated operating temperature."
        )

    if age_years >= 3:
        causes.append(
            "Battery age may be contributing to degradation."
        )

    symptom_result = analyze_battery_symptoms(
        symptoms
    )

    causes.extend(
        symptom_result["possible_causes"]
    )

    if not causes:
        causes.append(
            "No major rule-based cause identified."
        )

    # Remove duplicates while preserving order
    unique_causes = []

    for cause in causes:

        if cause not in unique_causes:
            unique_causes.append(cause)

    return unique_causes


# ============================================================
# COMPLETE BATTERY ANALYSIS
# ============================================================

def analyze_battery_health(
    battery_type,
    voltage_v,
    rated_capacity_ah,
    measured_capacity_ah,
    current_a,
    temperature_c,
    age_years,
    soc,
    symptoms=""
):
    """
    Run the complete Phase 3 battery health analysis.
    """

    if not battery_type:
        battery_type = "Not specified"

    voltage_v = _number(
        voltage_v,
        "Battery voltage"
    )

    if voltage_v <= 0:
        raise ValueError(
            "Battery voltage must be greater than zero."
        )

    current_a = _number(
        current_a,
        "Battery current"
    )

    soh = calculate_battery_soh(
        rated_capacity_ah,
        measured_capacity_ah
    )

    health_label = classify_battery_health(
        soh
    )

    power_kw = calculate_battery_power(
        voltage_v,
        current_a
    )

    temperature_result = check_battery_temperature(
        temperature_c
    )

    soc_result = check_battery_soc(
        soc
    )

    age_result = check_battery_age(
        age_years
    )

    risk_result = check_battery_risk(
        soh=soh,
        temperature_c=temperature_c,
        soc=soc,
        age_years=age_years,
        symptoms=symptoms
    )

    causes = generate_possible_causes(
        soh=soh,
        temperature_c=temperature_c,
        age_years=age_years,
        symptoms=symptoms
    )

    return {
        "battery_type": battery_type,
        "voltage_v": round(voltage_v, 2),
        "rated_capacity_ah": round(
            float(rated_capacity_ah),
            2
        ),
        "measured_capacity_ah": round(
            float(measured_capacity_ah),
            2
        ),
        "capacity_health_percent": soh,
        "soh_percent": soh,
        "health_label": health_label,
        "current_a": round(current_a, 2),
        "power_kw": power_kw,
        "temperature_c": round(
            float(temperature_c),
            2
        ),
        "temperature_status": temperature_result["status"],
        "temperature_message": temperature_result["message"],
        "soc_percent": round(
            float(soc),
            2
        ),
        "soc_status": soc_result["status"],
        "soc_message": soc_result["message"],
        "age_years": round(
            float(age_years),
            2
        ),
        "age_status": age_result["status"],
        "age_message": age_result["message"],
        "risk_level": risk_result["risk_level"],
        "risk_score": risk_result["risk_score"],
        "risk_warnings": risk_result["warnings"],
        "possible_causes": causes,
        "symptoms": symptoms,
    }
