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
from openap import (
    Drag,
    Thrust,
    WRAP,
    FlightPhase,
    FlightGenerator,
    FuelFlow,
    Emission,
)
from openap import prop
from pprint import pprint
AircraftID = pd.read_csv("Data\Aircraft ID.csv", usecols=['ECTRL ID','AC Type'])
ECTRL = pd.read_csv("Data\Aircraft ID.csv", usecols=['ECTRL ID'])
ACType = pd.read_csv("Data\Aircraft ID.csv", usecols=['AC Type'])
AircraftID['AC Type'] = AircraftID['AC Type'].str.lower()

#AircraftID_cleaned = AircraftID.drop_duplicates()
#AircraftID_cleaned.to_csv("Data\Aircraft_ID_Cleaned.csv", index=False)

AircraftTypes = ACType.drop_duplicates()
#AircraftTypes.to_csv("Data\Aircraft_types.csv", index=False)

df = pd.read_csv("Data\Aircraft_ID_Cleaned.csv")
AircraftDictionary = df.set_index(['ECTRL ID'])[('AC Type')].to_dict()

avaiable_aircraft = prop.available_aircraft()

#print(f"Supports {len(avaiable_aircraft)} aircraft types")
print(avaiable_aircraft)
def get_aircraft_dictionary():
    return {
        "A20N": "a20n",
        "A21N": "a21n",
        "A318": "a318",
        "A319": "a319",
        "A320": "a320",
        "A321": "a321",
        "A332": "a332",
        "A310": "a332",
        "A306": "a332",
        "A339": "a333",
        "A333": "a333",
        "A343": "a343",
        "A346": "a343",
        "A35K": "a359",
        "A359": "a359",
        "A388": "a388",
        "B734": "b734",
        "B735": "b734",
        "B733": "b734",
        "B736": "b737",
        "B737": "b737",
        "B738": "b738",
        "B744": "b744",
        "B743": "b744",
        "B748": "b748",
        "B752": "b752",
        "B763": "b763",
        "B772": "b772",
        "B77L": "b77w",
        "B77W": "b77w",
        "B78X": "b788",
        "B788": "b788",
        "B789": "b789",
        "C510": "c550",
        "E170": "e170",
        "E190": "e190",
        "E195": "e195",
        "E290": "e195",
        "E75L": "e75l",
        "GLF6": "glf6"
    }
print(get_aircraft_dictionary['A20N'])
