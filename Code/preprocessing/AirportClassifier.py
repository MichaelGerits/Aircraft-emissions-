
import pandas as pd
import numpy as np
df = pd.read_csv("Data\Airports\AirportsLongLat.csv")
LongitudeAirport=round(df["lon"],1)
LatAirport=round(df["lat"],1)
Name_of_Airport=df["city"]
LongitudeAirportlist=[]
Name_of_Airportlist=[]
LattitudeAirportlist=[]
ID=[]

Aiport_Classifier = {}
for i in range(28256):
    key = LongitudeAirport[i]
    key1=LatAirport[i]
    value = Name_of_Airport[i]
    Aiport_Classifier.update({(key,key1): value})

print(Aiport_Classifier[round(8.54313,1),round(50.0264,1)])
