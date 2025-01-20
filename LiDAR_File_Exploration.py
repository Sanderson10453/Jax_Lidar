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
las_fname = Path.cwd().joinpath(r'USGS_LPC_FL_Peninsular_FDEM_2018_D19_DRRA_LID2019_218755_E.laz')
#%% Opening the las data
##Reading all data
las_df = laspy.read(las_fname)

##Reading only the ground return points
las_ground_df = las_df.points[las_df.classification==2] #where 2 is ground

## Enpty Array
las_array = np.vstack((las_ground_df.x, las_ground_df.y, las_ground_df.z)).transpose()

#%% Plotting
fig = plt.figure()
ax = fig.add_subplot(projection = '3d')
ax.scatter(las_ground_df.x, las_ground_df.y, las_ground_df.z)
plt.show()