#import haversine as hs   
#from haversine import Unit
#using this method it is possible to calculate the distance between two point using (longitude and lattitude)

#lyon = (45.7597, 4.8422) # (lat, lon)
#paris = (48.8567, 2.3508)

#print(hs.haversine(lyon, paris))

import pandas as pd # data loading in, reads csv files quickly and easily
import matplotlib as mpl
import openap
ECTLR = pd.read_csv("Data\Aircraft ID.csv", usecols=['ECTRL ID'])
ACtype = pd.read_csv("Data\Aircraft ID.csv", usecols=[ 'AC Type'])
print(ACtype)


