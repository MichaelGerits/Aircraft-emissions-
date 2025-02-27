from AircraftIDandType import AircraftDictionary_Eurocontrol_and_Aircraft 
import pandas as pd
from preProcess import extract_ECTRLIDSeq 



print(extract_ECTRLIDSeq("Data\positions")[-1][238925257])

