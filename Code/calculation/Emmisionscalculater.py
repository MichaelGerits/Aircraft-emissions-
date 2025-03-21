import pandas as pd
import os
from openap import FuelFlow, Emission
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from openap.phase import FlightPhase
import tracemalloc
import sys

#adds the Code directory to the path for modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#custom modules
from preprocessing import AirportClassifier, preProcess, AircraftIDandType
from preprocessing.preProcess import extract_ECTRLIDSeq
from preprocessing.AircraftIDandType import AircraftDictionary_Eurocontrol_and_Aircraft #TODO: need to adapt to datafile
from preprocessing.AirportClassifier import Aiport_Classifier
from preprocessing.AircraftIDandType import aircraft_dict 
from preprocessing.AircraftIDandType import aircraft_dict_mass



#Load the data for al the required flights once
Data = extract_ECTRLIDSeq('Data/PositionData/March')

print("--------------------removing invalid aircraft types---------------------")
print(f"old dataset length: {len(Data)}")
# gets a list with eurocontrol id's with that invalid type
invalid_ID = [id for id, type in AircraftDictionary_Eurocontrol_and_Aircraft.items() if type not in list(aircraft_dict.keys())]
#delete flights with that type from data. to increase speed
for ID in invalid_ID:
    if ID in Data["keys"]:
        Data["keys"].remove(ID)
        Data.pop(ID, None)
print(f"new dataset length: {len(Data)}")
print("--------------------done---------------------")


