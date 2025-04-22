# import matplotlib.pyplot as plt
# import cartopy.crs as ccrs
# import cartopy.feature as cfeature
# import pandas as pd
# import numpy as np

# # Load and clean data
# df = pd.read_csv("dest1.csv", encoding='latin1')  # Adjusted to handle encoding issues
# df = df.dropna()

# # Extract coordinates for departures and arrivals
# dep_lons = df['Dep(start-coordinates)'].apply(lambda x: eval(x)[0])  # Extract Longitude from coordinates
# dep_lats = df['Dep(start-coordinates)'].apply(lambda x: eval(x)[1])  # Extract Latitude from coordinates
# arr_lons = df['Arr(end-coordinates)'].apply(lambda x: eval(x)[0])  # Extract Longitude from coordinates
# arr_lats = df['Arr(end-coordinates)'].apply(lambda x: eval(x)[1])  # Extract Latitude from coordinates

# # Combine departure and arrival coordinates
# all_lons = np.concatenate([dep_lons, arr_lons])  # All longitudes
# all_lats = np.concatenate([dep_lats, arr_lats])  # All latitudes

# # Create figure and set projection
# fig, ax = plt.subplots(figsize=(10, 7), subplot_kw={'projection': ccrs.PlateCarree()})

# # Set the extent to focus on the whole world (-180 to 180 longitude, -90 to 90 latitude)
# ax.set_extent([-25, 45, 34, 72], crs=ccrs.PlateCarree())

# # Add land, coastlines, and borders
# ax.coastlines()
# ax.add_feature(cfeature.BORDERS, linestyle=':')
# ax.add_feature(cfeature.LAND, color='lightgray')
# ax.add_feature(cfeature.OCEAN, color='lightblue')

# # Plot the departure and arrival coordinates
# ax.scatter(all_lons, all_lats, color='red', s=10, transform=ccrs.PlateCarree(), label="Flight Coordinates")

# # Add a legend
# ax.legend()

# # Add gridlines
# ax.gridlines(draw_labels=True, linestyle="--", linewidth=0.5)

# # Show plot
# plt.show()



import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
import numpy as np
from matplotlib.colors import LogNorm  # For better scaling of CO2 data

# Load and clean the data 
df = pd.read_csv("dest.csv", encoding='latin1')  
df = df.dropna()

# Extract coordinates for departures and arrivals
dep_lons = df['Dep(start-coordinates)'].apply(lambda x: eval(x)[0])  # Extract Longitude from coordinates
dep_lats = df['Dep(start-coordinates)'].apply(lambda x: eval(x)[1])  # Extract Latitude from coordinates
arr_lons = df['Arr(end-coordinates)'].apply(lambda x: eval(x)[0])  # Extract Longitude from coordinates
arr_lats = df['Arr(end-coordinates)'].apply(lambda x: eval(x)[1])  # Extract Latitude from coordinates

# CO2 emissions for each flight (split between departure and arrival)
co2_values = df['CO2']  # Total CO₂ emissions per flight
co2_half = co2_values / 2  # Split CO₂ emissions equally between departure and arrival

# Combine the departure and arrival coordinates
all_lons = np.concatenate([dep_lons, arr_lons])  # All longitudes
all_lats = np.concatenate([dep_lats, arr_lats])  # All latitudes
all_co2 = np.concatenate([co2_half, co2_half])  # CO₂ emissions for both points

# Create a DataFrame to group emissions by coordinate pairs
coords_df = pd.DataFrame({
    'Longitude': all_lons,
    'Latitude': all_lats,
    'CO2': all_co2
})

# Group by coordinates and sum CO₂ emissions
aggregated_df = coords_df.groupby(['Longitude', 'Latitude'], as_index=False).sum()

# Now we have aggregated CO2 emissions for the same coordinates

# Create figure and set projection
fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={'projection': ccrs.PlateCarree()})

# Set the extent to focus on Europe (Longitude: -25 to 45, Latitude: 34 to 72)
ax.set_extent([-25, 45, 34, 72], crs=ccrs.PlateCarree())

# Add land, coastlines, and borders
ax.coastlines()
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.LAND, color='lightgray')
ax.add_feature(cfeature.OCEAN, color='lightblue')

# Create a 2D histogram heatmap (hexbin) with logarithmic color scale
hb = ax.hexbin(
    aggregated_df['Longitude'], aggregated_df['Latitude'], C=aggregated_df['CO2'],  # CO₂ values for color intensity
    gridsize=100,  # Size of hexagons
    cmap='YlOrRd',  # Colormap
    mincnt=1,  # Ignore empty bins
    alpha=0.6,
    transform=ccrs.PlateCarree(),
    norm=LogNorm()  # Apply logarithmic color scaling
)

# Add colorbar
cbar = plt.colorbar(hb, ax=ax, orientation='vertical', shrink=0.6, label="Log CO₂ Emissions")

# Show plot
plt.show()






# import matplotlib.pyplot as plt
# import cartopy.crs as ccrs
# import cartopy.feature as cfeature
# import pandas as pd
# import numpy as np
# from scipy.stats import gaussian_kde
# from matplotlib.colors import LogNorm  # Import LogNorm for better scaling

# # Load and clean data
# df = pd.read_csv("Unique_airports_201903.csv")
# df = df.dropna()

# # Extract coordinates for departures and arrivals
# lat_long_list = list(zip(df['ADEP Longitude'], df['ADEP Latitude']))
# lat_long_list_arrival = list(zip(df['ADES Longitude'], df['ADES Latitude']))

# # Combine both departure and arrival coordinates
# all_coords = np.array(lat_long_list + lat_long_list_arrival)  # Convert to NumPy array

# # Create figure and set projection
# fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={'projection': ccrs.PlateCarree()})

# # Set the extent to focus on Europe (Longitude: -25 to 45, Latitude: 34 to 72)
# ax.set_extent([-25, 45, 34, 72], crs=ccrs.PlateCarree())

# # Add land, coastlines, and borders
# ax.coastlines()
# ax.add_feature(cfeature.BORDERS, linestyle=':')
# ax.add_feature(cfeature.LAND, color='lightgray')  # Lighter land color
# ax.add_feature(cfeature.OCEAN, color='lightblue')

# # Generate a KDE heatmap
# x, y = all_coords[:, 0], all_coords[:, 1]  # Longitude and Latitude
# kde = gaussian_kde([x, y])  # Fit KDE model

# # Create a grid for the heatmap
# x_grid = np.linspace(-25, 45, 300)  # Increase points for smoother heatmap
# y_grid = np.linspace(34, 72, 300)
# X, Y = np.meshgrid(x_grid, y_grid)
# Z = kde(np.vstack([X.ravel(), Y.ravel()])).reshape(X.shape)  # Evaluate KDE on grid

# # Adjust the colormap & normalization
# heatmap = ax.imshow(
#     Z, extent=[-25, 45, 34, 72], origin='lower', 
#     cmap='cividis',  # 🔹 Less red, more contrast (Alternatives: 'viridis', 'coolwarm', 'inferno')
#     norm=LogNorm(vmin=Z.min() + 1e-6, vmax=Z.max()),  # 🔹 Log scaling to balance colors
#     alpha=0.7  # 🔹 Adjust transparency for better visibility
# )

# # Add colorbar
# cbar = plt.colorbar(heatmap, ax=ax, orientation='vertical', shrink=0.6, label="Log Density")

# # Show plot
# plt.show()
