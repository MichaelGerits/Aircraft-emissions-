import pandas as pd # data loading in, reads csv files quickly and easily
from fastmeteo import Grid
import matplotlib as mpl
import openap
import seaborn
import cartopy




#import haversine as hs   
#from haversine import Unit

#df = pd.read_csv("Data/Route_2003.csv")

# Define flight data
#flight = pd.DataFrame({
#    "timestamp": ["2021-10-12T01:10:00", "2021-10-12T01:20:00"],
#    "latitude": [40.3, 42.5],
#    "longitude": [4.2, 6.6],
#    "altitude": [25000, 30000],  # Altitude in feet
#})

# Initialize FastMeteo Grid with local data storage path
#fmg = Grid(local_store="/tmp/era5-zarr")

# Interpolate and retrieve meteorological data for the flight
#flight_with_weather = fmg.interpolate(flight)
#print(flight_with_weather)