#############################################################################################################################################################
#Make a class for a flight
class Flight:
    def __init__(self, EURCTRLID):
        """
        this initialises certain variables and takes the data relevant to this flight. 
        also drops rows/cleans data
        """
        self.CO2, self.H2O, self.NOx, self.HC, self.CO = [None] * 5
        self.CO2rate, self.H2Orate, self.NOxrate, self.HCrate, self.COrate = [None] * 5
        self.ID = EURCTRLID

        #this if statement catches aircraft types that are not supported by the extended library for openAP
        type_raw = AircraftDictionary_Eurocontrol_and_Aircraft[EURCTRLID]
        if  type_raw not in list(aircraft_dict.keys()):
            raise ValueError(f"Aircraft: {AircraftDictionary_Eurocontrol_and_Aircraft[EURCTRLID]}, not supported")
        
        self.type = aircraft_dict[AircraftDictionary_Eurocontrol_and_Aircraft[EURCTRLID]]
        self.mass = aircraft_dict_mass[self.type]
        self.fuelFlow = FuelFlow(ac=self.type)
        self.emission = Emission(ac=self.type)
        #get the data for the flight
        self.flightData = Data[self.ID]

        #remove rows which have the same datetime (getting rid of duplicates)
        self.flightData = self.flightData.drop_duplicates(subset=['Time Over']).reset_index(drop=True)

        ############### this is the order of steps###############################
        self.airports = self.Findairports(init=True) #find the airports
        self.time_diffs = self.calcTimeDiffs() #list of time steps
        self.time_cum = np.cumsum(self.time_diffs) #list of total time passed
        self.DistHor = self.calcDistHorizontal() #distance steps
        self.alts = np.array(self.flightData['Flight Level'])*100 #gets the altitudes from  FL
        self.DistVert = self.calcDistVertical() #calculates the vertical steps

        self.spdHor = self.calcSpdHorizontal() #returns the horizontal velocities
        self.spdVert = self.calcSpdVertical() #returns the vertical climbrates

        self.FF = self.initializeFF() #returns the fuelflows for all points


        #--------------------------------------------------------------------------------------------------------------------------------------
        self.CO2rate = self.calcCO2Rate() * 1e-6
        self.H2Orate = self.calcH2ORate() * 1e-6
        self.NOxrate = self.calcNOxRate() * 1e-6
        self.COrate = self.calcCORate() * 1e-6
        self.HCrate = self.calcHCRate() * 1e-6

        #calculates the total emission in tons
        self.CO2 = self.integrateRate(rate=self.CO2rate) 
        self.NOx = self.integrateRate(rate=self.NOxrate) 
        self.H2O = self.integrateRate(rate=self.H2Orate) 
        self.CO = self.integrateRate(rate=self.COrate) 
        self.HC = self.integrateRate(rate=self.HCrate) 
        
        
        ############################################################################

    def calcTimeDiffs(self):
        """
        calculates the timesteps of the flight in seconds

        returns the array AND updates the class variable
        """
        time_diffs = np.array(pd.to_datetime(self.flightData['Time Over'], format='mixed').diff().dt.total_seconds().dropna())
        #format="%d/%m/%Y %H:%M"
        return time_diffs
    
    def calcDistHorizontal(self, R = 6371000):
        """
        calculates the horizontal distance flown using the haversine function
        need the angular coordinates and a radius (standard earth radius)

        haversine: https://en.wikipedia.org/wiki/Haversine_formula

        returns the array AND updates the class variable (m)
        """
        # Convert degrees to radians for calculation
        lat_rad = np.radians(np.array(self.flightData['Latitude']))
        lon_rad = np.radians(np.array(self.flightData['Longitude']))

        # Compute Haversine formula for distance between consecutive points
        dlat = np.diff(lat_rad)
        dlon = np.diff(lon_rad)

        a = np.sin(dlat / 2) ** 2 + np.cos(lat_rad[:-1]) * np.cos(lat_rad[1:]) * np.sin(dlon / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        # Compute distances in meters
        DistHor = (R * c)

        return DistHor
    
    def calcDistVertical(self):
        """
        calculates the distance steps vertically using the recorded flightlevels (ft)
        """
        DistVert = np.diff(self.alts)
        return DistVert
    
    def calcSpdHorizontal(self):
        """
        calculates the horizontal speed of the flights in knots

        for now we assume that this groundspeed is close enough to the TAS
        """
        spdHor = self.DistHor / self.time_diffs * 1.943844

        return spdHor
    
    def calcSpdVertical(self):
        """
        calculates the horizontal speed of the flights in ft/min
        """
        spdVert = self.DistVert / self.time_diffs * 60

        return spdVert

    def initializeFF(self):
        """
        initializes an array of fuel flow objects for each datapoint
        """
        FFArr = np.abs(np.array([self.fuelFlow.enroute(mass=self.mass, tas=spdHor, alt=alt, vs=spdVert) 
                          for spdHor, alt, spdVert in zip(self.spdHor, np.array(self.flightData['Flight Level'])[1:]*100, self.spdVert)]))
        return FFArr
    
    def calcCO2Rate(self):
        """
        returns an array with the emission rate
        """
        CO2rate = np.array([self.emission.co2(FF) 
                          for FF in self.FF])
        return CO2rate
    
    def calcH2ORate(self):
        """
        returns an array with the emission rate
        """
        H2Orate = np.array([self.emission.h2o(FF) 
                          for FF in self.FF])
        return H2Orate
    
    def calcNOxRate(self):
        """
        returns an array with the emission rate
        """
        NOxrate = np.array([self.emission.nox(FF, tas=spdHor, alt=alt) 
                          for FF, spdHor, alt in zip(self.FF, self.spdHor, np.array(self.flightData['Flight Level'])[1:]*100)])
        return NOxrate
    
    def calcCORate(self):
        """
        returns an array with the emission rate
        """
        COrate = np.array([self.emission.co(FF, tas=spdHor, alt=alt) 
                          for FF, spdHor, alt in zip(self.FF, self.spdHor, np.array(self.flightData['Flight Level'])[1:]*100)])
        return COrate
    
    def calcHCRate(self):
        """
        returns an array with the emission rate
        """
        HCrate = np.array([self.emission.hc(FF, tas=spdHor, alt=alt) 
                          for FF, spdHor, alt in zip(self.FF, self.spdHor, np.array(self.flightData['Flight Level'])[1:]*100)])
        return HCrate
    
    def integrateRate(self, rate, init=0):
        """
        a wrapper for integrating the rates, different methods of integrations can be added here
        the integration will be done in tons
        """
        arr = np.zeros(len(rate))  # Same size as velocity

        # Compute trapezoidal integration step by step
        for i in range(1, len(rate)):  # Start from 1 since first position is 0
            arr[i] = arr[i-1] + 0.5 * (rate[i-1] + rate[i]) * self.time_diffs[i-1]
        return arr
    
    def plotFlightData(self, x=[]):
        """
        plots the flightpoint data after minimal processing
        """
        if len(x)==0:
            x=self.time_cum

        plt.subplot(321)
        plt.scatter(x, self.alts[1:], marker=".", color='green', lw=0)
        plt.ylabel("altitude (ft)")

        plt.subplot(322)
        plt.scatter(x, np.cumsum(self.DistHor), marker=".",color='pink', lw=0)
        plt.ylabel("dist horizontal(steps) m")

        plt.subplot(323)
        plt.scatter(x, self.spdHor, marker=".",color='blue', lw=0)
        plt.ylabel("speed (knots)")

        plt.subplot(324)
        plt.scatter(x, self.spdVert, marker=".",color='red', lw=0)
        plt.ylabel("roc (fpm)")

        plt.subplot(325)
        plt.scatter(x, self.FF, marker=".",color='black', lw=0)
        plt.ylabel("FuelFlow (kg/s)")

        plt.show()
        return
    
    def plotEmissionData(self, x=[], tot=True):
        """
        plots the emission in function of the input
        if tot is true => plots the cumulative data
        if tot=False => plots the rates
        """
        if len(x)==0:
            x=self.time_cum
        if tot==True:
            vals = [self.CO2, self.H2O, self.NOx, self.HC, self.CO]
        else:
            vals = [self.CO2rate, self.H2Orate, self.NOxrate, self.HCrate, self.COrate]

        plt.subplot(321)
        plt.scatter(x, vals[0], marker=".", color='green', lw=0)
        plt.ylabel("CO2")

        plt.subplot(322)
        plt.scatter(x, vals[1], marker=".",color='pink', lw=0)
        plt.ylabel("H20")

        plt.subplot(323)
        plt.scatter(x, vals[2], marker=".",color='blue', lw=0)
        plt.ylabel("Nox")

        plt.subplot(324)
        plt.scatter(x, vals[3], marker=".",color='red', lw=0)
        plt.ylabel("CO")

        plt.subplot(325)
        plt.scatter(x, vals[4], marker=".",color='black', lw=0)
        plt.ylabel("Hydrocarbons")

        plt.show()
        return

    def plotGlobe(self):
        """
        plots a globe of the flight
        """
        lat_rad = np.radians(self.flightData['Latitude'])
        lon_rad = np.radians(self.flightData['Longitude'])

        radius = 1
        x = radius * np.cos(lat_rad) * np.cos(lon_rad)
        y = radius * np.cos(lat_rad) * np.sin(lon_rad)
        z = radius * np.sin(lat_rad)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x, y, z, c='b', marker='o')

        u, v = np.mgrid[0:2 * np.pi:100j, 0:np.pi:50j]
        xs = np.cos(u) * np.sin(v)
        ys = np.sin(u) * np.sin(v)
        zs = np.cos(v)

        ax.plot_wireframe(xs, ys, zs, color='lightgray', alpha=0.5)
        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        ax.set_zlabel('Z Axis')
        ax.set_box_aspect([1,1,1])  # Equal aspect ratio
        plt.show()


    def Findairports(self, init=False):
        try:
            lat_deg=np.round(np.array(self.flightData['Latitude']),0)
            lon_deg=np.round(np.array(self.flightData['Longitude']),0)
            if init==False:
                print("The aircraft depatured from",Aiport_Classifier[(lon_deg[0],lat_deg[0])], "and arrived at",Aiport_Classifier[(lon_deg[-1],lat_deg[-1])]) 
            return (1,1)
            #imports the airports using the coordinates from depature and arrival
        except KeyError:
            pass
    def Haul(self):
        print(self.DistHor[-1])
        if self.DistHor[-1] < 1.500:
            return("Short-haul flight")
        elif self.DistHor[-1] >= 3000:
            return("Long-haul flight")
        else:
            return("Medium-haul flight")
        
 

        
############################################################################################################################################################

#test = Flight(238925251)
#test.Findairports()
#test.plotEmissionData(np.cumsum(test.DistHor), tot=False)
#test.plotGlobe()

#-------------------------------------------------------------------------------------------
flights = []
print("--------------------initializing flights---------------------")
for id in Data["keys"]:
    '''
    Gets a list with all the valid flights
    -eliminates invalid types
    -other eliminations
    '''
    try:
        print(f"initializing flight: {id}")
        obj = Flight(id)
        flights.append(obj)  # Only adds if successful
    except ValueError as error:
        print(error)  # Handles the error and continues
print("--------------------done---------------------")
#--------------------------------------------------------------------------------------------
for fl in flights:
    fl.Findairports()
    print(fl.ID)

