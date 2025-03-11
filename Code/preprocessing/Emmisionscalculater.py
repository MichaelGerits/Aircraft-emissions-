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
from AircraftIDandType import aircraft_dict_mass
from AircraftIDandType import aircraft_dict
from AirportClassifier import AirportDicto



EuroControlID=238927688
PlaneType=AircraftDictionary_Eurocontrol_and_Aircraft[EuroControlID] #defines the planetype that will be used 
print(PlaneType)   
m_A320=aircraft_dict_mass[aircraft_dict[PlaneType]]     #in kg 
fuelflow = FuelFlow(ac=PlaneType)  #imports the specific flow for the type of aircraft
emission = Emission(ac=PlaneType)  #imports the specific emmisions for the type of aircraft


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


for row in Time: #imports the time as a list to make a list of hours and minutes 
    hours.append(int(row[-5:-3]))
    minutes.append(int(row[-2:]))
Lat.extend(Lattitude.astype(float).tolist())  #makes a float list of lattitude 
Long.extend(Longitude.astype(float).tolist()), #makes a float list of longtude 
FL.extend(FlightLevel.astype(float).tolist()), #makes a float list of the flight level  

delta=0    
TimeStamp=[]
Ttot=0
def DeltaTime(h1,m1,h2,m2):   #makes a function that calculates the time difference between two time points (unit minuts)
    delta=0
    if m2>m1:
        delta=m2-m1
    if m2<m1:
        delta=60-m1+m2
    if m2==m1:
        delta=0.5
    return delta

Delta=[]
for i in range(len(minutes)-2):    #makes a list of delta values.
    Delta.append(DeltaTime(hours[i],minutes[i],hours[i+1],minutes[i+1]))

def DistanceCalc(lat1,long1,lat2,long2): #returns the distance betweem two points in km 
    p1=(lat1,long1)
    p2=(lat2,long2)
    D=haversine(p1,p2)
    return D

def VerSpeedCalc(dt,FL1,FL2):
    v_vertical=(FL2-FL1)/dt*100   #vertical flight speed in ft/min
    return v_vertical
def HorSpeedCalc(dt,D):      #horizontal flight speed in kts
    v_horizontal=(D)/dt/60*1000*1.943844
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
TotalFuel=0
CO2Emmission=[]
H2OEmmission=[]
NOxEmmission=[]
COEmmission=[]
TotalCO2Emmission=0
TotalH2OEmmission=0
TotalNOxEmmission=0
TotalCOEmmission=0


for i in range(len(seq)-2):
    DisTot=DistanceCalc(Lat[i],Long[i],Lat[i+1],Long[i+1])+DisTot   #Caluculates the total distance travelled in km 
    Dis=DistanceCalc(Lat[i],Long[i],Lat[i+1],Long[i+1])   #Calculate the distance between two sequence point in km 
    Distances.append(DisTot)  # Makes a list of the total distances at a specific point in a journey 
    DeltaTot=Delta[i]+DeltaTot  # creates 
    FLTot.append(FL[i])
    Ttot.append(DeltaTot)
    VerticalSpeed=VerSpeedCalc(Delta[i],FL[i],FL[i+1])
    VerSpeeds.append(VerticalSpeed)
    HorizontalSpeed=HorSpeedCalc(Delta[i],Dis)
    HorSpeeds.append(HorizontalSpeed)
    FF = fuelflow.enroute(mass=m_A320, tas=HorSpeeds[i], alt=FL[i]*100, vs=VerSpeeds[i])
    TotalFuel=TotalFuel+FF*Delta[i]*60
    FuelFlow1.append(FF)
    CO2Emmission.append(emission.co2(FF))  # g/s
    H2OEmmission.append(emission.h2o(FF))  # g/s
    NOxEmmission.append(emission.nox(FF, tas=HorSpeeds[i], alt=FL[i]*100))  # g/s
    COEmmission.append(emission.co(FF, tas=HorSpeeds[i], alt=FL[i]*100))  # g/s



for i in range(len(CO2Emmission)-1):
    TotalCO2Emmission=TotalCO2Emmission+abs(Delta[i]*(CO2Emmission[i]))*60 # g
    TotalH2OEmmission=TotalH2OEmmission+abs(Delta[i]*(H2OEmmission[i+1]+H2OEmmission[i])/2)*60# g
    TotalNOxEmmission=TotalNOxEmmission+abs(Delta[i]*(NOxEmmission[i+1]+NOxEmmission[i])/2)*60# g
    TotalCOEmmission=TotalCOEmmission+abs(Delta[i]*(COEmmission[i+1]+COEmmission[i])/2) *60# g

print("Total CO2 emmisions [kg]=", TotalCO2Emmission/1000)
print("Total H2O emmisions [kg]=", TotalH2OEmmission/1000)
print("Total HOx emmisions [kg]=", TotalNOxEmmission/1000)
print("Total CO emmisions [kg]=", TotalCOEmmission/1000)
print("Total fuel spent=",TotalFuel)

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



