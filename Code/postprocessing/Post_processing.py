import pandas as pd
import glob
import os
import ast
import plotly.express as px

def plot_airport_map(df, label, airport_type='Dep'):
    if airport_type == 'Dep':
        coords_column = 'Dep(start-coordinates)'
        title = f"Top 15 Departure Airports by CO₂ Emissions in {label}"
    elif airport_type == 'Arr':
        coords_column = 'Arr(end-coordinates)'
        title = f"Top 15 Arrival Airports by CO₂ Emissions in {label}"
    else:
        raise ValueError("airport_type must be either 'Dep' or 'Arr'")

    df[f'{airport_type}CoordsStr'] = df[coords_column].apply(lambda x: str(x) if isinstance(x, list) else None)

    coords_group = df.groupby([airport_type, f'{airport_type}CoordsStr'])['CO2'].sum().reset_index()
    coords_group = coords_group.sort_values(by='CO2', ascending=False).head(15)

    coords_group[f'{airport_type}Coords'] = coords_group[f'{airport_type}CoordsStr'].apply(ast.literal_eval)

    coords_group = coords_group[coords_group[f'{airport_type}Coords'].apply(
        lambda x: isinstance(x, list) and len(x) == 2 and None not in x)]

    coords_group['lon'] = coords_group[f'{airport_type}Coords'].apply(lambda x: x[1])
    coords_group['lat'] = coords_group[f'{airport_type}Coords'].apply(lambda x: x[0])

    fig = px.scatter_geo(
        coords_group,
        lon='lon',
        lat='lat',
        text=airport_type,
        size='CO2',
        color='CO2',
        projection='natural earth',
        title=title,
        hover_name=airport_type,
        size_max=40
    )

    fig.update_traces(marker=dict(line=dict(width=0.5, color='black')))
    fig.update_layout(geo=dict(showland=True, landcolor="lightgray"))
    fig.show()

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

def load_csv():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dfs = []

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

    df['Start-Date'] = pd.to_datetime(df['Start-Date'], errors='coerce', dayfirst=True)
    df['End-date'] = pd.to_datetime(df['End-date'], errors='coerce', dayfirst=True)

    if 'Dep(start-coordinates)' in df.columns:
        df['Dep(start-coordinates)'] = df['Dep(start-coordinates)'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [None, None])
    if 'Arr(end-coordinates)' in df.columns:
        df['Arr(end-coordinates)'] = df['Arr(end-coordinates)'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [None, None])

    df.fillna("Unknown", inplace=True)

    return df, f"{year}{month}"

def summarize_flights(df):
    if {'CO2', 'NOX', 'Distance'}.issubset(df.columns):
        df['CO2'] = pd.to_numeric(df['CO2'], errors='coerce')
        df['NOX'] = pd.to_numeric(df['NOX'], errors='coerce')
        df['Distance'] = pd.to_numeric(df['Distance'], errors='coerce')

        num_flights = len(df)
        total_co2 = df['CO2'].sum()
        total_nox = df['NOX'].sum()
        total_distance = df['Distance'].sum() / 1000  # meters to kilometers

        print("\n=== Summary ===")
        print(f"Number of flights: {num_flights}")
        print(f"Total distance flown: {total_distance:.2f} km")
        print(f"Total CO2 emissions: {total_co2:.2f} kg")
        print(f"Total NOX emissions: {total_nox:.2f} kg")

        return total_co2, total_nox, total_distance
    else:
        print("Missing required columns in the data.")
        return 0, 0, 0

def group_by_aircraft_and_route(df):
    df['Route'] = df['Dep'] + " → " + df['Arr']
    grouped = df.groupby('Plane').agg({
        'CO2': 'sum',
        'NOX': 'sum',
        'Distance': 'sum',
        'Time': 'mean'
    })
    grouped['Distance (km)'] = grouped['Distance'] / 1000
    grouped['Avg Flight Time (min)'] = grouped['Time'] / 60
    return grouped[['CO2', 'NOX', 'Distance (km)', 'Avg Flight Time (min)']].sort_values(by='CO2', ascending=False)

def extract_top_departure_airports(df):
    if 'Dep' in df.columns:
        airport_emissions = df.groupby('Dep')[['CO2', 'NOX']].sum()
        top_airports = airport_emissions.sort_values(by='CO2', ascending=False).head(50)
        return top_airports
    else:
        print("Column 'Dep' not found — cannot calculate emissions by origin airport.")
        return pd.DataFrame()

def analyze_haul_emissions(df):
    if 'Haul' in df.columns:
        haul_group = df.groupby('Haul').agg({
            'CO2': 'sum',
            'NOX': 'sum',
            'Distance': 'sum'
        })
        haul_group['Distance (km)'] = haul_group['Distance'] / 1000
        return haul_group[['CO2', 'NOX', 'Distance (km)']]
    else:
        print("Column 'Haul' not found — skipping flight type analysis.")
        return pd.DataFrame()

def save_summary_csv(total_co2, total_nox, total_distance, top_airports, haul_emissions, aircraft_emissions, filename):
    if os.path.exists(filename):
        mode = 'a'
    else:
        mode = 'w'

    with open(filename, mode) as f:
        if mode == 'w':
            f.write(f"Total CO2 (kg),{total_co2:.2f}\n")
            f.write(f"Total NOX (kg),{total_nox:.2f}\n")
            f.write(f"Total Distance Flown (km),{total_distance:.2f}\n\n")
            f.write("Top 15 Departure Airports by CO2 Emissions:\n")
            top_airports.to_csv(f, lineterminator='\n')
            f.write("\nEmissions by Haul Type (CO2, NOX, Distance (km)):\n")
            haul_emissions.to_csv(f, lineterminator='\n')
            f.write("\nEmissions by Aircraft Type:\n")
            aircraft_emissions.to_csv(f, lineterminator='\n')
        else:
            f.write("\n\n=== New Entry ===\n")
            f.write(f"Total CO2 (kg),{total_co2:.2f}\n")
            f.write(f"Total NOX (kg),{total_nox:.2f}\n")
            f.write(f"Total Distance Flown (km),{total_distance:.2f}\n\n")
            f.write("Top 15 Departure Airports by CO2 Emissions:\n")
            top_airports.to_csv(f, lineterminator='\n')
            f.write("\nEmissions by Haul Type (CO2, NOX, Distance (km)):\n")
            haul_emissions.to_csv(f, lineterminator='\n')
            f.write("\nEmissions by Aircraft Type:\n")
            aircraft_emissions.to_csv(f, lineterminator='\n')

    print(f"Summary CSV updated: {filename}")

def main():
    df, label = load_csv()
    if df is not None:
        print("\nLoaded data preview:")
        print(df.head())

        total_co2, total_nox, total_distance = summarize_flights(df)
        aircraft_emissions = group_by_aircraft_and_route(df)
        top_airports = extract_top_departure_airports(df)
        haul_emissions = analyze_haul_emissions(df)

        summary_csv_filename = f"{label}sum.csv"
        save_summary_csv(total_co2, total_nox, total_distance, top_airports, haul_emissions, aircraft_emissions, summary_csv_filename)
        
        plot_airport_map(df, label, airport_type='Dep')
        plot_airport_map(df, label, airport_type='Arr')

if __name__ == "__main__":
    main()
