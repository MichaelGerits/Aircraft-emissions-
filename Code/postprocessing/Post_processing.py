import pandas as pd
import glob
import os

def get_valid_year():
    """Prompt user for a valid year (2015-2021)."""
    while True:
        try:
            year = int(input("Enter year (2015-2021): "))
            if 2015 <= year <= 2021:
                return str(year)
            print("Error: Year must be between 2015 and 2021.")
        except ValueError:
            print("Error: Please enter a valid integer.")

def get_valid_month():
    """Prompt user for a valid month (03, 06, 09, 12)."""
    valid_months = ['03', '06', '09', '12']
    while True:
        month = input("Enter month (03, 06, 09, or 12): ")
        if month in valid_months:
            return month
        print("Error: Month must be 03, 06, 09, or 12.")

def load_csv(mode):
    """Load CSV(s) based on the selected mode."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dfs = []

    if mode == 1:  # All files for a year (e.g., 2015*.csv)
        year = get_valid_year()
        pattern = os.path.join(script_dir, f"{year}*.csv")
    elif mode == 2:  # All files for a month (e.g., *06.csv)
        month = get_valid_month()
        pattern = os.path.join(script_dir, f"*{month}.csv")
    elif mode == 3:  # Specific year+month (e.g., 201506.csv)
        year = get_valid_year()
        month = get_valid_month()
        pattern = os.path.join(script_dir, f"{year}{month}.csv")

    files = glob.glob(pattern)
    if not files:
        print("No matching files found.")
        return None

    for file in files:
        try:
            df = pd.read_csv(file)
            dfs.append(df)
            print(f"Loaded: {os.path.basename(file)}")
        except Exception as e:
            print(f"Error loading {file}: {e}")

    return pd.concat(dfs, ignore_index=True) if dfs else None

def main():
    print("=== CSV Loading Modes ===")
    print("1. Load all data for a specific year")
    print("2. Load all data for a specific month")
    print("3. Load data for a specific year+month")

    while True:
        try:
            mode = int(input("Choose mode (1-3): "))
            if mode in {1, 2, 3}:
                break
            print("Error: Mode must be 1, 2, or 3.")
        except ValueError:
            print("Error: Please enter a valid integer.")

    df = load_csv(mode)
    if df is not None:
        print("\nLoaded data summary:")
        print(df.head())

if __name__ == "__main__":
    main()