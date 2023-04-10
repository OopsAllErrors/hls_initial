#find_tile.py

import os
import geopandas as gp

def open_ROI_file(file):
    #breakpoint()
    if file.endswith(('json', 'shp', 'kml')): 
        # Read file in and grab bounds
        try:
            if file.endswith(('json', 'shp')):
                bbox = gp.GeoDataFrame.from_file(file)
            else: 
                bbox = gp.GeoDataFrame.from_file(file, driver='KML')
            
            # Check if file is in Geographic CRS, if not, convert to it
            if bbox.crs.is_geographic:
                bbox.crs = 'EPSG:4326'
            else:
                bbox.to_crs("EPSG:4326", inplace=True)
                print("Note: ROI submitted is being converted to Geographic CRS (EPSG:4326)")
            # Check for number of features included in file
            if len(bbox) > 1:                                                            
                print('Multi-feature polygon detected. Only the first feature will be used.')
                bbox = bbox[0:1]
            
            return bbox
        except:
            sys.exit(f"The GeoJSON/shapefile is either not valid or could not be found.\nPlease double check the name and provide the absolute path to the file or make sure that it is located in {os.getcwd()}")     

def get_bbox_string(bbox):
    # Verify the geometry is valid and convert to comma separated string
    if  bbox['geometry'][0].is_valid:
        bounding_box = [b for b in bbox['geometry'][0].bounds]
        bbox_string = ''
        for b in bounding_box:
            bbox_string += f"{b},"
            bbox_string = bbox_string[:-1]
        return bbox_string
    else:
        sys.exit(f"The GeoJSON/shapefile: {ROI} is not valid.")




#
def find_MGRS_tiles(ROI,print_summary=True):
    
    s2_grid_file = os.path.join(os.path.dirname(__file__),'data','s2_grid.json')
    s2_grid = gp.GeoDataFrame.from_file(s2_grid_file)

    ROI_geom = ROI.to_crs(s2_grid.crs)['geometry'][0]

    intersecting_tiles = s2_grid.intersects(ROI_geom)
    tiles_containing = intersecting_tiles[intersecting_tiles==True].index.values.tolist()

    if tiles_containing:
        tiles = []
        coverage = []
        for ind,tile in s2_grid.iloc[tiles_containing].iterrows():
            tiles.append(tile['identifier'])
            area_overlapped = ROI_geom.intersection(tile['geometry']).area
            coverage.append((area_overlapped/ROI_geom.area)*100)
        
        if print_summary:
            print('Input geometry contained in {} HLS tile(s):'.format(len(tiles)))
            for ind,tile in enumerate(tiles):
                print('  {} covers {:.1f}%'.format(tile,coverage[ind]))
        
        #
        tiles = filter_results(tiles, coverage)
        return tiles
        
    else:
        print('No overlap found with any MGRS tiles')
        return None

#Sort poor and repetitive results from the output of 
def filter_results(tiles,coverage):
    
    #If there's only 1 result, just return that
    if len(tiles) == 1:
        return tiles
    breakpoint()
    #If the AOI fits entirely in at least 1 tile, remove all partial fits
    #  If the AOI is entirely within multiple tiles, arbitrarily pick 1, additional tiles will have the same data
    if 100.0 in coverage:
        tile_ind = coverage.index(100.0)
        return [tiles[tile_ind]]
    
    #If the AOI is not fully 1 in tile and is split between multiple, return all
    return tiles
    
    
    
    