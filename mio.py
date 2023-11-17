#hls_funcs

#Generalized data and functions for handling HLS data.

import os
import datetime
import glob
import sys
import imageio.v3 as imio
import numpy as np
import math
from imtools import *
import rasterio as rio
import imageio
import matplotlib.pyplot as plt
import io

'''#########################################################################
## General Info
#########################################################################'''

s30_bands = {
    'coastal': 'B01',
    'blue': 'B02',
    'green': 'B03',
    'red': 'B04',
    'RE1': 'B05',
    'RE2': 'B06',
    'RE3': 'B07',
    'NIR_broad': 'B08',
    'NIR_narrow': 'B8A',
    'water_vapor': 'B09',
    'cirrus': 'B10',
    'SWIR1': 'B11',
    'SWIR2': 'B12'}

l30_bands = {
    'coastal': 'B01',
    'blue': 'B02',
    'green': 'B03',
    'red': 'B04',
    'NIR_narrow': 'B05',
    'SWIR1': 'B06',
    'SWIR2': 'B07',
    'cirrus': 'B09',
    'TIR1': 'B10',
    'TIR2': 'B11'}

bands = {'S30': s30_bands, 'L30': l30_bands}
image_band_names = ['B01','B02','B03','B04','B05','B08','B09','B10','B11','B12','B8A']

# Create a LUT dict including the HLS product bands mapped to names
lut = {'HLSS30': {'COASTAL-AEROSOL':'B01', 'BLUE':'B02', 'GREEN':'B03', 'RED':'B04', 'RED-EDGE1':'B05', 'RED-EDGE2':'B06', 'RED-EDGE3':'B07', 'NIR-Broad':'B08', 'NIR1':'B8A', 'WATER-VAPOR':'B09', 'CIRRUS':'B10', 'SWIR1':'B11', 'SWIR2':'B12', 'FMASK':'Fmask'},
       'HLSL30': {'COASTAL-AEROSOL':'B01', 'BLUE':'B02', 'GREEN':'B03', 'RED':'B04', 'NIR1':'B05', 'SWIR1':'B06','SWIR2':'B07', 'CIRRUS':'B09', 'TIR1':'B10', 'TIR2':'B11', 'FMASK':'Fmask'}}

#"Recipes" for various vegetation indices that are commonly used for HLS images
class VI(object):
    NDVI  = lambda NIR,red:        (NIR-red)/(NIR+red)                                             #Normalized Difference Vegetation Index
    EVI   = lambda NIR,red,blue:   2.5*(NIR-red)/(NIR+6.0*red-7.5*blue+1)                          #Enhanced Vegetation Index
    SAVI  = lambda NIR,red:        1.5*(NIR-red)/(NIR+red+0.5)                                     #Soil Adjusted Vegetation Index
    MSAVI = lambda NIR,red:        (2.0*NIR+1.0*(np.sqrt(2.0*NIR+1.0))**2.0-8.0*(NIR-red))/2.0     #Modified Soil Adjusted Vegetation Index
    NDMI  = lambda NIR,SWIR1:      (NIR-SWIR1)/(NIR+SWIR1)                                         #Normalized Difference Moisture Index
    NDWI  = lambda green,NIR:      (green-NIR)/(green+NIR)                                         #Normalized Difference Water Index
    NBR   = lambda NIR,SWIR2:      (NIR-SWIR2)/(NIR+SWIR2)                                         #Normalized Burn Ratio
    NBR2  = lambda SWIR1,SWIR2:    (SWIR1-SWIR2)/(SWIR1+SWIR2)                                     #Normalized Burn Ratio 2
    TVI   = lambda NIR,green,red:  (120.0*(NIR-green)-200.0*(red-green))/2.0                       #Triangular Vegetation Index

'''#########################################################################
## Basic functions
#########################################################################'''

