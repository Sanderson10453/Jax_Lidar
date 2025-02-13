#%% Import modules

#Path
from pathlib import Path
import os

#Geospatial
import geopandas as gp
import laspy
from pyproj import CRS, Transformer

#Numpy
import numpy as np

#Timing
import time

#Plotting
import matplotlib.pyplot as plt


# File paths
las_fname = (Path.cwd()).parent.parent.joinpath(r'USGS_LPC_FL_Peninsular_FDEM_2018_D19_DRRA_LID2019_218755_E.laz')
#%% Opening the las data
##Reading all data
las_df = laspy.read(las_fname)
proj = CRS(6437)
##Reading only the ground return points
las_ground_df = las_df.points[las_df.classification==2] #where 2 is ground

#Extent
las_df_extent = [las_df.header.min,las_df.header.max]
print(las_df_extent)    #[minx, miny, minz], [maxx, maxy, maxz]

## Enpty Array
las_array = np.vstack((las_ground_df.x, las_ground_df.y, las_ground_df.z)).transpose()


#%% Create Shapefile to Cut Las Dataset
start = time.time()
## Reading the box
fishnet_fname = (Path.cwd()).parents[1].joinpath(r'Emmett_Reed_Fishnet.json')
box = gp.read_file(fishnet_fname).dissolve()
box_coord_syst = box.crs
print(box_coord_syst)
box_np = box.to_numpy()

#Checking Coordinate System
if proj == box_coord_syst:
    pass
else:
    transformer = Transformer.from_crs(proj, box_coord_syst, always_xy=True)

    # Get the x, y, and z coordinates 
    las_x = las_ground_df.x.copy()
    las_y = las_ground_df.y.copy()
    las_z = las_ground_df.z.copy()

    #Chunking
    chunk_size = 100000
    for i in range(0,len(las_ground_df), chunk_size):

        chunk_x = las_ground_df.x[i:i + chunk_size]
        chunk_y = las_ground_df.y[i:i + chunk_size]
        chunk_z = las_ground_df.z[i:i + chunk_size]
        
        #Projecting
        projected_x, projected_y, projected_z = transformer.transform(chunk_x, chunk_y, chunk_z)

        las_x[i:i + chunk_size] = projected_x
        las_y[i:i + chunk_size] = projected_y
        las_z[i:i + chunk_size] = projected_z

        #Replacing vals
        las_ground_df.x = las_x
        las_ground_df.y = las_y
        las_ground_df.z = las_z

    # Transform the coordinates
    lat, lon, elev = transformer.transform(las_x, las_y, las_z) 
end = time.time()
print(f'Elapsed Time {end-start}')


