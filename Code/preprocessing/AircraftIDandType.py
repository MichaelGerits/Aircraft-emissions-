
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


#importing the Aircraft ID (the eurocontrol number and the aircraft type)
#Setting up the Dictionary between the eurocontrol number and aircraft type.  
df = pd.read_csv("Data\planedata\Aircraft ID.csv")
AircraftDictionary_Eurocontrol_and_Aircraft = df.set_index(['ECTRL ID'])[('AC Type')].to_dict()

#This setups a dictionary with equal planes 
aircraft_dict = {
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


