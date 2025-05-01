import pandas as pd
import os
from openap import FuelFlow, Emission
import matplotlib.pyplot as plt
import numpy as np
import sys
import csv

from tqdm import tqdm

#adds the Code directory to the path for modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#custom modules
from preprocessing.preProcess import extract_ECTRLIDSeq
from preprocessing.AircraftIDandType import AircraftDictionary_Eurocontrol_and_Aircraft 
from preprocessing.AirportClassifier import Aiport_Classifier
from preprocessing.AircraftIDandType import aircraft_dict 
from preprocessing.AircraftIDandType import aircraft_dict_mass


#############################################################################################################################################################
#Make a class for a flight

class Flight:
    def __init__(self, EURCTRLID, Data):
        """Initialize a Flight object with minimal picklable attributes."""
        self.CO2, self.H2O, self.NOx, self.HC, self.CO = [None] * 5
        self.CO2rate, self.H2Orate, self.NOxrate, self.HCrate, self.COrate = [None] * 5
        self.ID = EURCTRLID

        # Check if aircraft type is supported
        type_raw = AircraftDictionary_Eurocontrol_and_Aircraft.get(EURCTRLID)
        if type_raw not in aircraft_dict:
            raise ValueError(f"Aircraft: {type_raw} not supported")

        self.type = aircraft_dict[type_raw]
        self.mass = aircraft_dict_mass[self.type]

        # Store flight data
        self.flightData = Data[self.ID].drop_duplicates(subset=['Time Over']).reset_index(drop=True)

        # Compute initial parameters
        self.airports = self.Findairports(init=False)
        self.time_diffs = self.calcTimeDiffs()
        self.time_cum = np.cumsum(self.time_diffs)
        self.DistHor = self.calcDistHorizontal()
        self.alts = np.array(self.flightData['Flight Level']) * 100
        self.DistVert = self.calcDistVertical()
        self.spdHor = self.calcSpdHorizontal()
        self.spdVert = self.calcSpdVertical()

        # Fuel Flow & Emission objects are NOT initialized here to avoid pickling issues

    def initialize_emission(self):
        """Does the openAP calculations after setting up base parameters."""
        try:
            self.fuelFlow = FuelFlow(ac=self.type)
            self.emission = Emission(ac=self.type)
            self.FF = self.initializeFF()

            self.CO2rate = self.calcCO2Rate() * 1e-6
            self.H2Orate = self.calcH2ORate() * 1e-6
            self.NOxrate = self.calcNOxRate() * 1e-6
            self.COrate = self.calcCORate() * 1e-6
            self.HCrate = self.calcHCRate() * 1e-6

            self.CO2 = self.integrateRate(rate=self.CO2rate)
            self.NOx = self.integrateRate(rate=self.NOxrate)
            self.H2O = self.integrateRate(rate=self.H2Orate)
            self.CO = self.integrateRate(rate=self.COrate)
            self.HC = self.integrateRate(rate=self.HCrate) 
        except RuntimeWarning:
            print("issue during computation")    
        
        ############################################################################
    def __str__(self):
        """Defines how the object is printed with key stats."""
        return f"Flight {self.id} | emissions: {[self.CO2[-1], self.H2O[-1], self.NOx[-1], self.HC[-1], self.CO[-1]]} | Airports: {self.Findairports(init=True)}"
    def calcTimeDiffs(self):
        """
        calculates the timesteps of the flight in seconds

        returns the array AND updates the class variable
        """
        time_diffs = np.array(pd.to_datetime(self.flightData['Time Over'], format="mixed", dayfirst=True).diff().dt.total_seconds().dropna())



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
        rate = np.abs(rate)
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
            fisk=0
            #imports the airports using the coordinates from depature and arrival
            lat_deg=np.array(self.flightData['Latitude'])
            lon_deg=np.array(self.flightData['Longitude'])
            if init==False:
                print("The aircraft depatured from",Aiport_Classifier[(lat_deg[0],lon_deg[0])], "and arrived at",Aiport_Classifier[(lat_deg[-1],lon_deg[-1])]) 
            return [Aiport_Classifier[np.ceil(lat_deg[0]*1e1),np.floor(lon_deg[0]*1e1)],Aiport_Classifier[np.ceil(lat_deg[-1]*1e1),np.floor(lon_deg[-1]*1e1)],[float(lat_deg[0]),float(lon_deg[0])],[float(lat_deg[-1]),float(lon_deg[-1])]]
            #imports the airports using the coordinates from depature and arrival
        except KeyError:
            fisk=1
            return [None, None, None, None]
        except UnicodeEncodeError:
            print("fisk")
        if fisk==1:
            try:
                lat_deg=np.array(self.flightData['Latitude']+0.1)
                lon_deg=np.array(self.flightData['Longitude']+0.1)
                return [Aiport_Classifier[(np.round(lon_deg[0],1),np.round(lat_deg[0],1))],Aiport_Classifier[(np.round(lon_deg[-1],1),np.round(lat_deg[-1],1))],[lon_deg[0],lat_deg[0]],[lon_deg[-1],lat_deg[-1]]]
            except KeyError:
                return [None, None, None, None]

  
        
    def Haul(self):
        if np.sum(self.DistHor) < 1500000:
            return("Short-haul flight")
        elif np.sum(self.DistHor) >= 3000000:
            return("Long-haul flight")
        else:
            return("Medium-haul flight")
        
