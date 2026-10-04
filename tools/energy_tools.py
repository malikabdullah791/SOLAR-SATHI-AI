"""
SolarSathi AI - Energy Calculation Tools

This module contains deterministic energy calculations.
The calculations are simulation/decision-support calculations only.
They do not directly control any electrical equipment.
"""


def _validate_non_negative(value, name):
    """Validate that a numerical value is not negative."""
    if value is None:
        raise ValueError(f"{name} cannot be empty.")

    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a number.")

    if value < 0:
        raise ValueError(f"{name} cannot be negative.")

    return value


def _validate_soc(soc):
    """Validate battery state of charge."""
    try:
        soc = float(soc)
    except (TypeError, ValueError):
        raise ValueError("Battery SOC must be a number.")

    if soc < 0 or soc > 100:
        raise ValueError("Battery SOC must be between 0 and 100%.")

    return soc


def calculate_solar_surplus(solar_kw, load_kw):
    """
    Calculate excess solar power after supplying the load.

    Example:
    Solar = 5 kW
    Load = 3 kW
    Surplus = 2 kW
    """
    solar_kw = _validate_non_negative(solar_kw, "Solar power")
    load_kw = _validate_non_negative(load_kw, "Load power")

    return max(solar_kw - load_kw, 0.0)


def calculate_solar_deficit(solar_kw, load_kw):
    """
    Calculate load demand that solar cannot cover.

    Example:
    Solar = 2 kW
    Load = 5 kW
    Deficit = 3 kW
    """
    solar_kw = _validate_non_negative(solar_kw, "Solar power")
    load_kw = _validate_non_negative(load_kw, "Load power")

    return max(load_kw - solar_kw, 0.0)


def calculate_grid_import(
    load_kw,
    solar_kw,
    battery_to_load_kw=0.0
):
    """
    Calculate grid power required after solar and battery contribution.
    """
    load_kw = _validate_non_negative(load_kw, "Load power")
    solar_kw = _validate_non_negative(solar_kw, "Solar power")
    battery_to_load_kw = _validate_non_negative(
        battery_to_load_kw,
        "Battery discharge power"
    )

    remaining_load = max(
        load_kw - solar_kw - battery_to_load_kw,
        0.0
    )

    return remaining_load


def calculate_grid_export(solar_kw, load_kw, battery_charge_kw=0.0):
    """
    Calculate solar power that can potentially be exported
    after serving load and battery charging.
    """
    solar_kw = _validate_non_negative(solar_kw, "Solar power")
    load_kw = _validate_non_negative(load_kw, "Load power")
    battery_charge_kw = _validate_non_negative(
        battery_charge_kw,
        "Battery charging power"
    )

    export_power = max(
        solar_kw - load_kw - battery_charge_kw,
        0.0
    )

    return export_power


def calculate_energy_flow(
    solar_kw,
    load_kw,
    battery_soc,
    grid_available=True,
    min_battery_soc=20.0,
    max_battery_charge_kw=5.0,
    max_battery_discharge_kw=5.0
):
    """
    Calculate a simplified energy flow.

    Priority:

    1. Solar supplies load.
    2. Solar surplus charges battery.
    3. Remaining solar surplus may be exported.
    4. Battery supplies remaining load.
    5. Grid supplies remaining load.
    6. If grid is unavailable, remaining load becomes unserved.

    This is a simplified simulation model.
    It is NOT real inverter control logic.
    """

    solar_kw = _validate_non_negative(solar_kw, "Solar power")
    load_kw = _validate_non_negative(load_kw, "Load power")
    battery_soc = _validate_soc(battery_soc)

    if min_battery_soc < 0 or min_battery_soc > 100:
        raise ValueError("Minimum battery SOC must be between 0 and 100%.")

    max_battery_charge_kw = _validate_non_negative(
        max_battery_charge_kw,
        "Maximum battery charging power"
    )

    max_battery_discharge_kw = _validate_non_negative(
        max_battery_discharge_kw,
        "Maximum battery discharge power"
    )

    # ---------------------------------------------------------
    # STEP 1: Solar supplies the load
    # ---------------------------------------------------------

    solar_to_load_kw = min(solar_kw, load_kw)

    remaining_load_kw = max(
        load_kw - solar_to_load_kw,
        0.0
    )

    solar_surplus_kw = max(
        solar_kw - solar_to_load_kw,
        0.0
    )

    # ---------------------------------------------------------
    # STEP 2: Charge battery from solar surplus
    # ---------------------------------------------------------

    solar_to_battery_kw = 0.0

    if solar_surplus_kw > 0 and battery_soc < 100:
        solar_to_battery_kw = min(
            solar_surplus_kw,
            max_battery_charge_kw
        )

    remaining_solar_surplus_kw = max(
        solar_surplus_kw - solar_to_battery_kw,
        0.0
    )

    # ---------------------------------------------------------
    # STEP 3: Export remaining solar
    # ---------------------------------------------------------

    solar_export_kw = remaining_solar_surplus_kw

    # ---------------------------------------------------------
    # STEP 4: Battery supplies remaining load
    # ---------------------------------------------------------

    battery_to_load_kw = 0.0

    if (
        remaining_load_kw > 0
        and battery_soc > min_battery_soc
    ):
        battery_to_load_kw = min(
            remaining_load_kw,
            max_battery_discharge_kw
        )

    remaining_load_after_battery = max(
        remaining_load_kw - battery_to_load_kw,
        0.0
    )

    # ---------------------------------------------------------
    # STEP 5: Grid supplies remaining load
    # ---------------------------------------------------------

    grid_to_load_kw = 0.0

    if grid_available:
        grid_to_load_kw = remaining_load_after_battery

    # ---------------------------------------------------------
    # STEP 6: Unserved load
    # ---------------------------------------------------------

    unserved_load_kw = max(
        remaining_load_after_battery - grid_to_load_kw,
        0.0
    )

    # ---------------------------------------------------------
    # Energy balance
    # ---------------------------------------------------------

    total_supply_kw = (
        solar_to_load_kw
        + battery_to_load_kw
        + grid_to_load_kw
    )

    total_demand_kw = load_kw

    balance_error_kw = total_supply_kw - total_demand_kw

    return {
        "solar_to_load_kw": round(solar_to_load_kw, 3),
        "solar_to_battery_kw": round(solar_to_battery_kw, 3),
        "battery_to_load_kw": round(battery_to_load_kw, 3),
        "grid_to_load_kw": round(grid_to_load_kw, 3),
        "solar_export_kw": round(solar_export_kw, 3),
        "unserved_load_kw": round(unserved_load_kw, 3),
        "solar_surplus_kw": round(solar_surplus_kw, 3),
        "solar_deficit_kw": round(
            max(load_kw - solar_kw, 0.0),
            3
        ),
        "total_supply_kw": round(total_supply_kw, 3),
        "total_demand_kw": round(total_demand_kw, 3),
        "balance_error_kw": round(balance_error_kw, 3),
    }


