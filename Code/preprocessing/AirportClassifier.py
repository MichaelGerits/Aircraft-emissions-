
import pandas as pd
import numpy as np

df = pd.read_csv("Data\Airports\AirportsLongLat.csv")

LongitudeAirport=round(df["lon"],1)
Name_of_Airport=df["city"]
LongitudeAirportlist=[]
Name_of_Airportlist=[]

print(LongitudeAirport)
for i in range(28256):
    LongitudeAirportlist.append(LongitudeAirport[i])
    Name_of_Airportlist.append(Name_of_Airport[i])


AirportDicto=dict(zip(LongitudeAirportlist, Name_of_Airportlist))

