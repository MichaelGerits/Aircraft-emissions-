import pandas # data loading in, reads csv files quickly and easily
import openap
#import fastmeteo
import matplotlib
#import seaborn
#import cartopy

#import haversine as hs   
#from haversine import Unit



df = pandas.read_csv("Data/Route_2003.csv")
print(df.head())  