def calculate_backup_time(
    battery_capacity_kwh,
    battery_soc,
    load_kw,
    min_soc=20.0,
    usable_fraction=0.90
):
    """
    Estimate battery backup time.

    This is a simplified estimate.

    Example:
    Battery = 10 kWh
    SOC = 60%
    Minimum SOC = 20%
    Load = 3 kW
    """

    battery_capacity_kwh = _validate_non_negative(
        battery_capacity_kwh,
        "Battery capacity"
    )

    battery_soc = _validate_soc(battery_soc)

    load_kw = _validate_non_negative(
        load_kw,
        "Load power"
    )

    if min_soc < 0 or min_soc > 100:
        raise ValueError(
            "Minimum SOC must be between 0 and 100%."
        )

    if usable_fraction <= 0 or usable_fraction > 1:
        raise ValueError(
            "Usable fraction must be greater than 0 and <= 1."
        )

    if load_kw == 0:
        return float("inf")

    if battery_soc <= min_soc:
        return 0.0

    usable_soc_fraction = (
        battery_soc - min_soc
    ) / 100

    usable_energy_kwh = (
        battery_capacity_kwh
        * usable_soc_fraction
        * usable_fraction
    )

    backup_hours = usable_energy_kwh / load_kw

    return round(backup_hours, 2)


def calculate_energy_from_power(power_kw, hours):
    """
    Convert power to energy.

    Energy = Power × Time
    """

    power_kw = _validate_non_negative(
        power_kw,
        "Power"
    )

    hours = _validate_non_negative(
        hours,
        "Hours"
    )

    return round(power_kw * hours, 3)


def calculate_daily_energy(power_kw, hours_per_day):
    """
    Calculate daily energy consumption/generation.
    """

    return calculate_energy_from_power(
        power_kw,
        hours_per_day
    )


def calculate_energy_cost(
    energy_kwh,
    tariff_rs_per_kwh
):
    """
    Calculate electricity cost in Pakistani Rupees.
    """

    energy_kwh = _validate_non_negative(
        energy_kwh,
        "Energy"
    )

    tariff_rs_per_kwh = _validate_non_negative(
        tariff_rs_per_kwh,
        "Tariff"
    )

    return round(
        energy_kwh * tariff_rs_per_kwh,
        2
    )


def check_energy_balance(
    supply_kw,
    demand_kw,
    tolerance_kw=0.01
):
    """
    Check whether energy supply approximately equals demand.
    """

    supply_kw = _validate_non_negative(
        supply_kw,
        "Supply"
    )

    demand_kw = _validate_non_negative(
        demand_kw,
        "Demand"
    )

    difference = abs(
        supply_kw - demand_kw
    )

    return {
        "balanced": difference <= tolerance_kw,
        "difference_kw": round(difference, 4),
        "tolerance_kw": tolerance_kw
    }


def create_energy_summary(
    solar_kw,
    load_kw,
    battery_soc,
    grid_available,
    battery_capacity_kwh=10.0,
    grid_tariff=50.0
):
    """
    Create a complete energy summary for the dashboard.
    """

    flow = calculate_energy_flow(
        solar_kw=solar_kw,
        load_kw=load_kw,
        battery_soc=battery_soc,
        grid_available=grid_available
    )

    backup_time = calculate_backup_time(
        battery_capacity_kwh=battery_capacity_kwh,
        battery_soc=battery_soc,
        load_kw=load_kw
    )

    energy_cost = calculate_energy_cost(
        energy_kwh=load_kw,
        tariff_rs_per_kwh=grid_tariff
    )

    balance = check_energy_balance(
        supply_kw=flow["total_supply_kw"],
        demand_kw=flow["total_demand_kw"]
    )

    return {
        "flow": flow,
        "backup_time_hours": backup_time,
        "estimated_load_cost_rs": energy_cost,
        "energy_balance": balance
    }
