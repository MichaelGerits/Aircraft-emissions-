import os #allows to communicate with operating system
import pandas # data loading in, reads csv files quickly and easily
import numpy as np

############################################################################################################################""
def extract_routeIDSeq(Folder):
    '''
    This file loads all the documents in the "Data" folder into a dictionary structure to be used in other files
    the dictionary allows to organise the snippets of the full data with the original file

    runs with datafiles that include routeID and sequence number


    result:

    DB:
        List[
        ->dictionary per data file:
            {name: ....
             full_dat: ....
             (route_id 1): .....
             (route_id 2): .....
             .
             .
             .
             "keys": ["route_id 1", "route_id 2", ....]
             }
            ]
    '''
    
    print("\n\n---------------------------------------------------------------")
    DB = np.array([])
    # iterate over files in
    # that directory
    for filename in os.listdir(Folder):
        print(f'Extracting: {filename}')
        dat = pandas.read_csv(os.path.join(Folder, filename))

        #adds filename and data to database
        DB = np.append(DB,{"name": filename, "full_data": dat})

        #find the rows where a new flight begins
        dat['group'] = (dat['Sequence Number'] == 1).cumsum()

        # Split into multiple DataFrames
        split_dfs = [group.drop(columns=['group']).reset_index(drop=True) for _, group in dat.groupby('group')]

        # Display the split DataFrames
        for flight in split_dfs:
            DB[-1].update({flight['Route ID'][0]: flight})
        DB[-1].update({"keys": list(DB[-1].keys())[2:]})

    print("\n\n-----------Done!!-----------")
    return DB
##################################################################################################################################

def extract_ECTRLIDSeq(Folder):
    '''
   this function will load all the files in a folder 
   (make sure to go as far down as possible)
    then it creates a database for that last folder



    result:

    DB:
        ->dictionary per data file:
            {name: ....
             (ectrl_id 1): .....
             (ectrl_id 2): .....
             .
             .
             .
             "keys": ["ectrl_id 1", "ectrl_id 2", ....]
             }
            
    '''
    
    print("\n\n---------------------------------------------------------------")
    if not os.path.exists(Folder):
        print("Invalid Directory, please check spelling or \,/")
        quit()
    DB = {"name": Folder.split("/")[-1]}
    # iterate over files in
    # that directory
    for filename in os.listdir(Folder):
        print(f'Extracting: {filename}')
        dat = pandas.read_csv(os.path.join(Folder, filename))

        #find the rows where a new flight begins
        dat['group'] = (dat['Sequence Number'] == 0).cumsum()
        print(dat["group"])

        # Split into multiple DataFrames
        split_dfs = [group.drop(columns=['group']).reset_index(drop=True) for _, group in dat.groupby('group')]

        # Display the split DataFrames
        for flight in split_dfs:
            DB.update({int(flight['ECTRL ID'][0]): flight})
    DB.update({"keys": list(DB.keys())[2:]})

    print("\n\n-----------Done!!-----------")
    return DB
##################################################################################################################################

#print(extract_ECTRLIDSeq('Data/PositionData/March')["keys"])





