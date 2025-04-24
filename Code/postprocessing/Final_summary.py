import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from io import StringIO
import re

def load_emissions_summary(file_path):
    """Load data from an emissions summary CSV file with the given format."""
    
    data = {
        'totals': {},
        'top_departure_airports': None,
        'emissions_by_haul': None,
        'emissions_by_aircraft': None
    }
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('==='):
            if 'EMISSIONS SUMMARY' in line:
                current_section = 'summary'
            elif 'Routes with Highest CO2 Emissions' in line:
                current_section = 'routes'
            elif 'New Entry' in line:
                current_section = 'new_entry'
            elif 'Top 15 Departure Airports' in line:
                current_section = 'top_airports'
            elif 'Emissions by Haul Type' in line:
                current_section = 'haul_type'
            elif 'Emissions by Aircraft Type' in line:
                current_section = 'aircraft_type'
            continue
        
        if not line:
            continue
            
        if current_section == 'summary':
            if 'Total CO2 Emissions:' in line:
                data['totals']['CO2'] = float(line.split(':')[1].strip().split()[0])
            elif 'Total NOX Emissions:' in line:
                data['totals']['NOX'] = float(line.split(':')[1].strip().split()[0])
                
        elif current_section == 'new_entry':
            if line.startswith('Total CO2'):
                data['totals']['CO2'] = float(line.split(',')[1])
            elif line.startswith('Total NOX'):
                data['totals']['NOX'] = float(line.split(',')[1])
                
        elif current_section == 'top_airports':
            if line.startswith('Dep,CO2,NOX'):
                data_start = lines.index(line + '\n') + 1
                data_end = data_start
                while data_end < len(lines) and lines[data_end].strip() and not lines[data_end].startswith('==='):
                    data_end += 1
                csv_data = ''.join(lines[data_start:data_end])
                data['top_departure_airports'] = pd.read_csv(StringIO(csv_data))
                
        elif current_section == 'haul_type':
            if line.startswith('Haul,CO2,NOX'):
                data_start = lines.index(line + '\n') + 1
                data_end = data_start
                while data_end < len(lines) and lines[data_end].strip() and not lines[data_end].startswith('==='):
                    data_end += 1
                csv_data = ''.join(lines[data_start:data_end])
                data['emissions_by_haul'] = pd.read_csv(StringIO(csv_data))
                
        elif current_section == 'aircraft_type':
            if line.startswith('Plane,CO2,NOX'):
                data_start = lines.index(line + '\n') + 1
                data_end = data_start
                while data_end < len(lines) and lines[data_end].strip() and not lines[data_end].startswith('==='):
                    data_end += 1
                csv_data = ''.join(lines[data_start:data_end])
                data['emissions_by_aircraft'] = pd.read_csv(StringIO(csv_data))
    
    return data

def load_all_sum_files(directory):
    """Load all *sum.csv files in a directory."""
    files = glob.glob(os.path.join(directory, '*sum.csv'))
    print(f"Found {len(files)} sum files in {directory}: {files}")  # Debug output
    
    all_data = {}
    
    for file in files:
        try:
            filename = os.path.basename(file)
            year_month = filename[:6]  # Extract year and month from filename (e.g., '202003')
            emissions_summary = load_emissions_summary(file)
            
            co2 = emissions_summary['totals'].get('CO2', 0)
            nox = emissions_summary['totals'].get('NOX', 0)
            
            all_data[year_month] = {'CO2': co2, 'NOX': nox}
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")
            continue
    
    return all_data

