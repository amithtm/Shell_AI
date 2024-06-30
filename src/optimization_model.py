from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus

def create_optimization_model(demand, vehicles, vehicles_fuels, fuels, carbon_emissions):
    # Define the problem
    problem = LpProblem("Fleet_Optimization", LpMinimize)

    # Define decision variables
    years = range(2023, 2039)
    vehicle_models = vehicles['Model'].unique()
    fuel_types = fuels['Fuel_Type'].unique()

    # Number of vehicles purchased each year
    N_v_yr = LpVariable.dicts("N_v_yr", [(v, yr) for v in vehicle_models for yr in years], 0, None, LpBinary)

    # Number of vehicles operating each year
    N_v_yrp = LpVariable.dicts("N_v_yrp", [(v, yr, yrp) for v in vehicle_models for yr in years for yrp in years if yrp <= yr], 0, None, LpBinary)

    # Fuel consumption
    m_v_f = vehicles_fuels.set_index(['Model', 'Fuel_Type']).to_dict()['Consumption']

    # Define costs (placeholders, replace with actual data)
    C_buy = ...
    C_ins = ...
    C_mnt = ...
    C_fuel = ...
    C_sell = ...
    budget = ...

    # Objective function
    problem += lpSum(C_buy[v, yr] * N_v_yr[v, yr] for v in vehicle_models for yr in years) \
               + lpSum(C_ins[v, yr] * N_v_yrp[v, yr, yrp] for v in vehicle_models for yr in years for yrp in years if yrp <= yr) \
               + lpSum(C_mnt[v, yr] * N_v_yrp[v, yr, yrp] for v in vehicle_models for yr in years for yrp in years if yrp <= yr) \
               + lpSum(C_fuel[v, f, yr] * N_v_yrp[v, yr, yrp] * m_v_f[v, f] for v in vehicle_models for f in fuel_types for yr in years for yrp in years if yrp <= yr) \
               - lpSum(C_sell[v, yr] * N_v_yr[v, yr] for v in vehicle_models for yr in years)

    # Constraints
    # Demand satisfaction
    for size in demand['Size'].unique():
        for bucket in demand['Distance_Bucket'].unique():
            for yr in years:
                problem += lpSum(N_v_yrp[v, yr, yrp] for v in vehicle_models for yrp in years if yrp <= yr) >= demand.loc[(demand['Size'] == size) & (demand['Distance_Bucket'] == bucket) & (demand['Year'] == yr), 'Demand'].values[0]

    # Carbon emission limits
    for yr in years:
        problem += lpSum(N_v_yrp[v, yr, yrp] * m_v_f[v, f] * carbon_emissions.loc[carbon_emissions['Fuel_Type'] == f, 'Emission_Rate'].values[0] for v in vehicle_models for f in fuel_types for yrp in years if yrp <= yr) <= carbon_emissions.loc[carbon_emissions['Year'] == yr, 'Carbon_Limit'].values[0]

    # Yearly budget constraints
    for yr in years:
        problem += lpSum(C_buy[v, yr] * N_v_yr[v, yr] for v in vehicle_models) \
                  + lpSum(C_ins[v, yr] * N_v_yrp[v, yr, yrp] for v in vehicle_models for yrp in years if yrp <= yr) \
                  + lpSum(C_mnt[v, yr] * N_v_yrp[v, yr, yrp] for v in vehicle_models for yrp in years if yrp <= yr) \
                  + lpSum(C_fuel[v, f, yr] * N_v_yrp[v, yr, yrp] * m_v_f[v, f] for v in vehicle_models for f in fuel_types for yrp in years if yrp <= yr) \
                  - lpSum(C_sell[v, yr] * N_v_yr[v, yr] for v in vehicle_models) <= budget.loc[budget['Year'] == yr, 'Budget'].values[0]

    # Vehicle operation constraints
    for v in vehicle_models:
        for yr in years:
            problem += lpSum(N_v_yrp[v, yr, yrp] for yrp in years if yrp <= yr) <= lpSum(N_v_yr[v, yrp] for yrp in years if yrp <= yr)

    return problem

if __name__ == "__main__":
    # Test model creation with dummy data
    demand, vehicles, vehicles_fuels, fuels, carbon_emissions = load_data()
    problem = create_optimization_model(demand, vehicles, vehicles_fuels, fuels, carbon_emissions)
    problem.solve()
    print("Status:", LpStatus[problem.status])
    for v in problem.variables():
        if v.varValue > 0:
            print(v.name, "=", v.varValue)
3. main.py - Main script to run the optimization
Create a file main.py in the root directory to run the entire process.

python
Copy code
# main.py

from src.load_data import load_data
from src.optimization_model import create_optimization_model
from pulp import LpStatus

if __name__ == "__main__":
    # Load data
    demand, vehicles, vehicles_fuels, fuels, carbon_emissions = load_data()

    # Create optimization model
    problem = create_optimization_model(demand, vehicles, vehicles_fuels, fuels, carbon_emissions)

    # Solve the problem
    problem.solve()

    # Print the status
    print("Status:", LpStatus[problem.status])

    # Print the results
    for v in problem.variables():
        if v.varValue > 0:
            print(v.name, "=", v.varValue)