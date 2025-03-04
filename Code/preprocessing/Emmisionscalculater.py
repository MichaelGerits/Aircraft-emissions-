
import pandas as pd
from preProcess import extract_ECTRLIDSeq
from openap import FuelFlow, Emission
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


fuelflow = FuelFlow(ac="A320")
emission = Emission(ac="A320")

TAS = 350
ALT = 30000

FF = fuelflow.enroute(mass=60000, tas=TAS, alt=ALT, vs=0)  # kg/s

CO2 = emission.co2(FF)  # g/s
H2O = emission.h2o(FF)  # g/s
NOx = emission.nox(FF, tas=TAS, alt=ALT)  # g/s
CO = emission.co(FF, tas=TAS, alt=ALT)  # g/s
HC = emission.hc(FF, tas=TAS, alt=ALT)  # g/s


df=extract_ECTRLIDSeq('Data/PositionData/March')[238925253]
seq=df["Sequence Number"]
Time=df["Time Over"]
FL=df["Flight Level"]
Lattitude=df["Latitude"]
Longitude=df["Longitude"]
FlightLevel=df["Flight Level"]
hours=[]
minutes=[]
Lat=[]
Long=[]
FL=[]
for row in Time: 
    hours.append(int(row[9:10]))
    minutes.append(int(row[11:13]))

for row in Lattitude:
    Lat.append(Lattitude)
    Long.append(Longitude)
    FL.append(FlightLevel)
    



delta=0
def DeltaTime(h1,m1,h2,m2):
    delta=0
    if m2>m1:
        delta=m2-m1
    if m2<m1:
        delta=60-m1+m2

    return delta

Delta=[]
for i in range(len(minutes)-2):
    Delta.append(DeltaTime(hours[i],minutes[i],hours[i+1],minutes[i+1]))

latitude = Lat
longitude = Long

# Convert latitude and longitude to radians
lat_rad = np.radians(Lat)
lon_rad = np.radians(Long)

# Assume a unit sphere (radius = 1)
radius = 1

# Convert to Cartesian coordinates
x = radius * np.cos(lat_rad) * np.cos(lon_rad)
y = radius * np.cos(lat_rad) * np.sin(lon_rad)
z = radius * np.sin(lat_rad)

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot points on the sphere
ax.scatter(x, y, z, c='b', marker='o')

# Draw the sphere for reference
u, v = np.mgrid[0:2 * np.pi:100j, 0:np.pi:50j]
xs = np.cos(u) * np.sin(v)
ys = np.sin(u) * np.sin(v)
zs = np.cos(v)
ax.plot_wireframe(xs, ys, zs, color='lightgray', alpha=0.5)

# Set labels and aspect
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_box_aspect([1,1,1])  # Equal aspect ratio

plt.show()