def create_flight(EURCTRLID, Data, string):
    """Helper function for multiprocessing to create a Flight object."""
    
    try:
        #print("initializing ", EURCTRLID)
        flight = Flight(EURCTRLID, Data) #initializes the object
        flight.initialize_emission()  # does the calculation
        with open(string, 'a', newline='',encoding="utf-8") as file:
            writer = csv.writer(file)
            row_list=[flight.ID,flight.type,flight.Findairports(init=True)[0],flight.Findairports(init=True)[1],flight.Findairports(init=True)[2],flight.Findairports(init=True)[3],flight.CO2[-1],flight.NOx[-1],flight.time_cum[-1],round(np.sum(flight.calcDistHorizontal()),0),flight.Haul(),np.array(flight.flightData['Time Over'])[0],np.array(flight.flightData['Time Over'])[-1]]
            writer.writerow(row_list)

    except ValueError as e:
        print(e)
        flight = None
  
    except RuntimeWarning:
        print("issue during computation")
        flight= None

    except IndexError:
        print("issue with listindexing")
        flight= None
   

    
        
    return flight
        

def filter_flights_by_coordinates(Data, min_lat, max_lat, min_lon, max_lon):
    print("\n--------------------removing flights out of bounds---------------------")
    print(f"    old dataset length: {len(Data) - 2}")  # Excluding "name" and "keys"

    def is_within_bounds(df):
        """ Check if first or last coordinates are within bounds """
        first_lat, first_lon = df.iloc[0][['Latitude', 'Longitude']]
        last_lat, last_lon = df.iloc[-1][['Latitude', 'Longitude']]
        
        return ((min_lat <= first_lat <= max_lat and min_lon <= first_lon <= max_lon) or
                (min_lat <= last_lat <= max_lat and min_lon <= last_lon <= max_lon))

    # Extract only valid flight IDs, skipping the first and last items ("name" and "keys")
    flight_entries = list(Data.items())[1:-1]  # Skip first ("name") and last ("keys")
    valid_flight_ids = {flight_id for flight_id, df in tqdm(flight_entries, desc="eliminating flights", unit="flight") if is_within_bounds(df)}
    
    # Update "keys" and filter Data dictionary
    Data = {key: Data[key] for key in valid_flight_ids}
    Data["keys"] = list(valid_flight_ids)
    
    print(f"    new dataset length: {len(Data)}")  # Now only valid flights
    print("--------------------done---------------------")
    
    return Data


############################################################################################################################################################

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":

    #Load the data for al the required flights once
    Data = extract_ECTRLIDSeq('Data\PositionData\FPA202109')
    outputloc = 'Data\Outputdata/202109.csv'


    fil=True #decide if you want to go through the filtering process or not
    if fil==True:
        print("\n--------------------removing invalid aircraft types---------------------")
        print(f"    old dataset length: {len(Data)-2}")

        # Convert aircraft_dict keys to a set for faster lookups
        valid_types = set(aircraft_dict.keys())

        # Get invalid IDs in a set for fast lookups
        invalid_IDs = {id for id, type in AircraftDictionary_Eurocontrol_and_Aircraft.items() if type not in valid_types}

        # Filter Data["keys"] in one go
        Data["keys"] = [ID for ID in Data["keys"] if ID not in invalid_IDs]

        # Use dictionary comprehension to remove invalid entries
        Data = {key: value for key, value in Data.items() if key not in invalid_IDs}

        print(f"    new dataset length: {len(Data)-2}")
        print("--------------------done---------------------")

        Data = filter_flights_by_coordinates(Data=Data, min_lat=37.623, max_lat=69.896, min_lon=-23.723, max_lon=31.823)

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------
    print(f"--------------------initializing {len(Data)-2} flights ---------------------")
    
    with open(outputloc, 'w', newline='') as file:
        writer = csv.writer(file)
        row_list = [
            ["EurocontrolID","Plane", "Dep","Arr", "Dep(start-coordinates)", "Arr(end-coordinates)","CO2","NOX","Time","Distance","Haul","Start-Date","End-date"],  
        ]
        writer.writerows(row_list)
    
    


    flights = []
    for ID in tqdm(Data["keys"], desc="Initializing objects", unit="flight"):
        obj = create_flight(ID, Data, outputloc)
        flights.append(obj)
    

    # Filter out None values
    flights = [f for f in flights if f is not None]

    print("--------------------done---------------------")
    print("error")

    #--------------------------------------------------------------------------------------------
   

    #flights[0].plotEmissionData(tot=False)
    #print(flights[0].time_cum, flights[0].time_diffs)

 
