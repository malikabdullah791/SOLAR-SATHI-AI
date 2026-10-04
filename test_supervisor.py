from agents.supervisor_agent import run_supervisor_agent


result = run_supervisor_agent(
    solar_kw=3.2,
    load_kw=2.8,
    grid_available=True,

    battery_type="Lead Acid",
    battery_voltage=48,
    rated_capacity_ah=200,
    measured_capacity_ah=180,
    battery_current=10,
    temperature_c=30,
    battery_age=2,
    battery_soc=65,
    symptoms="No visible abnormal symptoms",

    essential_load_kw=2.0,
    non_essential_load_kw=0.5,
    peak_load_kw=4.0,

    grid_tariff=50,
)


print("\n==============================")
print("SUPERVISOR RESULT")
print("==============================")

print("Success:")
print(result["success"])

print("\nWorkflow:")

for step in result["workflow"]:
    print("✓", step)

print("\nPriority:")
print(
    result["final_recommendation"]["priority"]
)

print("\nRecommendations:")

for item in result["final_recommendation"][
    "recommendations"
]:
    print("-", item)

print("\nWarnings:")

for item in result["final_recommendation"][
    "warnings"
]:
    print("-", item)
