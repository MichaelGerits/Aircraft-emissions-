import pandas as pd
import glob
import os
import ast
import matplotlib.pyplot as plt
import plotly.express as px

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
    df['Start-Date'] = pd.to_datetime(df['Start-Date'], errors='coerce', dayfirst=True)
    df['End-date'] = pd.to_datetime(df['End-date'], errors='coerce', dayfirst=True)

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
        import matplotlib.pyplot as plt
        from mpl_toolkits.basemap import Basemap

        # --- Monthly Emissions Scatter Plot ---
        df['Month'] = df['Start-Date'].dt.month
        monthly = df.groupby('Month')[['CO2', 'NOX']].sum().reindex(range(1, 13))
        monthly.index = monthly.index.map(lambda x: pd.to_datetime(str(x), format='%m').strftime('%b'))

        plt.figure(figsize=(10, 5))
        plt.plot(monthly.index, monthly['CO2'], marker='o', label='CO2 (kg)', color='skyblue')
        plt.plot(monthly.index, monthly['NOX'], marker='o', label='NOX (kg)', color='orange')
        plt.title(f"Monthly Emissions in {label}")
        plt.ylabel("Emissions (kg)")
        plt.xlabel("Month")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # --- Top & Bottom 10 CO2 and NOX Routes ---
        df['Route'] = df['Dep'] + " → " + df['Arr']
        route_emissions = df.groupby('Route')[['CO2', 'NOX']].sum()
        route_emissions_nonzero = route_emissions[(route_emissions['CO2'] > 0) & (route_emissions['NOX'] > 0)]

        def plot_bar(data, title, color):
            data.plot(kind='bar', color=color, figsize=(10, 5))
            plt.title(title)
            plt.ylabel("Emissions (kg)")
            plt.xlabel("Route")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()

        plot_bar(route_emissions.sort_values(by='CO2', ascending=False).head(10),
                 f"Top 10 Routes by CO2 in {label}", 'red')

        plot_bar(route_emissions_nonzero.sort_values(by='CO2').head(10),
                 f"Bottom 10 Routes by CO2 (Non-zero) in {label}", 'green')

        plot_bar(route_emissions.sort_values(by='NOX', ascending=False).head(10),
                 f"Top 10 Routes by NOX in {label}", 'darkorange')

        plot_bar(route_emissions_nonzero.sort_values(by='NOX').head(10),
                 f"Bottom 10 Routes by NOX (Non-zero) in {label}", 'blue')

        # --- Emissions by Flight Type using 'Haul' column ---
        if 'Haul' in df.columns:
            haul_emissions = df.groupby('Haul')[['CO2', 'NOX']].sum()
            print("\n=== Total Emissions by Flight Type ===")
            print(haul_emissions)

            haul_emissions.plot(kind='bar', color=['skyblue', 'orange'], figsize=(8, 5))
            plt.title(f"Total Emissions by Flight Type in {label}")
            plt.ylabel("Emissions (kg)")
            plt.xlabel("Flight Type")
            plt.xticks(rotation=0)
            plt.tight_layout()
            plt.show()
        else:
            print("Column 'Haul' not found — skipping flight type analysis.")

        # --- Emissions by Departure Airport ---
        if 'Dep' in df.columns:
            airport_emissions = df.groupby('Dep')[['CO2', 'NOX']].sum()
            top_airports = airport_emissions.sort_values(by='CO2', ascending=False).head(15)

            top_airports.plot(kind='barh', figsize=(10, 6), color=['skyblue', 'orange'])
            plt.title(f"Top 15 Departure Airports by Emissions in {label}")
            plt.xlabel("Emissions (kg)")
            plt.ylabel("Airport of Origin")
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.show()
        else:
            print("Column 'Dep' not found — cannot calculate emissions by origin airport.")

        def plot_top_airport_map(df, label):
    # Group and sort emissions by departure airport

    # Convert coordinates to string so they can be grouped
            df['DepCoordsStr'] = df['Dep(start-coordinates)'].apply(lambda x: str(x) if isinstance(x, list) else None)

    # Group and sort emissions by departure airport and coordinate string
            coords_group = df.groupby(['Dep', 'DepCoordsStr'])['CO2'].sum().reset_index()
            coords_group = coords_group.sort_values(by='CO2', ascending=False).head(15)

    # Convert string coordinates back to lists
            coords_group['Dep(start-coordinates)'] = coords_group['DepCoordsStr'].apply(ast.literal_eval)

    # Filter valid coordinates
            coords_group = coords_group[coords_group['Dep(start-coordinates)'].apply(
                lambda x: isinstance(x, list) and len(x) == 2 and None not in x)]

    # Extract lat/lon
            coords_group['lon'] = coords_group['Dep(start-coordinates)'].apply(lambda x: x[0])
            coords_group['lat'] = coords_group['Dep(start-coordinates)'].apply(lambda x: x[1])

    # Plot
            fig = px.scatter_geo(
                coords_group,
                lon='lon',
                lat='lat',
                text='Dep',
                size='CO2',
                color='CO2',
                projection='natural earth',
                title=f"Top 15 Departure Airports by CO₂ Emissions in {label}",
                hover_name='Dep',
                size_max=40
            )

            fig.update_traces(marker=dict(line=dict(width=0.5, color='black')))
            fig.update_layout(geo=dict(showland=True, landcolor="lightgray"))
            fig.show()

        plot_top_airport_map(df, label)




    elif mode == 2:
        df['Route'] = df['Dep'] + " → " + df['Arr']
        top_routes = df.groupby('Route')[['CO2']].sum().sort_values(by='CO2', ascending=False).head(10)

        top_routes.plot(kind='bar', legend=False, color='salmon')
        plt.title(f"Top 10 Routes by CO2 in Month {label}")
        plt.ylabel("CO2 (kg)")
        plt.xlabel("Route")
        plt.xticks(rotation=45, ha='right')
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
