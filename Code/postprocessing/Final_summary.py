import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import matplotlib
from io import StringIO
from matplotlib.ticker import FuncFormatter

matplotlib.use('TkAgg')  # Or 'Agg' for non-interactive backend

def load_emissions_summary(file_path):
    """Load emissions data from a summary file."""
    data = {
        'totals': {},
        'top_departure_airports': None,
        'top_arrival_airports': None,
        'emissions_by_haul': None,
        'emissions_by_aircraft': None
    }

    with open(file_path, 'r') as f:
        lines = f.readlines()

    current_section = None

    for i, line in enumerate(lines):
        line = line.strip()

        # Section detection
        if line.startswith('==='):
            if 'New Entry' in line:
                current_section = 'header'
            elif 'Top 15 Departure Airports' in line:
                current_section = 'top_departure_airports'
            elif 'Top 15 Arrival Airports' in line:
                current_section = 'top_arrival_airports'
            elif 'Emissions by Haul Type' in line:
                current_section = 'haul_type'
            elif 'Emissions by Aircraft Type' in line:
                current_section = 'aircraft_type'
            continue

        if not line:
            continue

        def parse_csv_section(start_index, header_line):
            """Helper to parse CSV-style sections."""
            data_lines = []
            next_idx = start_index + 1
            while next_idx < len(lines) and lines[next_idx].strip() and not lines[next_idx].startswith('==='):
                data_lines.append(lines[next_idx])
                next_idx += 1
            csv_data = header_line + '\n' + ''.join(data_lines)
            return pd.read_csv(StringIO(csv_data))

        # Data extraction
        if current_section == 'header':
            if 'Total CO2 (kg)' in line:
                data['totals']['CO2'] = float(line.split(',')[1])
            elif 'Total NOX (kg)' in line:
                data['totals']['NOX'] = float(line.split(',')[1])
            elif 'Total Distance Flown (km)' in line:
                data['totals']['Distance'] = float(line.split(',')[1])

        elif current_section == 'top_departure_airports' and line.startswith('Dep,CO2,NOX'):
            data['top_departure_airports'] = parse_csv_section(i, line)

        elif current_section == 'haul_type' and line.startswith('Haul,CO2,NOX,Distance (km)'):
            data['emissions_by_haul'] = parse_csv_section(i, line)

        elif current_section == 'aircraft_type' and line.startswith('Plane,CO2,NOX,Distance (km),Avg Flight Time (min)'):
            data['emissions_by_aircraft'] = parse_csv_section(i, line)

    return data

def load_all_sum_files(directory):
    """Load all summary files in a directory."""
    files = glob.glob(os.path.join(directory, '*sum.csv'))
    all_data = {}

    for file in files:
        filename = os.path.basename(file)
        try:
            year_month = filename[:6]  # Extract YYYYMM
            emissions_summary = load_emissions_summary(file)
            
            # Convert kg to metric tons for better readability
            all_data[year_month] = {
                'CO2_t': emissions_summary['totals'].get('CO2', 0) / 1000,
                'NOX_t': emissions_summary['totals'].get('NOX', 0) / 1000,
                'Distance_km': emissions_summary['totals'].get('Distance', 0),
                'raw_data': emissions_summary
            }
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

    return all_data

def plot_emissions_trends(directory, output_dir=None):
    """Plot CO2 and NOX emission trends over time."""
    emissions_data = load_all_sum_files(directory)
    
    if not emissions_data:
        print("No data found to plot.")
        return

    # Prepare data
    months = sorted(emissions_data.keys())
    co2_values = [emissions_data[month]['CO2_t'] for month in months]
    nox_values = [emissions_data[month]['NOX_t'] for month in months]
    
    # Create plot
    plt.figure(figsize=(12, 6))
    ax = plt.gca()
    
    # CO2 plot
    ax.plot(months, co2_values, label='CO₂ Emissions', color='#1f77b4', 
            marker='o', linestyle='-', linewidth=2)
    ax.set_ylabel('CO₂ Emissions (metric tons)', color='#1f77b4')
    ax.tick_params(axis='y', labelcolor='#1f77b4')
    
    # NOX plot (secondary axis)
    ax2 = ax.twinx()
    ax2.plot(months, nox_values, label='NOₓ Emissions', color='#ff7f0e', 
             marker='s', linestyle='--', linewidth=2)
    ax2.set_ylabel('NOₓ Emissions (metric tons)', color='#ff7f0e')
    ax2.tick_params(axis='y', labelcolor='#ff7f0e')
    
    # Formatting
    ax.set_title('Monthly Aviation Emissions Trends')
    ax.set_xlabel('Year-Month')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(months)
    ax.set_xticklabels(months, rotation=45, ha='right')
    
    # Combine legends
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2, loc='upper left')
    
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(os.path.join(output_dir, 'emissions_trends.png'), dpi=300)
    plt.show()

