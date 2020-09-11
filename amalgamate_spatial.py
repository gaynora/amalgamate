'''
amalgamates the area of one or more polygons into another defined geographical area, removing overlapping parts

takes multiple shapefiles, creates a union of combined area of all
uses the result of the union to create an intersection with an area of interest, creating a new polygon where areas overlap
only one polygon is created where overlapping parts exist - there are no overlapping polygons in the output
geometries are dissolved on the area of interest unique ID

python 3 script
'''

import geopandas
import pandas

#import the shapefile(s) to clip
first_shp = geopandas.read_file('shapes_to_dissolve.shp') #change filenames and paths as literals if needed
second_shp = geopandas.read_file('shapes_to_dissolve2.shp')
third_shp = geopandas.read_file('shapes_to_dissolve3.shp')
# multiple polygon layers may be added

#import the area of interest shapefile
area_of_interest = geopandas.read_file('aoi.shp')

#union of multiple polygons
def do_union(firstpolys, secondpolys):
    res_union = geopandas.overlay(firstpolys, secondpolys, how='union')
    return res_union

union1 = do_union(first_shp, second_shp)
union2 = do_union(union1, third_shp)
#multiple unions may be added - the overlay method is limted to 2 polygon layers

#intersect / clip the result of the union operation with the area of interest polygon
def do_intersect(shapefile_to_clip, aoi):
    intersection = geopandas.overlay(shapefile_to_clip, aoi, how='intersection')
    dissolved = intersection.dissolve(by='aoi') #the attribute field defined is from the area of interest polygon and must be present in the input polygon, and a unique ID
    return dissolved

intersect = do_intersect(union2, area_of_interest)

#calculate the area of each polygon and store in attribute table
intersect["m2"] = intersect.area

aoi_output = area_of_interest.merge(intersect, on='uniqueid')# this field needs to be a unique ID and not the same as that used to perform the dissolve function, it may need to be changed

# convert the intersect geodataframe / polygons into a simple attribute table
intersect_table = pandas.DataFrame(intersect.drop(columns='geometry')) 

#join the intersect dataframe / attribute table of m2 to area of interest polygon 
def table_join(x, y):
    merge_result = x.merge(y, on='uniqueid') #Geodataframe / polygons needs to be the left argument, and dataframe or simple table the right argument, field name literal may need to be changed 
    return merge_result

z = table_join(area_of_interest, intersect_table)


#save results as new shapefiles
intersect.to_file('intersect_output.shp')# the resultant attribute table gives the columns in order of polygon arguments given to the overlay function, then area/m2
z.to_file('aoi_output.shp')
