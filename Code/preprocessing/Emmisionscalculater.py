
import pandas as pd
from preProcess import extract_ECTRLIDSeq
from openap import FuelFlow, Emission
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from openap.phase import FlightPhase
from haversine import haversine
import tracemalloc
import matplotlib.pyplot as plt
from AircraftIDandType import AircraftDictionary_Eurocontrol_and_Aircraft
EuroControlID=238925267
PlaneType=AircraftDictionary_Eurocontrol_and_Aircraft[EuroControlID]
print(PlaneType)
m_A320=181840     #in kg 
fuelflow = FuelFlow(ac=PlaneType)  #imports the specific flow for the type of aircraft
emission = Emission(ac=PlaneType)  #imports the specific emmisions for the type of aircraft

TAS = 350
ALT = 30000

FF = fuelflow.enroute(mass=m_A320, tas=TAS, alt=ALT, vs=0)  # kg/s

CO2 = emission.co2(FF)  # g/s
H2O = emission.h2o(FF)  # g/s
NOx = emission.nox(FF, tas=TAS, alt=ALT)  # g/s
CO = emission.co(FF, tas=TAS, alt=ALT)  # g/s
HC = emission.hc(FF, tas=TAS, alt=ALT)  # g/s


df=extract_ECTRLIDSeq('Data/PositionData/March')[EuroControlID]  #imports the data
seq=df["Sequence Number"]
Time=df["Time Over"]
Lattitude=df["Latitude"]
Longitude=df["Longitude"]
FlightLevel=df["Flight Level"]
hours=[]
minutes=[]
Lat=[]
Long=[]
FL=[]


for row in Time: 
    hours.append(int(row[-5:-3]))
    minutes.append(int(row[-2:]))
Lat.extend(Lattitude.astype(float).tolist())  #makes a float list of lat
Long.extend(Longitude.astype(float).tolist()), #makes a float list of long
FL.extend(FlightLevel.astype(float).tolist()), # 
print(Time)
print(hours)
delta=0
TimeStamp=[]
Ttot=0
def DeltaTime(h1,m1,h2,m2):
    delta=0
    if m2>m1:
        delta=m2-m1
    if m2<m1:
        delta=60-m1+m2
    if m2==m1:
        delta=0.5
    return delta

Delta=[]
for i in range(len(minutes)-2):
    Delta.append(DeltaTime(hours[i],minutes[i],hours[i+1],minutes[i+1]))

def DistanceCalc(lat1,long1,lat2,long2):
    p1=(lat1,long1)
    p2=(lat2,long2)
    D=haversine(p1,p2)
    return D

def VerSpeedCalc(dt,FL1,FL2):
    v_vertical=(FL2-FL1)/dt*10/0.3048/60   #vertical flight speed in ft/min
    return v_vertical
def HorSpeedCalc(dt,D):      #horizontal flight speed in m/s
    v_horizontal=(D)/dt/60*1000

    return v_horizontal
Distances=[]
VerSpeeds=[]
HorSpeeds=[]
Dis=0
DisTot=0
DeltaTot=0
Ttot=[]
FLTot=[]
FuelFlow1=[]
CO2Emmission=[]
H2OEmmission=[]
NOxEmmission=[]
COEmmission=[]
TotalCO2Emmission=0
TotalH2OEmmission=0
TotalNOxEmmission=0
TotalCOEmmission=0
for i in range(len(seq)-2):
    DisTot=DistanceCalc(Lat[i],Long[i],Lat[i+1],Long[i+1])+DisTot
    Dis=DistanceCalc(Lat[i],Long[i],Lat[i+1],Long[i+1])
    Distances.append(DisTot)
    DeltaTot=Delta[i]+DeltaTot
    FLTot.append(FL[i])
    Ttot.append(DeltaTot)
    VerticalSpeed=VerSpeedCalc(Delta[i],FL[i],FL[i+1])
    VerSpeeds.append(VerticalSpeed)
    HorizontalSpeed=HorSpeedCalc(Delta[i],Dis)
    HorSpeeds.append(HorizontalSpeed)
    FF = fuelflow.enroute(mass=m_A320, tas=HorSpeeds[i], alt=FLTot[i], vs=VerSpeeds[i])
    FuelFlow1.append(FF)
    CO2Emmission.append(emission.co2(FF))  # g/s
    H2OEmmission.append(emission.h2o(FF))  # g/s
    NOxEmmission.append(emission.nox(FF, tas=HorSpeeds[i], alt=FLTot[i]))  # g/s
    COEmmission.append(emission.co(FF, tas=HorSpeeds[i], alt=FLTot[i]))  # g/s
