import pandas as pd


#Load data from CSV files
def load_data():
    vehicles = pd.read_csv('./Dataset/vehicles.csv')
    carbon_emissions = pd.read_csv('./Dataset/carbon_emissions.csv')
    cost_profiles = pd.read_csv('./Dataset/cost_profiles.csv')
    demand = pd.read_csv('./Dataset/demand.csv')
    fuels = pd.read_csv('./Dataset/fuels.csv')
    vehicles_fuels = pd.read_csv('./Dataset/vehicles_fuels.csv')

    return vehicles, carbon_emissions, cost_profiles, demand, fuels, vehicles_fuels


#Test Loading data
if __name__ == '__main__':
    vehicles, carbon_emissions, cost_profiles, demand, fuels, vehicles_fuels = load_data()
    print(demand.head())
    print(vehicles.head())
    print(vehicles_fuels.head())
    print(fuels.head())
    print(carbon_emissions.head())
