
import pandas as pd
import numpy as np

df = pd.read_csv("Data\Airports\AirportsLongLat.csv")

LongitudeAirport=round(df["lon"],0)
LatAirport=round(df["lat"],0)
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

coordinates = {} # initializes an empty dictionary
n = 2
Aiport_Classifier = {}
for i in range(28256):
    key = LongitudeAirport[i]
    key1=LatAirport[i]
    value = Name_of_Airport[i]
    Aiport_Classifier.update({(key,key1): value})
print(Aiport_Classifier)

print(Aiport_Classifier[140.0, -6.0])