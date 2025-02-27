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
import seaborn as sns


# File paths
las_fname = (Path.cwd()).parent.parent.joinpath(r'USGS_LPC_FL_Peninsular_FDEM_2018_D19_DRRA_LID2019_218755_E.laz')

#%% Defining Funcs
def get_las_crs(las_df) -> CRS:
    las_crs = CRS.from_wkt(str(las_df.header.parse_crs())).sub_crs_list[0].to_epsg()
    
    return las_crs

def proj_las(las_df, input_crs, ouput_crs) -> np.array:
    start = time.time()
    #Checking Coordinate System
    if input_crs == ouput_crs:
        pass
    else:
        transformer = Transformer.from_crs(input_crs, ouput_crs, always_xy=True)

        # Get the x, y, and z coordinates 
        las_x = las_df.x.copy()
        las_y = las_df.y.copy()
        las_z = las_df.z.copy()

        #Chunking
        chunk_size = 100000
        for i in range(0,len(las_df), chunk_size):

            chunk_x = las_df.x[i:i + chunk_size]
            chunk_y = las_df.y[i:i + chunk_size]
            chunk_z = las_df.z[i:i + chunk_size]
            
            #Projecting
            projected_x, projected_y, projected_z = transformer.transform(chunk_x, chunk_y, chunk_z)

            las_x[i:i + chunk_size] = projected_x
            las_y[i:i + chunk_size] = projected_y
            las_z[i:i + chunk_size] = projected_z

        #Replacing vals
        las_df.x = las_x.astype(np.float64)
        las_df.y = las_y.astype(np.float64)
        las_df.z = las_z.astype(np.float64)


    ##Bools for Values
    x_valid = (las_df.x >= minx) & (las_df.x <= maxx)
    y_valid = (las_df.y >= miny) & (las_df.y <= maxy)

    #combined Bools
    valid_points = x_valid & y_valid

    ## Clipping and Converting to Numpy Array
    las_array = np.vstack((las_x, 
                        las_y, 
                        las_z)
                        ,dtype='float64').transpose()

    #Clipping 
    las_array_clipped = las_array[valid_points]
    end = time.time()
    print(f'Elapsed Time {end-start}')

    return las_array_clipped

#%% Opening the las data
##Reading all data
las_df = laspy.read(las_fname)

#Figuring out the projection
las_crs = CRS.from_wkt(str(las_df.header.parse_crs())).sub_crs_list[0].to_epsg()
proj = las_crs

##Reading only the ground return points
las_ground_df = las_df.points[las_df.classification==2] #where 2 is ground

#Extent
las_df_extent = [las_df.x.min,las_df.x.max,
                 las_df.y.min, las_df.y.max ]
# print(las_df_extent)    #[minx, miny, minz], [maxx, maxy, maxz]


#Checking CRS
# las_df.header.parse_crs()


#%% Create Shapefile to Cut Las Dataset
start = time.time()
## Formating the bounds
#Reading the box
fishnet_fname = (Path.cwd()).parents[1].joinpath(r'Emmett_Reed_Fishnet.json')
box = gp.read_file(fishnet_fname).dissolve()
#Projecting the box
box_coord_syst = box.crs

#Getting bounds
minx, miny, maxx, maxy = box.total_bounds
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
    las_ground_df.x = las_x.astype(np.float64)
    las_ground_df.y = las_y.astype(np.float64)
    las_ground_df.z = las_z.astype(np.float64)


##Bools for Values
x_valid = (las_ground_df.x >= minx) & (las_ground_df.x <= maxx)
y_valid = (las_ground_df.y >= miny) & (las_ground_df.y <= maxy)

#combined Bools
valid_points = x_valid & y_valid

## Clipping and Converting to Numpy Array
#Creating array
# las_array = np.vstack((las_ground_df.x, 
#                        las_ground_df.y, 
#                        las_ground_df.z)
#                       ,dtype='float64').transpose()
las_array = np.vstack((las_x, 
                       las_y, 
                       las_z)
                      ,dtype='float64').transpose()

#Clipping 
las_array_clipped = las_array[valid_points]
end = time.time()
print(f'Elapsed Time {end-start}')

#%% Working with the Cropped LAS file
##What are some statistics on the Elevation?
#Numpy Array
las_elev_array = las_array_clipped[:,2]

##Stats
#3 num summary
min_elev = np.min(las_elev_array)
mean_elev = np.average(las_elev_array)
max_elev = np.max(las_elev_array)
sd = np.std(las_elev_array)

#Quantiles
# perc_5 = np.percentile(las_elev_array, 1)
# q1 = np.percentile(las_elev_array, 25)
perc_5 = np.quantile(las_elev_array, .01)
quantile_1 = np.quantile(las_elev_array, .25)

#A 3 Z-score for outside the 97.5%
threshold = ((-3*sd) + mean_elev)

#Histogram
# sns.histplot(las_elev_array, stat='count')
sns.histplot(las_elev_array[np.where(las_elev_array<perc_5)], stat='frequency')
#%% Tag Points Greater than 75th percentile
#Cloud points greater than the q4 value
las_array_filt = las_array_clipped[np.where(las_array_clipped[:,2] < threshold)]

#Manually select
las_array_filt = las_array_clipped[np.where(las_array_clipped[:,2] < perc_5)]
las_df_filt = las_df.points[las_df.z<=perc_5] #where 2 is ground
#%% Write to las
start = time.time()

##Writing
writ_path = (Path.cwd()).parent.parent.joinpath(r'Filt_USGS_LPC_FL_Peninsular_FDEM_2018_D19_DRRA_LID2019_218755_E.las')
if os.path.exists(writ_path):
    print('File Exists')
else:
    print('File Doesnt exist, writing')

    #Ripping Header
    header = las_df.header

    #Opening Writer
    with laspy.open(writ_path, mode='w', header=header) as wr:
    
        point_record = laspy.ScaleAwarePointRecord.zeros(las_array_filt.shape[0], header=header)
        point_record.x = las_array_filt[:,0]
        point_record.y = las_array_filt[:,1]
        point_record.z = las_array_filt[:,2]
        
        #Writing
        wr.write_points(las_df_filt)

end = time.time()
print(f'Elapsed Time {end-start}')