def plot_top_airports(directory, airport_type='departure', top_n=15, output_dir=None):
    """Plot top airports by emissions."""
    files = glob.glob(os.path.join(directory, '*sum.csv'))
    combined_df = pd.DataFrame()

    for file in files:
        summary = load_emissions_summary(file)
        df = summary.get(f'top_{airport_type}_airports')
        if df is not None:
            combined_df = pd.concat([combined_df, df])

    if combined_df.empty:
        print(f"No {airport_type} airport data found.")
        return

    # Aggregate and sort
    col = 'Dep' if airport_type == 'departure' else 'Arr'
    result = (combined_df.groupby(col, as_index=False)[['CO2', 'NOX']]
              .sum()
              .sort_values('CO2', ascending=False)
              .head(top_n))
    
    # Convert to metric tons
    result['CO2_t'] = result['CO2'] / 1000
    result['NOX_t'] = result['NOX'] / 1000

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Bar plot for CO2
    bars = ax.bar(result[col], result['CO2_t'], color='#1f77b4', alpha=0.7, label='CO₂')
    ax.set_ylabel('CO₂ Emissions (metric tons)', color='#1f77b4')
    ax.tick_params(axis='y', labelcolor='#1f77b4')
    ax.set_xticklabels(result[col], rotation=45, ha='right')
    
    # Line plot for NOX on secondary axis
    ax2 = ax.twinx()
    line = ax2.plot(result[col], result['NOX_t'], color='#ff7f0e', 
                    marker='o', label='NOₓ', linewidth=2)
    ax2.set_ylabel('NOₓ Emissions (metric tons)', color='#ff7f0e')
    ax2.tick_params(axis='y', labelcolor='#ff7f0e')
    
    # Formatting
    title_type = 'Departure' if airport_type == 'departure' else 'Arrival'
    ax.set_title(f'Top {top_n} {title_type} Airports by Emissions')
    ax.grid(True, axis='y', alpha=0.3)
    
    # Combine legends
    lines = [bars[0], line[0]]
    labels = ['CO₂', 'NOₓ']
    ax.legend(lines, labels, loc='upper right')
    
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(os.path.join(output_dir, f'top_{airport_type}_airports.png'), dpi=300)
    plt.show()

