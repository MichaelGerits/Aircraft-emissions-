
import pandas as pd
import numpy as np

df = pd.read_csv("Data\Airports\AirportsLongLat.csv")

LongitudeAirport=round(df["lon"],2)
LatAirport=round(df["lat"],2)
Name_of_Airport=df["city"]
LongitudeAirportlist=[]
Name_of_Airportlist=[]
LattitudeAirportlist=[]
ID=[]
#+abs(LatAirport[i]*10**number)
for i in range(28256):
    number=len(str(LongitudeAirport[i]))
    LongitudeAirportlist.append((LongitudeAirport[i]))
    Name_of_Airportlist.append(Name_of_Airport[i])
    LattitudeAirportlist.append((LatAirport[i],LongitudeAirport[i]))
    #ID.append(round(0.5*(LongitudeAirport[i]+LatAirport[i])*(LongitudeAirport[i]+LatAirport[i]+1)-LatAirport[i],4))

#AirportDicto=dict(zip([(LongitudeAirport,LattitudeAirportlist)], Name_of_Airportlist))

