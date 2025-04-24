import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from io import StringIO

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
    all_data = {}
    
    for file in files:
        filename = os.path.basename(file)
        year_month = filename[:6]  # Extract year and month from filename (e.g., '202401')
        emissions_summary = load_emissions_summary(file)
        
        co2 = emissions_summary['totals'].get('CO2', 0)
        nox = emissions_summary['totals'].get('NOX', 0)
        
        all_data[year_month] = {'CO2': co2, 'NOX': nox}
    
    return all_data

def plot_emissions(directory):
    emissions_data = load_all_sum_files(directory)
    
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



# Example usage:
directory_path = ''
plot_emissions(directory_path)
