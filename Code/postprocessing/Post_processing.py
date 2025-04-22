import pandas as pd
import glob
import os
import ast
import matplotlib.pyplot as plt

def get_valid_year():
    while True:
        try:
            year = input("Enter year (2015–2021 or 'q' to quit): ")
            if year.lower() == 'q':
                return None
            year = int(year)
            if 2015 <= year <= 2021:
                return str(year)
            print("Error: Year must be between 2015 and 2021.")
        except ValueError:
            print("Error: Please enter a valid integer.")

def get_valid_month():
    valid_months = ['03', '06', '09', '12']
    while True:
        month = input("Enter month (03, 06, 09, or 12, or 'q' to quit): ")
        if month.lower() == 'q':
            return None
        if month in valid_months:
            return month
        print("Error: Month must be 03, 06, 09, or 12.")

def load_csv(mode):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dfs = []

    if mode == 1:
        year = get_valid_year()
        if not year:
            return None, None
        pattern = os.path.join(script_dir, f"{year}*.csv")
    elif mode == 2:
        month = get_valid_month()
        if not month:
            return None, None
        pattern = os.path.join(script_dir, f"*{month}.csv")
    elif mode == 3:
        year = get_valid_year()
        if not year:
            return None, None
        month = get_valid_month()
        if not month:
            return None, None
        pattern = os.path.join(script_dir, f"{year}{month}.csv")

    files = sorted(glob.glob(pattern))
    if not files:
        print("No matching files found.")
        return None, None

    for file in files:
        try:
            df = pd.read_csv(file)
            dfs.append(df)
            print(f"Loaded: {os.path.basename(file)}")
        except Exception as e:
            print(f"Error loading {file}: {e}")

    if not dfs:
        return None, None

    df = pd.concat(dfs, ignore_index=True)

    # Clean and process the data
    df['Start-Date'] = pd.to_datetime(df['Start-Date'], errors='coerce')
    df['End-date'] = pd.to_datetime(df['End-date'], errors='coerce')

    if 'Dep(start-coordinates)' in df.columns:
        df['Dep(start-coordinates)'] = df['Dep(start-coordinates)'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [None, None])
    if 'Arr(end-coordinates)' in df.columns:
        df['Arr(end-coordinates)'] = df['Arr(end-coordinates)'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [None, None])

    df.fillna("Unknown", inplace=True)

    return df, year if mode == 1 else month

def summarize_flights(df):
    if 'CO2' in df.columns and 'NOX' in df.columns:
        df['CO2'] = pd.to_numeric(df['CO2'], errors='coerce')
        df['NOX'] = pd.to_numeric(df['NOX'], errors='coerce')

        num_flights = len(df)
        total_co2 = df['CO2'].sum()
        total_nox = df['NOX'].sum()

        print("\n=== Summary ===")
        print(f"Number of flights: {num_flights}")
        print(f"Total CO2 emissions: {total_co2:.2f} kg")
        print(f"Total NOX emissions: {total_nox:.2f} kg")
    else:
        print("Missing 'CO2' or 'NOX' column in the data.")

def group_by_aircraft_and_route(df):
    print("\n=== Emissions by Aircraft Type ===")
    by_plane = df.groupby('Plane')[['CO2', 'NOX']].sum().sort_values(by='CO2', ascending=False)
    print(by_plane)

    print("\n=== Emissions by Route (Dep → Arr) ===")
    df['Route'] = df['Dep'] + " → " + df['Arr']
    by_route = df.groupby('Route')[['CO2', 'NOX']].sum().sort_values(by='CO2', ascending=False)
    print(by_route.head(10))  # print top 10 routes

def plot_emissions(df, mode, label):
    if mode == 1:
        df['Month'] = df['Start-Date'].dt.strftime('%b')
        monthly = df.groupby('Month')[['CO2']].sum()
        monthly = monthly.reindex(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        monthly.plot(kind='bar', legend=False)
        plt.title(f"Monthly CO2 Emissions in {label}")
        plt.ylabel("CO2 (kg)")
        plt.tight_layout()
        plt.show()
    elif mode == 2:
        df['Route'] = df['Dep'] + " → " + df['Arr']
        route_emissions = df.groupby('Route')[['CO2']].sum().sort_values(by='CO2', ascending=False).head(10)
        route_emissions.plot(kind='bar', legend=False)
        plt.title(f"Top 10 Emission Routes in Month {label}")
        plt.ylabel("CO2 (kg)")
        plt.tight_layout()
        plt.show()

def main():
    print("=== CSV Loading Modes ===")
    print("1. Load all data for a specific year")
    print("2. Load all data for a specific month")
    print("3. Load data for a specific year+month")

    while True:
        try:
            mode = int(input("Choose mode (1–3): "))
            if mode in {1, 2, 3}:
                break
            print("Error: Mode must be 1, 2, or 3.")
        except ValueError:
            print("Error: Please enter a valid integer.")

    df, label = load_csv(mode)
    if df is not None:
        print("\nLoaded data preview:")
        print(df.head())

        summarize_flights(df)
        group_by_aircraft_and_route(df)

        if mode in {1, 2}:
            plot_emissions(df, mode, label)

if __name__ == "__main__":
    main()
