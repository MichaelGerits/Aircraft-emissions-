
import pandas as pd
from preProcess import extract_ECTRLIDSeq
from openap import FuelFlow, Emission

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


df=extract_ECTRLIDSeq('Data/PositionData/March')[238925251]
seq=df["Sequence Number"]
Time=df["Time Over"]
FL=df["Flight Level"]
hours=[]
minutes=[]
for row in Time: 
    hours.append(int(row[9:10]))
    minutes.append(int(row[12:13]))


def DeltaTime(h1,m1,h2,m2):
    delta=0
    if m2<m1:
        delta=60-m1+m2
    if m2>m1:
        delta=m2-m1

    return delta


for i in range(len(minutes)-1):
    print(DeltaTime(hours[i],minutes[i],hours[i+1],minutes[i+1]))

