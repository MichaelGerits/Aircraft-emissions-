
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

Aiport_Classifier = {}
for i in range(28256):
    key = LongitudeAirport[i]
    key1=LatAirport[i]
    value = Name_of_Airport[i]
    Aiport_Classifier.update({(key,key1): value})