def plot_efficiency_metrics(directory, category='haul', top_n=10, output_dir=None):
    """Plot efficiency metrics by category."""
    files = glob.glob(os.path.join(directory, '*sum.csv'))
    efficiency_data = []

    for file in files:
        year = os.path.basename(file)[:4]  # Extract year
        summary = load_emissions_summary(file)

        if category == 'haul':
            df = summary['emissions_by_haul']
            group_col = 'Haul'
        else:
            df = summary['emissions_by_aircraft']
            group_col = 'Plane'

        if df is not None and 'Distance (km)' in df.columns:
            df = df.copy()
            df['Year'] = year
            df['CO2_kg_per_km'] = df['CO2'] / df['Distance (km)']
            df['NOX_g_per_km'] = (df['NOX'] * 1000) / df['Distance (km)']
            efficiency_data.append(df[[group_col, 'Year', 'CO2_kg_per_km', 'NOX_g_per_km']])

    if not efficiency_data:
        print(f"No {category} efficiency data found.")
        return

    df_all = pd.concat(efficiency_data)
    
    # For aircraft, filter to top N most common
    if category == 'aircraft':
        aircraft_counts = df_all.groupby(group_col).size()
        top_aircraft = aircraft_counts.nlargest(top_n).index
        df_all = df_all[df_all[group_col].isin(top_aircraft)]

    # Create plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # CO2 efficiency plot
    pivot_co2 = df_all.pivot_table(index='Year', columns=group_col, 
                                 values='CO2_kg_per_km', aggfunc='mean')
    pivot_co2.plot(kind='bar', ax=ax1, width=0.8)
    ax1.set_title(f'CO₂ Emissions Efficiency by {category.capitalize()} Type')
    ax1.set_ylabel('kg CO₂ per km')
    ax1.grid(True, axis='y', alpha=0.3)
    ax1.legend(title=group_col, bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # NOX efficiency plot
    pivot_nox = df_all.pivot_table(index='Year', columns=group_col, 
                                 values='NOX_g_per_km', aggfunc='mean')
    pivot_nox.plot(kind='bar', ax=ax2, width=0.8)
    ax2.set_title(f'NOₓ Emissions Efficiency by {category.capitalize()} Type')
    ax2.set_ylabel('g NOₓ per km')
    ax2.grid(True, axis='y', alpha=0.3)
    ax2.legend(title=group_col, bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(os.path.join(output_dir, f'efficiency_{category}.png'), dpi=300)
    plt.show()

def analyze_single_file(file_path):
    """Perform detailed analysis of a single emissions file."""
    data = load_emissions_summary(file_path)
    
    if not data['totals']:
        print("No data found in file.")
        return

    print("\n=== SUMMARY ===")
    print(f"Total CO₂: {data['totals']['CO2']:,.2f} kg")
    print(f"Total NOₓ: {data['totals']['NOX']:,.2f} kg")
    print(f"Total Distance: {data['totals']['Distance']:,.2f} km")
    print(f"Overall CO₂ efficiency: {data['totals']['CO2']/data['totals']['Distance']:.4f} kg/km")
    
    if data['emissions_by_haul'] is not None:
        print("\n=== HAUL TYPE EFFICIENCY ===")
        data['emissions_by_haul']['CO2_kg_per_km'] = (
            data['emissions_by_haul']['CO2'] / data['emissions_by_haul']['Distance (km)'])
        print(data['emissions_by_haul'][['Haul', 'CO2_kg_per_km']].sort_values('CO2_kg_per_km'))
    
    if data['emissions_by_aircraft'] is not None:
        print("\n=== AIRCRAFT EFFICIENCY (TOP 10) ===")
        aircraft_eff = data['emissions_by_aircraft'].copy()
        aircraft_eff['CO2_kg_per_km'] = aircraft_eff['CO2'] / aircraft_eff['Distance (km)']
        aircraft_eff['NOX_g_per_km'] = (aircraft_eff['NOX'] * 1000) / aircraft_eff['Distance (km)']
        print(aircraft_eff[['Plane', 'CO2_kg_per_km', 'NOX_g_per_km']]
              .sort_values('CO2_kg_per_km')
              .head(10))
        
        print("\n=== LEAST EFFICIENT AIRCRAFT ===")
        print(aircraft_eff[['Plane', 'CO2_kg_per_km', 'NOX_g_per_km']]
              .sort_values('CO2_kg_per_km', ascending=False)
              .head(5))

# Example usage
if __name__ == "__main__":
    # Set your directory path where the CSV files are located
    data_directory = ''
    output_directory = ''  # Optional
    
    # Create output directory if it doesn't exist
    if output_directory and not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # 1. Plot emission trends
    plot_emissions_trends(data_directory, output_directory)
    
    # 2. Plot top airports
    plot_top_airports(data_directory, 'departure', 15, output_directory)
    plot_top_airports(data_directory, 'arrival', 15, output_directory)
    
    # 3. Plot efficiency metrics
    plot_efficiency_metrics(data_directory, 'haul', output_dir=output_directory)
    plot_efficiency_metrics(data_directory, 'aircraft', top_n=10, output_dir=output_directory)
    
    # 4. Analyze a single file in detail
    sample_file = os.path.join(data_directory, '202003sum.csv')
    analyze_single_file(sample_file)