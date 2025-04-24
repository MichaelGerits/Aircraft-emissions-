import pandas as pd
import glob
import os
import ast


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

    # Clean and process the data
    df['Start-Date'] = pd.to_datetime(df['Start-Date'], errors='coerce', dayfirst=True)
    df['End-date'] = pd.to_datetime(df['End-date'], errors='coerce', dayfirst=True)

    if 'Dep(start-coordinates)' in df.columns:
        df['Dep(start-coordinates)'] = df['Dep(start-coordinates)'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [None, None])
    if 'Arr(end-coordinates)' in df.columns:
        df['Arr(end-coordinates)'] = df['Arr(end-coordinates)'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [None, None])

    df.fillna("Unknown", inplace=True)

    return df, f"{year}{month}"

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

        return total_co2, total_nox
    else:
        print("Missing 'CO2' or 'NOX' column in the data.")
        return 0, 0

def group_by_aircraft_and_route(df):
    by_plane = df.groupby('Plane')[['CO2', 'NOX']].sum().sort_values(by='CO2', ascending=False)
    df['Route'] = df['Dep'] + " → " + df['Arr']
    return by_plane

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
        haul_emissions = df.groupby('Haul')[['CO2', 'NOX']].sum()
        return haul_emissions
    else:
        print("Column 'Haul' not found — skipping flight type analysis.")
        return pd.DataFrame()

def save_summary_csv(total_co2, total_nox, top_airports, haul_emissions, aircraft_emissions, filename):
    if os.path.exists(filename):
        mode = 'a'
    else:
        mode = 'w'

    with open(filename, mode) as f:
        if mode == 'w':
            f.write(f"Total CO2,{total_co2:.2f}\n")
            f.write(f"Total NOX,{total_nox:.2f}\n")
            f.write("\nTop 15 Departure Airports by CO2 Emissions:\n")
            top_airports.to_csv(f, lineterminator='\n')  # Changed line_terminator to lineterminator
            f.write("\nEmissions by Haul Type:\n")
            haul_emissions.to_csv(f, lineterminator='\n')  # Changed here too
            f.write("\nEmissions by Aircraft Type:\n")
            aircraft_emissions.to_csv(f, lineterminator='\n')  # And here
        else:
            f.write("\n\n=== New Entry ===\n")
            f.write(f"Total CO2,{total_co2:.2f}\n")
            f.write(f"Total NOX,{total_nox:.2f}\n")
            f.write("\nTop 15 Departure Airports by CO2 Emissions:\n")
            top_airports.to_csv(f, lineterminator='\n')  # Changed here
            f.write("\nEmissions by Haul Type:\n")
            haul_emissions.to_csv(f, lineterminator='\n')  # And here
            f.write("\nEmissions by Aircraft Type:\n")
            aircraft_emissions.to_csv(f, lineterminator='\n')  # And here
    print(f"Summary CSV updated: {filename}")
    

def main():
    df, label = load_csv()
    if df is not None:
        print("\nLoaded data preview:")
        print(df.head())

        total_co2, total_nox = summarize_flights(df)
        aircraft_emissions = group_by_aircraft_and_route(df)
        top_airports = extract_top_departure_airports(df)
        haul_emissions = analyze_haul_emissions(df)

        summary_csv_filename = f"{label}sum.csv"
        save_summary_csv(total_co2, total_nox, top_airports, haul_emissions, aircraft_emissions, summary_csv_filename)

if __name__ == "__main__":
    main()
