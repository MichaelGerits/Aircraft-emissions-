
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
    prop
)
from openap import prop
from pprint import pprint


#importing the Aircraft ID (the eurocontrol number and the aircraft type)
#Setting up the Dictionary between the eurocontrol number and aircraft type.  
df = pd.read_csv("Data\AircraftData\March\Aircraft ID.csv")
AircraftDictionary_Eurocontrol_and_Aircraft= df.set_index(['ECTRL ID'])[('AC Type')].to_dict()

#This setups a dictionary with equal planes 
aircraft_dict = {
    "A20N": "a20n",
    "A21N": "a20n",
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
    "B739": "b738",
    "B744": "b744",
    "B743": "b744",
    "B748": "b748",
    "B752": "b752",
    "B763": "b752",
    "B764": "b752",
    "B767": "b752",
    "B772": "b772",
    "B77L": "b77w",
    "B77W": "b77w",
    "B78X": "b788",
    "b78x": "b788",
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

#This setups a dictionary with the masses of airplanes 

aircraft_dict_mass = {
    "a20n": 75500,
    "a21n": 79000,
    "a318": 97000,
    "a319": 68000,
    "a320": 75500,
    "a321": 90000,
    "a332": 200000,  # A310 and A306 also map to a332, but only one key can exist
    "a333": 220000,  # A339 also maps to a333
    "a343": 300000,  # A343 and A346 both map to a343
    "a359": 220000,  # A35K and A359 both map to a359
    "a388": 560000,
    "b734": 70000,  # B733, B734, and B735 all map to b734
    "b737": 70000,  # B736 also maps to b737
    "b738": 80000,
    "b744": 390000,  # B743 and B744 both map to b744
    "b748": 440000,
    "b752": 59000,
    "b763": 90000,
    "b772": 200000,
    "b77w": 280000,  # B77L and B77W both map to b77w
    "b788": 230000,  # B78X and B788 both map to b788
    "b789": 240000,
    "c550": 6000,
    "e170": 30000,
    "e190": 50000,
    "e195": 50000,  # E195 and E290 both map to e195
    "e75l": 35000,
    "glf6": 45000
}
mass_list = [75500,79000,97000, 68000, 75500,
    78000,
    93500,
    230000,
    242000,
    276000,
    280000,
    560000,
    80000,
    82000,
    88000,
    90000,
    68000,
    70000,
    79000,
    85100,
    396800,
    447700,
    115600,
    158700,
    297000,
    299300,
    351500,
    228000,
    254000,
    6849,
    22000,
    34200,
    50300,
    50790,
    38790,
    45200
]
for i in openap.prop.available_aircraft():
    aircraft = prop.aircraft(i)
    pprint(aircraft["mtow"])

aircraft_mass_data = {
    "format": ["ZFW", "MTOW", "MAX RANGE"],
    "a20n": [mass_list[0]],
    "a21n": [mass_list[1]],
    "a318": [mass_list[2]],
    "a319": [mass_list[3]],
    "a320": [mass_list[4]],
    "a321": [mass_list[5]],
    "a332": [mass_list[6]],  # A310 and A306 also map to a332, but only one key can exist
    "a333": [mass_list[7]],  # A339 also maps to a333
    "a343": [mass_list[8]],  # A343 and A346 both map to a343
    "a359": [mass_list[9]],  # A35K and A359 both map to a359
    "a388": [mass_list[10]],
    "b734": [mass_list[11]],  # B733, B734, and B735 all map to b734
    "b737": [mass_list[12]],  # B736 also maps to b737
    "b738": [mass_list[13]],
    "b744": [mass_list[14]],  # B743 and B744 both map to b744
    "b748": [mass_list[15]],
    "b752": [mass_list[16]],
    "b763": [mass_list[17]],
    "b772": [mass_list[18]],
    "b77w": [mass_list[19]],  # B77L and B77W both map to b77w
    "b788": [mass_list[20]],  # B78X and B788 both map to b788
    "b789": [mass_list[21]],
    "c550": [mass_list[22]],
    "e170": [mass_list[23]],
    "e190": [mass_list[24]],
    "e195": [mass_list[25]],  # E195 and E290 both map to e195
    "e75l": [mass_list[26]],
    "glf6": [mass_list[27]]
}

