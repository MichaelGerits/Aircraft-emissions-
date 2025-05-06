import pandas as pd
import glob
import os
import ast
import re
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

def plot_monthly_emissions(monthly_data, label):
    """Create a time series plot of emissions by month"""
    if len(monthly_data) <= 1:
        print("Need multiple months to plot monthly emissions")
        return
    
    fig = px.line(
        monthly_data,
        x='Month',
        y=['CO2', 'NOX'],
        title=f"Monthly Emissions ({label})",
        labels={'value': 'Emissions (kg)', 'variable': 'Emission Type'},
        markers=True
    )
    
    fig.update_layout(
        yaxis_title="Emissions (kg)",
        xaxis_title="Month",
        legend_title="Emission Type"
    )
    
    # Format y-axis to show full numbers
    fig.update_yaxes(tickformat=".0f")
    
    fig.show()

def get_available_dates():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pattern = os.path.join(script_dir, "*.csv")
    files = sorted(glob.glob(pattern))

    date_pattern = re.compile(r'(\d{6})\.csv$')
    dates = []

    for file in files:
        match = date_pattern.search(os.path.basename(file))
        if match:
            dates.append(match.group(1))

    return sorted(dates), script_dir

def prompt_date_selection(available_dates):
    print("\nAvailable datasets:")
    for idx, date in enumerate(available_dates):
        year = date[:4]
        month = date[4:]
        print(f"{idx + 1}: {year}-{month}")

    selection = input("\nEnter the numbers of the dates to load (e.g., 1,3,5): ")
    try:
        indices = [int(i.strip()) - 1 for i in selection.split(",")]
        selected = [available_dates[i] for i in indices if 0 <= i < len(available_dates)]
        return selected
    except Exception as e:
        print(f"Invalid selection: {e}")
        return []

def load_csv():
    available_dates, script_dir = get_available_dates()
    if not available_dates:
        print("No CSV files found.")
        return None, None, None

    selected_dates = prompt_date_selection(available_dates)
    if not selected_dates:
        print("No valid dates selected.")
        return None, None, None

    dfs = []
    monthly_data = []
    
    for date_str in selected_dates:
        file_path = os.path.join(script_dir, f"{date_str}.csv")
        try:
            df = pd.read_csv(file_path)
            dfs.append(df)
            print(f"Loaded: {os.path.basename(file_path)}")
            
            # Calculate monthly totals
            if {'CO2', 'NOX'}.issubset(df.columns):
                df['CO2'] = pd.to_numeric(df['CO2'], errors='coerce')
                df['NOX'] = pd.to_numeric(df['NOX'], errors='coerce')
                monthly_data.append({
                    'Month': pd.to_datetime(date_str, format='%Y%m').strftime('%Y-%m'),
                    'CO2': df['CO2'].sum(),
                    'NOX': df['NOX'].sum()
                })
                
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    if not dfs:
        return None, None, None

    df = pd.concat(dfs, ignore_index=True)

    df['Start-Date'] = pd.to_datetime(df['Start-Date'], errors='coerce', dayfirst=True)
    df['End-date'] = pd.to_datetime(df['End-date'], errors='coerce', dayfirst=True)

    if 'Dep(start-coordinates)' in df.columns:
        df['Dep(start-coordinates)'] = df['Dep(start-coordinates)'].apply(
            lambda x: ast.literal_eval(x) if pd.notna(x) else [None, None])
    if 'Arr(end-coordinates)' in df.columns:
        df['Arr(end-coordinates)'] = df['Arr(end-coordinates)'].apply(
            lambda x: ast.literal_eval(x) if pd.notna(x) else [None, None])

    df.fillna("Unknown", inplace=True)
    label = "_".join(selected_dates)
    monthly_df = pd.DataFrame(monthly_data) if monthly_data else None
    return df, label, monthly_df

def summarize_flights(df):
    if {'CO2', 'NOX', 'Distance'}.issubset(df.columns):
        df['CO2'] = pd.to_numeric(df['CO2'], errors='coerce')
        df['NOX'] = pd.to_numeric(df['NOX'], errors='coerce')
        df['Distance'] = pd.to_numeric(df['Distance'], errors='coerce')

        num_flights = len(df)
        total_co2 = df['CO2'].sum()*0.5
        total_nox = df['NOX'].sum()*0.5
        total_distance = df['Distance'].sum() / 1000 *0.5 # meters to kilometers

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
    grouped.index.name = 'Aircraft Type'
    grouped['Distance (km)'] = grouped['Distance'] / 1000*0.5
    grouped['Avg Flight Time (min)'] = grouped['Time'] / 60*0.5
    return grouped[['CO2', 'NOX', 'Distance (km)', 'Avg Flight Time (min)']].sort_values(by='CO2', ascending=False)

def extract_top_departure_airports(df):
    if 'Dep' in df.columns:
        airport_emissions = df.groupby('Dep')[['CO2', 'NOX']].sum()*0.5
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
        haul_group.index.name = 'Haul Type'
        haul_group['Distance (km)'] = haul_group['Distance'] / 1000
        return haul_group[['CO2', 'NOX', 'Distance (km)']]*0.5
    else:
        print("Column 'Haul' not found — skipping flight type analysis.")
        return pd.DataFrame()

def save_summary_csv(total_co2, total_nox, total_distance, top_airports, haul_emissions, aircraft_emissions, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        pass  # Clear file

    def write_summary(f):
        f.write("=== SUMMARY ===\n")
        f.write(f"Total CO2 (kg),{total_co2:.2f}\n")
        f.write(f"Total NOX (kg),{total_nox:.2f}\n")
        f.write(f"Total Distance Flown (km),{total_distance:.2f}\n\n")

        f.write("=== Top Departure Airports by CO2 Emissions ===\n")
        top_airports.to_csv(f, index=True)
        f.write("\n")

        f.write("\n=== Emissions by Haul Type ===\n")
        haul_emissions.to_csv(f, index=True)
        f.write("\n")

        f.write("\n=== Emissions by Aircraft Type ===\n")
        aircraft_emissions.to_csv(f, index=True)

    with open(filename, 'a', encoding='utf-8') as f:
        write_summary(f)

def main():
    df, label, monthly_data = load_csv()
    if df is not None:
        print("\nLoaded data preview:")
        print(df.head())

        total_co2, total_nox, total_distance = summarize_flights(df)
        aircraft_emissions = group_by_aircraft_and_route(df)
        top_airports = extract_top_departure_airports(df)
        haul_emissions = analyze_haul_emissions(df)

        summary_csv_filename = f"{label}_summary.csv"
        save_summary_csv(total_co2, total_nox, total_distance, top_airports, 
                        haul_emissions, aircraft_emissions, summary_csv_filename)

        plot_airport_map(df, label, airport_type='Dep')
        plot_airport_map(df, label, airport_type='Arr')
        
        if monthly_data is not None and len(monthly_data) > 1:
            plot_monthly_emissions(monthly_data, label)

if __name__ == "__main__":
    main()