import pandas as pd
import numpy as np
from collections import defaultdict


# Load data
def load_data():
    demand_df = pd.read_csv('demand.csv')
    vehicles_df = pd.read_csv('vehicles.csv')
    vehicles_fuels_df = pd.read_csv('vehicles_fuels.csv')
    fuels_df = pd.read_csv('fuels.csv')
    carbon_emissions_df = pd.read_csv('carbon_emissions.csv')


def preprocess_data():
    # Data cleaning and validation
    def validate_data(df, name):
        print(f"Validating {name}:")
        print(f"Shape: {df.shape}")
        print(f"Missing values:\n{df.isnull().sum()}")
        print(f"Data types:\n{df.dtypes}\n")

    validate_data(demand_df, "Demand")
    validate_data(vehicles_df, "Vehicles")
    validate_data(vehicles_fuels_df, "Vehicles Fuels")
    validate_data(fuels_df, "Fuels")
    validate_data(carbon_emissions_df, "Carbon Emissions")

    # Create lookup dictionaries
    vehicles_dict = vehicles_df.set_index('ID').to_dict('index')
    fuels_dict = fuels_df.set_index(['Fuel', 'Year']).to_dict('index')

    # Organize demand data
    demand_dict = demand_df.set_index(['Year', 'Size', 'Distance']).to_dict()['Demand (km)']

    # Structure carbon emission limits
    carbon_limits = carbon_emissions_df.set_index('Year')['Carbon emission CO2/kg'].to_dict()

    # Example of calculating derived values (this would need to be expanded)
    def calculate_costs(vehicle_cost, years=10):
        insurance_rates = [0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14]
        maintenance_rates = [0.01, 0.03, 0.05, 0.07, 0.09, 0.11, 0.13, 0.15, 0.17, 0.19]
        resale_values = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.3, 0.3, 0.3]

        insurance_costs = [vehicle_cost * rate for rate in insurance_rates]
        maintenance_costs = [vehicle_cost * rate for rate in maintenance_rates]
        resale_values = [vehicle_cost * rate for rate in resale_values]

        return insurance_costs, maintenance_costs, resale_values

    # Organize vehicle data
    vehicles_dict = {}
    for _, vehicle in vehicles_df.iterrows():
        vehicle_id = vehicle['ID']
        vehicle_cost = vehicle['Cost ($)']
        insurance_costs, maintenance_costs, resale_values = calculate_costs(vehicle_cost)

        vehicles_dict[vehicle_id] = {
            'type': vehicle['Vehicle'],
            'size': vehicle['Size'],
            'year': vehicle['Year'],
            'cost': vehicle_cost,
            'yearly_range': vehicle['Yearly range (km)'],
            'distance_bucket': vehicle['Distance'],
            'insurance_costs': insurance_costs,
            'maintenance_costs': maintenance_costs,
            'resale_values': resale_values
        }

    # Organize fuel consumption data
    fuel_consumption = defaultdict(dict)
    for _, row in vehicles_fuels_df.iterrows():
        fuel_consumption[row['ID']][row['Fuel']] = row['Consumption (unit_fuel/km)']

    # Add fuel consumption to vehicles_dict
    for vehicle_id, fuel_data in fuel_consumption.items():
        vehicles_dict[vehicle_id]['fuel_consumption'] = fuel_data

    # Organize fuel data
    fuels_dict = defaultdict(lambda: defaultdict(dict))
    for _, fuel in fuels_df.iterrows():
        fuels_dict[fuel['Fuel']][fuel['Year']] = {
            'emissions': fuel['Emissions (CO2/unit_fuel)'],
            'cost': fuel['Cost ($/unit_fuel)'],
            'cost_uncertainty': fuel['Cost Uncertainty (±%)']
        }

    # Organize demand data
    demand_dict = defaultdict(lambda: defaultdict(dict))
    for _, demand in demand_df.iterrows():
        demand_dict[demand['Year']][demand['Size']][demand['Distance']] = demand['Demand (km)']

    # Organize carbon emission limits
    carbon_limits = carbon_emissions_df.set_index('Year')['Carbon emission CO2/kg'].to_dict()

    # Create size and distance bucket mappings
    size_buckets = {'S1': '17 tons', 'S2': '44 tons', 'S3': '50 tons', 'S4': '64 tons'}
    distance_buckets = {'D1': 300, 'D2': 400, 'D3': 500, 'D4': 600}

    # Create a mapping of which distance buckets each vehicle can satisfy
    distance_satisfaction = {
        'D1': ['D1', 'D2', 'D3', 'D4'],
        'D2': ['D2', 'D3', 'D4'],
        'D3': ['D3', 'D4'],
        'D4': ['D4']
    }

    # Precompute fuel costs and emissions for each vehicle-fuel combination
    for vehicle_id, vehicle_data in vehicles_dict.items():
        vehicle_data['yearly_fuel_costs'] = defaultdict(dict)
        vehicle_data['yearly_emissions'] = defaultdict(dict)

        for fuel, consumption in vehicle_data['fuel_consumption'].items():
            for year in range(2023, 2039):
                if year in fuels_dict[fuel]:
                    fuel_cost = fuels_dict[fuel][year]['cost']
                    fuel_emissions = fuels_dict[fuel][year]['emissions']

                    yearly_distance = vehicle_data['yearly_range']
                    yearly_fuel_cost = yearly_distance * consumption * fuel_cost
                    yearly_emissions = yearly_distance * consumption * fuel_emissions

                    vehicle_data['yearly_fuel_costs'][fuel][year] = yearly_fuel_cost
                    vehicle_data['yearly_emissions'][fuel][year] = yearly_emissions

    # Print sample of processed data
    print("Sample of processed vehicle data:")
    print(list(vehicles_dict.items())[0])
    print("\nSample of demand data:")
    print(list(demand_dict.items())[0])
    print("\nSample of fuel data:")
    print(list(fuels_dict.items())[0])
    print("\nCarbon emission limits:")
    print(carbon_limits)
    print("\nSize buckets:")
    print(size_buckets)
    print("\nDistance buckets:")
    print(distance_buckets)
    print("\nDistance satisfaction mapping:")
    print(distance_satisfaction)

    # Prepare data structures for optimization
    years = list(range(2023, 2039))
    vehicle_ids = list(vehicles_dict.keys())
    size_buckets = list(size_buckets.keys())
    distance_buckets = list(distance_buckets.keys())
    fuel_types = list(fuels_dict.keys())

    print("\nPrepared data structures for optimization:")
    print(f"Years: {years}")
    print(f"Number of vehicle types: {len(vehicle_ids)}")
    print(f"Size buckets: {size_buckets}")
    print(f"Distance buckets: {distance_buckets}")
    print(f"Fuel types: {fuel_types}")
