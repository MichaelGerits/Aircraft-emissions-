#import haversine as hs   
#from haversine import Unit
#using this method it is possible to calculate the distance between two point using (longitude and lattitude)

#lyon = (45.7597, 4.8422) # (lat, lon)
#paris = (48.8567, 2.3508)

#print(hs.haversine(lyon, paris))

import pandas as pd # data loading in, reads csv files quickly and easily
import matplotlib as mpl
import openap
from csv import DictReader
AircraftID = pd.read_csv("Data\Aircraft ID.csv", usecols=['ECTRL ID','AC Type'])
ECTRL = pd.read_csv("Data\Aircraft ID.csv", usecols=['ECTRL ID'])
ACType = pd.read_csv("Data\Aircraft ID.csv", usecols=['AC Type'])
AircraftID_cleaned = AircraftID.drop_duplicates()
AircraftID_cleaned.to_csv("Data\Aircraft_ID_Cleaned.csv", index=False)

df = pd.read_csv("Data\Aircraft_ID_Cleaned.csv")
AircraftDictionary = df.set_index(['ECTRL ID'])['AC Type'].to_dict()


print(AircraftDictionary)
