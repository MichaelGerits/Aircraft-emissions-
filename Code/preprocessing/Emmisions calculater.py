from AircraftIDandType import AircraftDictionary_Eurocontrol_and_Aircraft 
import pandas as pd
from preProcess import extract_ECTRLIDSeq 
from openap import FuelFlow, Emission

fuelflow = FuelFlow(ac="A320")
emission = Emission(ac="A320")

TAS = 350
ALT = 30000

FF = fuelflow.enroute(mass=60000, tas=TAS, alt=ALT, vs=0)  # kg/s

CO2 = emission.co2(FF)  # g/s
H2O = emission.h2o(FF)  # g/s
NOx = emission.nox(FF, tas=TAS, alt=ALT)  # g/s
CO = emission.co(FF, tas=TAS, alt=ALT)  # g/s
HC = emission.hc(FF, tas=TAS, alt=ALT)  # g/s


