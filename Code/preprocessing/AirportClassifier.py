
import pandas as pd
import numpy as np
df = pd.read_csv("Data\Airports\AirportsLongLat.csv")
LongitudeAirport=np.ceil(df["lon"])
LatAirport=np.floor(df["lat"])
Name_of_Airport=df["city"]
LongitudeAirportlist=[]
Name_of_Airportlist=[]
LattitudeAirportlist=[]
ID=[]

Aiport_Classifier = {}
for i in range(len(LongitudeAirport)):
    key = LongitudeAirport[i]
    key1=LatAirport[i]
    value = Name_of_Airport[i]
    Aiport_Classifier.update({(key,key1): value})

