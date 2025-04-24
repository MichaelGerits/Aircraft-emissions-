
import pandas as pd
import numpy as np
df = pd.read_csv("Data\Airports\AirportsLongLat.csv")
LatAirport=df["lat"]
LongitudeAirport=df["lon"]
Name_of_Airport=df["city"]
LongitudeAirportlist=[]
Name_of_Airportlist=[]
LattitudeAirportlist=[]
ID=[]

Aiport_Classifier = {}
for i in range(len(LongitudeAirport)):
    key=np.ceil(LatAirport[i] * 1e1)
    key1 = np.floor(LongitudeAirport[i] * 1e1)
    value = Name_of_Airport[i]
    Aiport_Classifier.update({(key,key1): value})

#print(Aiport_Classifier[(501,85)])
#50.03333,8.57056 => Frankfurt

#51.5183,7.61224 => dortmund