#The line of code below will return a list of all HLS files in a folder.
#  By default, also includes all subfolders.
#  If a folder isn't provided, it uses the current folder.
def find(path=os.getcwd(),check_subfols=True):
    file_list = []
    if check_subfols:
        for root, dirs, files in os.walk(path):
            for file in files:
                is_valid = file.endswith('.tif')
                if(file.startswith('HLS.')) and is_valid:
                    file_list.append(os.path.join(root,file))
    
    else:
        for file in os.listdir():
            is_valid = file.endswith('.tif')
            if(file.startswith('HLS.')) and is_valid:
                    file_list.append(os.path.join(path,file))
    return file_list

def process_image(im,processes):
    reader = rio.open(im)                #Create a reader object
    array = reader.read()                #Ingest the array
    array = np.where(array==-9999, np.nan, array)         #Remove nodata values
    array = process(array,processes)     #Put through a processing stack
    #array = array.astype(rio.uint8)      #Fit to 8-bit
    return array

def get_metadata(tif_path):
    """
    Extract metadata from a .tif file.

    Parameters:
    - tif_path: Path to the .tif file

    Returns:
    - metadata: Dictionary containing the metadata
    """
    with rio.open(tif_path) as src:
        metadata = src.meta
        metadata.update(src.tags())  # Add additional tags to the metadata
        metadata['crs'] = src.crs.to_string()  # Get the Coordinate Reference System (CRS)
        metadata['transform'] = src.transform.to_gdal()  # Get the affine transformation parameters
    return metadata

def plot_vi_meta_to_image(vi_array, metadata, vi_choice, cmap="RdYlGn"):
    """
    Plots a vegetation index (VI) represented by the given vi_array and incorporates
    metadata information in the plot title. Saves the plot as a PNG image in memory.

    Parameters:
    - vi_array (numpy.ndarray): The 2D array containing the vegetation index values to be plotted.
    - metadata (dict): Metadata information related to the satellite imagery.
    - vi_choice (str): The name or type of vegetation index being plotted (e.g., NDVI, EVI).
    - cmap (str, optional): The colormap to be used in the plot. Default is "RdYlGn".

    Returns:
    - io.BytesIO: A BytesIO object containing the PNG image of the plot.

    Example:
    plot_buffer = plot_vi_meta_to_image(vi_array, metadata, 'NDVI')
    """
    
    sensing_time = metadata.get('SENSING_TIME', 'N/A')
    spacecraft_name = metadata.get('SPACECRAFT_NAME', 'N/A')
    coordinate_system = metadata.get('HORIZONTAL_CS_NAME', 'N/A')
    spatial_resolution = metadata.get('SPATIAL_RESOLUTION', 'N/A')

    fig, ax = plt.subplots(figsize=(10,10))
    
    # Use the result of ax.imshow() for colorbar
    im = ax.imshow(vi_array, cmap=cmap, vmin=-1, vmax=1) 
    
    ax.set_xticks([])  # Remove x-axis tick labels
    ax.set_yticks([])  # Remove y-axis tick labels
    
    # Construct a title using the extracted metadata
    title = f"{vi_choice} from {spacecraft_name} on {sensing_time}\nCoordinate System: {coordinate_system} | Spatial Resolution: {spatial_resolution}m"
    ax.set_title(title, fontsize=10)
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    
    return buf


