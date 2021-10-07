#===============================================================================
# Selecting routes within a distance of a point
#===============================================================================
# How do find the rte_nm values in the lrs within a specific distance of a 
# point?
# 
# Lets say you have point coordinates and you need to find all of the routes in
# the LRS within 50 meters of that point.  The function below will do that, given
# a Shapely point, a distance, and the LRS as a GeoDataFrame.
#===============================================================================
# Written for GeoPandas in Python 3.7
# By Dan Fourquet
#===============================================================================


def select_nearby_routes(point, distance, lrs):
    """ Returns a list of RTE_NMs within the given distance of the
        input point """
    pointBuffer = point.buffer(distance)
    output = lrs[lrs.intersects(pointBuffer)]["RTE_NM"].tolist()
    
    return output


#===============================================================================
# Example - Use the select_nearby_routes function to find all routes within
# 50 meters of an input point
#===============================================================================

import geopandas as gp
from shapely.geometry import Point
from shapely.ops import transform
import pyproj

# Set up LRS
lrsPath = r'path\to\lrs.shp'
lrs = gp.read_file(lrsPath)
lrs = lrs.to_crs(epsg=3968) # Virginia Lambert required for accurate buffer distance

# Create point
point = Point(-77.091, 38.873)

# Project point to Virginia Lambert using pyproj
project = pyproj.Transformer.from_crs(pyproj.CRS('EPSG:4326'), pyproj.CRS('EPSG:3968'), always_xy=True).transform
point = transform(project, point)

routes = select_nearby_routes(point=point, distance=50, lrs=lrs)
print(routes)
# ['S-VA000PR S GARFIELD ST', 'S-VA000PR N GARFIELD ST', 'R-VA   US00050EB', 'R-VA   US00050WB']