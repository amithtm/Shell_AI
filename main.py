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