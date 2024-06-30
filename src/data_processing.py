import pandas as pd
import numpy as np
from collections import defaultdict


def preprocess_data(data_dict):
    """
    Process the raw data and structure it for the optimization model.

    :param data_dict: Dictionary containing raw dataframes
    :return: Dictionary containing processed data structures
    """

    # Extract dataframes from the input dictionary
    demand_df = data_dict['Demand']
    vehicles_df = data_dict['Vehicles']
    vehicles_fuels_df = data_dict['Vehicles_fuels']
    fuels_df = data_dict['Fuels']
    carbon_emissions_df = data_dict['Carbon_emissions']

    # Helper function for cost calculations
    def calculate_costs(vehicle_cost, years=10):
        insurance_rates = [0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14]
        maintenance_rates = [0.01, 0.03, 0.05, 0.07, 0.09, 0.11, 0.13, 0.15, 0.17, 0.19]
        resale_values = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.3, 0.3, 0.3]

        insurance_costs = [vehicle_cost * rate for rate in insurance_rates]
        maintenance_costs = [vehicle_cost * rate for rate in maintenance_rates]
        resale_values = [vehicle_cost * rate for rate in resale_values]

        return insurance_costs, maintenance_costs, resale_values

    # Process vehicle data
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

    # Process fuel consumption data
    fuel_consumption = defaultdict(dict)
    for _, row in vehicles_fuels_df.iterrows():
        fuel_consumption[row['ID']][row['Fuel']] = row['Consumption (unit_fuel/km)']

    # Add fuel consumption to vehicles_dict
    for vehicle_id, fuel_data in fuel_consumption.items():
        vehicles_dict[vehicle_id]['fuel_consumption'] = fuel_data

    # Process fuel data
    fuels_dict = defaultdict(lambda: defaultdict(dict))
    for _, fuel in fuels_df.iterrows():
        fuels_dict[fuel['Fuel']][fuel['Year']] = {
            'emissions': fuel['Emissions (CO2/unit_fuel)'],
            'cost': fuel['Cost ($/unit_fuel)'],
            'cost_uncertainty': fuel['Cost Uncertainty (±%)']
        }

    # Process demand data
    demand_dict = defaultdict(lambda: defaultdict(dict))
    for _, demand in demand_df.iterrows():
        demand_dict[demand['Year']][demand['Size']][demand['Distance']] = demand['Demand']

    # Process carbon emission limits
    carbon_limits = carbon_emissions_df.set_index('Year')['Total Carbon emission limit'].to_dict()

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

    # Prepare data structures for optimization
    years = list(range(2023, 2039))
    vehicle_ids = list(vehicles_dict.keys())
    size_buckets_list = list(size_buckets.keys())
    distance_buckets_list = list(distance_buckets.keys())
    fuel_types = list(fuels_dict.keys())

    # Return processed data
    return {
        'vehicles_dict': vehicles_dict,
        'fuels_dict': fuels_dict,
        'demand_dict': demand_dict,
        'carbon_limits': carbon_limits,
        'size_buckets': size_buckets,
        'distance_buckets': distance_buckets,
        'distance_satisfaction': distance_satisfaction,
        'years': years,
        'vehicle_ids': vehicle_ids,
        'size_buckets_list': size_buckets_list,
        'distance_buckets_list': distance_buckets_list,
        'fuel_types': fuel_types
    }


# If you want to test this function independently, you can add:
if __name__ == "__main__":
    from load_data import load_data  # Assuming you have this function in a separate file

    raw_data = load_data()
    processed_data = preprocess_data(raw_data)
    print("Processed data keys:", processed_data.keys())
    # You can add more print statements here to inspect the processed data