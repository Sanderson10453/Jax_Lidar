#%% Import modules

#Path
from pathlib import Path
import os

#Geospatial
import geopandas as gp
import laspy

#Numpy
import numpy as np


#Plotting
import matplotlib.pyplot as plt


# File paths
las_fname = (Path.cwd()).parent.parent.joinpath(r'USGS_LPC_FL_Peninsular_FDEM_2018_D19_DRRA_LID2019_218755_E.laz')
#%% Opening the las data
##Reading all data
las_df = laspy.read(las_fname)
print(las_df.header.parse_crs)
##Reading only the ground return points
las_ground_df = las_df.points[las_df.classification==2] #where 2 is ground

## Enpty Array
las_array = np.vstack((las_ground_df.x, las_ground_df.y, las_ground_df.z)).transpose()


#%% Create Shapefile to Cut Las Dataset
## Reading the box
fishnet_fname = (Path.cwd()).parents[1].joinpath(r'Emmett_Reed_Fishnet.json')
box = gp.read_file(fishnet_fname).dissolve()
box_np = box.to_numpy()

#Box Boundaries
minx, miny, maxx, maxy = box.total_bounds
length = box.length
height= box.area/box.length

## Cutting the las dataset
x_valid = (las_array[:, 0] >= minx) & (las_array[:, 0] <= maxx)
y_valid = (las_array[:, 1] >= miny) & (las_array[:, 1] <= maxy)


#Combining Bools
valid_points = x_valid & y_valid

las_array_filt = las_array[valid_points]
box
#%% Plotting - Bad way to plot
# fig = plt.figure()
# ax = fig.add_subplot(projection = '3d')
# ax.scatter(las_ground_df.x, las_ground_df.y, las_ground_df.z)
# plt.show()