#Takes lists of HLS files and turns them into a dictionary divided by collection.
#  If called, it gives a brief summary of the dataset.
#  If called with the print() command, it returns a detailed description.
#  If subscripted or iterated across, it returns items in date order as dictionaries
#    where the key is the collection ID and the values are a list of associated files.
#  Initiating with reversed=True or using <object_name>.reverse() will change the order,
#    so the files will then be listed from most recent to earliest.
class granules(object):
    def __init__(self,file_list=[], reversed=False):
        
        #Establish variables. Add the initial dataset if there is 1.
        self.collects = {}
        self.dates = []
        self.reversed = reversed
        self._index = 0
        self.add(file_list)
    
    #Add files to into a sorted dictionary, then call order_historically below.
    def add(self,file_list):
        for file in file_list:
            cid = file[file.rfind('HLS'):file.rfind('.v2.0')+5]
            if cid in self.collects.keys():
                self.collects[cid].append(file)
            else:
                self.collects[cid] = [file]
                try:
                    self.dates.append(datetime.datetime.strptime(file.split(".")[3],"%Y%jT%H%M%S"))
                except ValueError:
                    self.dates.append(datetime.datetime(2022, 3, 21, 21, 9, 31))
                    print(file)
                    
        self.order_historically()
    
    #Sort files by date.
    def order_historically(self):
        self.dates = sorted(self.dates)
        dateStrings = [f"{date:%Y%jT%H%M%S}" for date in self.dates]
        self.order = []
        for date in dateStrings:
            files = [key for key, value in self.collects.items() if date in key]
            self.order.extend(set(files))
        if self.reversed:
            self.reverse()
    
    #Reverse the dataset. Data is stored from earliest to most-recent unless self.reversed = True.
    def reverse(self):
        self.dates.reverse()
        self.order.reverse()
        self.reversed = not self.reversed
    
    #Print a summation of the contents of the dictionary.
    def total(self):
        collects = list(self.collects.keys())
        numFiles = sum(len(self.collects[collect]) for collect in collects)
        numCols = len(collects)
        total = '{} HLS image files consisting of {} unique collections.'.format(numFiles,numCols)
        return total
    
    #Print a summation of the date range of the imagery.
    def date_range(self):
        if not self.dates:
            return 'No HLS files provided.'
        elif len(self.dates) == 1:
            return 'Cannot calculate range from 1 image file.'
        else:
            diff = self.dates[0] - self.dates[-1]
            first_date = self.dates[0].strftime("%d-%b-%Y")
            second_date = self.dates[-1].strftime("%d-%b-%Y")
            years = math.trunc(abs(diff.days/365.0))
            days = abs(diff.days) - (365*years)
            av = abs(len(self.collects.keys())/diff.days)
            order = 'earliest to most recent' if self.reversed is False else 'most recent to earliest'
            message = 'Dataset contains imagery from {} to {}, ordered from {}.'.format(first_date,second_date,order)
            message += '\nData spans {:} years and {:} days, with an average revisit of {:.1f} days.'.format(years,days,1/av)
            return message
    
    #
    def create_time_series(self,bands=band_combinations.rgb,processes=stack.simpleRGB):
        numBands = len(bands)

        if numBands == 1:
            pass
        
        elif numBands == 3:
            numCollects = len(list(self.collects.keys()))                   #Get the size of the current collection
            firstImage = next(self)                                         #Get the first image in this object
            firstBand = bands[0]                                            #Get the first band to look at
            
            currentCollect = list(firstImage.keys())[0]                     #Get the collection ID
            imageFiles = list(firstImage.values())[0]                       #Get the list of image files
            firstBandFile = [im for im in imageFiles if firstBand in im][0] #Get the image file associated with the first image to form
            array = process_image(firstBandFile,processes)                  #Open, process and prepare the image for output
            
            arrayShape = list(array.shape)                                         #We can now preallocate memory for the time series
            timeSeriesShape = [numCollects,arrayShape[1],arrayShape[2],numBands] #This will be a 4D array with dimensions:
            timeSeries = np.zeros(timeSeriesShape)                                 #Time,Band,X,Y
            timeSeries[0,:,:,0] = array                                            #Add images by: timeSeries[collect,:,:,band]
            
            thisBand = [im for im in imageFiles if bands[1] in im][0]       #Now iterate through the next 2 bands
            array = process_image(thisBand,processes)
            timeSeries[0,:,:,1] = array
            thisBand = [im for im in imageFiles if bands[2] in im][0]
            array = process_image(thisBand,processes)
            timeSeries[0,:,:,2] = array
            
            for collectInd,collection_name in enumerate(self.order):                   #Now iterate through the entire collection               #
                imageFiles = list(self.collects[collection_name])                   #
                print('  Adding {} to the time series.'.format(collection_name))
                
                for bandInd,band in enumerate(bands):                       #Iterate through the bands
                    thisBand = [im for im in imageFiles if band in im][0]   #
                    array = process_image(thisBand,processes)
                    timeSeries[collectInd,:,:,bandInd] = array
                
            print('Converting to uint8')
            timeSeries = timeSeries.astype(rio.uint8)
            print('Creating .gif file')
            imio.imwrite(f"test2.gif",timeSeries,duration=1000)
                            
    def create_VI_time_series(self,VI_choice = 'EVI',processes=stack.simpleRGB):
        """
        Process vegetation index time series for a given VI choice, create a GIF, and save it.

        Parameters:
        - VI_choice (str, optional): The vegetation index choice. Default is 'EVI'.
        - processes (int, optional): The number of processes to use for parallel processing. Default is 1.

        Raises:
        - Prints an error message if an invalid VI choice is provided and defaults to 'EVI'.

        Example:
        granule.create_VI_time_series(VI_choice = 'NDVI')
        """
        metadata_collection = {}
        vegetation_index_arrays = []
        acutal_order = []
        bands = getattr(band_combinations, VI_choice.lower(), None)

        vi_function = getattr(VI, VI_choice, None)
        if vi_function is None:
            print(f"Invalid VI value: {VI_choice}. Using default EVI.")
            vi_function = VI.EVI
        
        def generate_gif():
                frames = []
                for series, collection_name in zip(vegetation_index_arrays, acutal_order):
                    metadata = metadata_collection[collection_name]
                    buf = plot_vi_meta_to_image(series[0], metadata, VI_choice)
                    frames.append(imageio.imread(buf))

                # Save the frames as a GIF
                name = VI_choice + metadata.get('SENSING_TIME', 'N/A')
                imio.imwrite(f"{name}.gif", frames, duration=1000)

            
        # image_files = [file for sublist in self.collects.values() for file in sublist]

        for collect_ind,collection_name in enumerate(self.order):
            print('Adding {} to the time series.'.format(collection_name))    
            image_files = list(self.collects[collection_name])                
            try:
                bands_arrays = {}
                for band_id in bands:
                    try:
                        # Find the first file in image_files that contains the current band_id
                        band_file = next(im for im in image_files if band_id in im)
                        bands_arrays[band_id] = process_image(band_file, processes)
                    except StopIteration:
                        # Handle the case where no matching file is found
                        print(f"File for band {band_id} not found.")
                        continue

                metadata_collection[collection_name] = get_metadata(band_file)

                VIarray = vi_function(
                    *[bands_arrays[band] for band in bands]
                )
                vegetation_index_arrays.append(VIarray)
                acutal_order.append(collection_name)
            except Exception as e:
                print(e)
        
        generate_gif()
       
    #When called directly, print a summation of the file list.
    def __repr__(self):
        return self.total()
    
    #When the print command is used, list the individual collections and the associated filenames.
    def __str__(self):
        message = ''
        for collect in self.order:
            message += '\n' + collect
            for file in self.collects[collect]:
                message += '\n     ' + file
        message += '\n\n' + self.total()
        message += '\n' + self.date_range()
        return message
    
    #Make this object subscriptable. Items are output in date order, earliest by default.
    def __getitem__(self,item):
         return {self.order[item]: self.collects[self.order[item]]}
    
    #Make this object iterable.
    def __iter__(self):
        return self
    def __next__(self):
        self._index += 1
        if self._index <= len(self.order):
            return self.__getitem__(self._index-1)
        else:
            self._index = 0
            raise StopIteration

#An object to handle calling and opening indivudal granules.
class granule(object):
    def __init__(self,input_list):
        pass

# Usage
# granule = granules(find())
# granule.create_VI_time_series(VI_choice = 'EVI')