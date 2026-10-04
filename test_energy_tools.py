from tools.energy_tools import (
    calculate_solar_surplus,
    calculate_solar_deficit,
    calculate_energy_flow,
    calculate_backup_time,
    calculate_energy_cost,
    check_energy_balance,
)


print("=== Solar Surplus Test ===")

surplus = calculate_solar_surplus(
    solar_kw=5,
    load_kw=3,
)

print("Solar surplus:", surplus, "kW")


print("\n=== Solar Deficit Test ===")

deficit = calculate_solar_deficit(
    solar_kw=2,
    load_kw=4,
)

print("Solar deficit:", deficit, "kW")


print("\n=== Energy Flow Test ===")

flow = calculate_energy_flow(
    solar_kw=5,
    load_kw=3,
    battery_soc=60,
    grid_available=True,
)

for key, value in flow.items():
    print(f"{key}: {value}")


print("\n=== Backup Time Test ===")

backup = calculate_backup_time(
    battery_capacity_kwh=10,
    battery_soc=60,
    load_kw=3,
)

print("Estimated backup:", backup, "hours")


print("\n=== Energy Cost Test ===")

cost = calculate_energy_cost(
    energy_kwh=10,
    tariff_per_kwh=45,
)

print("Energy cost:", cost)


print("\n=== Energy Balance Test ===")

balance = check_energy_balance(
    solar_to_load_kw=3,
    battery_to_load_kw=0,
    grid_to_load_kw=0,
    load_kw=3,
)

print(balance)


print("\nAll tests completed.")