for i in range(len(CO2Emmission)-1):
    TotalCO2Emmission=TotalCO2Emmission+abs(Delta[i]*(CO2Emmission[i+1]+CO2Emmission[i])/2)*60 # g
    TotalH2OEmmission=TotalH2OEmmission+abs(Delta[i]*(H2OEmmission[i+1]+H2OEmmission[i])/2)*60# g
    TotalNOxEmmission=TotalNOxEmmission+abs(Delta[i]*(NOxEmmission[i+1]+NOxEmmission[i])/2)*60# g
    TotalCOEmmission=TotalCOEmmission+abs(Delta[i]*(COEmmission[i+1]+COEmmission[i])/2) *60# g

print("Total CO2 emmisions [kg]=", TotalCO2Emmission/1000)
print("Total H2O emmisions [kg]=", TotalH2OEmmission/1000)
print("Total HOx emmisions [kg]=", TotalNOxEmmission/1000)
print("Total CO emmisions [kg]=", TotalCOEmmission/1000)
plt.subplot(221)
plt.scatter(Ttot, FLTot, marker=".", color='green', lw=0)
plt.ylabel("altitude (ft)")

plt.subplot(222)
plt.scatter(Ttot, HorSpeeds, marker=".",color='blue', lw=0)
plt.ylabel("speed (m/s)")

plt.subplot(223)
plt.scatter(Ttot, VerSpeeds, marker=".",color='red', lw=0)
plt.ylabel("roc (fpm)")

plt.subplot(224)
plt.scatter(Ttot, FuelFlow1, marker=".",color='black', lw=0)
plt.ylabel("FuelFlow (kg/s)")

plt.show()


plt.subplot(221)
plt.plot(Ttot, CO2Emmission,marker=".", color='green',linestyle='-', lw=2)
plt.ylabel("CO2Emmission (g/s)")

plt.subplot(222)
plt.plot(Ttot, H2OEmmission, marker=".",color='blue',linestyle='-', lw=2)
plt.ylabel("H2OEmmission (g/s)")

plt.subplot(223)
plt.plot(Ttot, NOxEmmission, marker=".",color='red',linestyle='-', lw=2)
plt.ylabel("NOxEmmission (g/s)")

plt.subplot(224)
plt.plot(Ttot, COEmmission, marker=".",color='black',linestyle='-', lw=2)
plt.ylabel("COEmmission (g/s)")


plt.show()





# Convert latitude and longitude to radians
#lat_rad = np.radians(Lat)
#lon_rad = np.radians(Long)

# Assume a unit sphere (radius = 1)
#radius = 1

# Convert to Cartesian coordinates
#x = radius * np.cos(lat_rad) * np.cos(lon_rad)
#y = radius * np.cos(lat_rad) * np.sin(lon_rad)
#z = radius * np.sin(lat_rad)

# Create a 3D plot
#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')

# Plot points on the sphere
#ax.scatter(x, y, z, c='b', marker='o')

# Draw the sphere for reference
#u, v = np.mgrid[0:2 * np.pi:100j, 0:np.pi:50j]
#xs = np.cos(u) * np.sin(v)
#ys = np.sin(u) * np.sin(v)
#zs = np.cos(v)
#ax.plot_wireframe(xs, ys, zs, color='lightgray', alpha=0.5)

# Set labels and aspect
#ax.set_xlabel('X Axis')
#ax.set_ylabel('Y Axis')
#ax.set_zlabel('Z Axis')
#ax.set_box_aspect([1,1,1])  # Equal aspect ratio

#plt.show()