def plot_emissions(directory):
    emissions_data = load_all_sum_files(directory)
    
    if not emissions_data:
        print("No emissions data found to plot!")
        return
    
    # Prepare the data for plotting
    months = sorted(emissions_data.keys())
    co2_values = [emissions_data[month]['CO2'] for month in months]
    nox_values = [emissions_data[month]['NOX'] for month in months]
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(months, co2_values, label='CO2 Emissions (tons)', color='blue', marker='o')
    plt.plot(months, nox_values, label='NOX Emissions (tons)', color='green', marker='o')
    
    plt.title('Total CO2 and NOX Emissions Over Time')
    plt.xlabel('Year-Month')
    plt.ylabel('Emissions (tons)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    
    # Show the plot
    plt.show()

def load_all_sum_files_grouped(directory):
    """Load all *sum.csv files and group by year."""
    files = glob.glob(os.path.join(directory, '*sum.csv'))
    print(f"Found {len(files)} sum files for yearly grouping: {files}")  # Debug output
    
    yearly_data = {}
    
    for file in files:
        try:
            filename = os.path.basename(file)
            match = re.match(r'^(\d{4})\d{2}sum\.csv$', filename)
            if not match:
                continue
            
            year = match.group(1)
            emissions_summary = load_emissions_summary(file)
            
            if year not in yearly_data:
                yearly_data[year] = {
                    'airports': [],
                    'aircraft': [],
                    'totals': {'CO2': [], 'NOX': []}
                }
            
            # Aggregate airport data
            if emissions_summary['top_departure_airports'] is not None:
                airports = emissions_summary['top_departure_airports'].head(5)
                yearly_data[year]['airports'].append(airports)
            
            # Aggregate aircraft data
            if emissions_summary['emissions_by_aircraft'] is not None:
                aircraft = emissions_summary['emissions_by_aircraft']
                yearly_data[year]['aircraft'].append(aircraft)
            
            # Store totals
            yearly_data[year]['totals']['CO2'].append(emissions_summary['totals'].get('CO2', 0))
            yearly_data[year]['totals']['NOX'].append(emissions_summary['totals'].get('NOX', 0))
        except Exception as e:
            print(f"Error processing {file} for yearly grouping: {str(e)}")
            continue
    
    return yearly_data

def plot_yearly_emissions(yearly_data):
    """Plot emissions trends, top airports, and aircraft per year."""
    if not yearly_data:
        print("No yearly data found to plot!")
        return
    
    for year, data in yearly_data.items():
        # Skip if no data
        if not data['airports'] or not data['aircraft']:
            print(f"Skipping {year} - incomplete data")
            continue
        
        # --- Plot 1: Top 5 Airports ---
        plt.figure(figsize=(15, 6))
        
        # Aggregate airport emissions across all months
        airports_combined = pd.concat(data['airports'])
        top_airports = airports_combined.groupby('Dep').sum().nlargest(5, 'CO2')
        
        plt.subplot(1, 2, 1)
        top_airports['CO2'].plot(kind='bar', color='skyblue')
        plt.title(f'Top 5 Departure Airports by CO2 Emissions ({year})')
        plt.xlabel('Airport')
        plt.ylabel('CO2 Emissions (tons)')
        plt.xticks(rotation=45)
        
        # --- Plot 2: Aircraft Emissions ---
        aircraft_combined = pd.concat(data['aircraft'])
        top_aircraft = aircraft_combined.groupby('Plane').sum().nlargest(5, 'CO2')
        
        plt.subplot(1, 2, 2)
        top_aircraft['CO2'].plot(kind='pie', autopct='%1.1f%%', startangle=90)
        plt.title(f'Top 5 Aircraft by CO2 Emissions ({year})')
        plt.ylabel('')
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up one level to the main project directory where the sum files are
    directory_path = os.path.join(script_dir, '..')
    
    # Convert to absolute path and normalize
    directory_path = os.path.abspath(directory_path)
    
    print(f"Working directory: {os.getcwd()}")
    print(f"Looking for sum files in: {directory_path}")
    
    # First plot - monthly emissions
    plot_emissions(directory_path)
    
    # Second plot - yearly grouped data
    yearly_data = load_all_sum_files_grouped(directory_path)
    plot_yearly_emissions(yearly_data)