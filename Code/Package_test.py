import pandas # data loading in, reads csv files quickly and easily

#import OpenAP
#import fastmeteo
import matplotlib
#import seaborn
#import cartopy

df = pandas.read_csv("Data/Route_2003.csv")
print(df.head())