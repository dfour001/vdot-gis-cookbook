#===============================================================================
# Load LRS into GeoPandas
#===============================================================================
# How do I bring the LRS and m-values into a GeoPandas script?
# 
# GeoPandas does not support importing a line file with m-values by itself.  My
# workaround is to use the shapefile module to read the m-values and store them
# in a python dictionary.  The downside is that this means that the LRS must be
# saved as a shapefile in order to be used with GeoPandas if you also need to
# have access to the m-values.
#
# The code below will load the LRS as a GeoDataFrame and create a dictionary of
# m-values.  The dictionary keys are the rte_nm and the m-values are stored as
# a list.  The index of the m-values in the list correspond to the index of the
# vertices in the polyline for that route (eg mValueDict['R-VA   IS00095NB'][-1]
# will return the m-value for the last point on I-95).
#===============================================================================
# Written for GeoPandas in Python 3.7
# By Dan Fourquet
#===============================================================================

import geopandas as gp
import shapefile

# LRS - This must be a shapefile in order to bring in m-values
lrsPath = r'.\data\LRS\LRS_Full.shp'

def load_m_values(lrsPath):
    """ Reads the LRS as a shapefile and returns an m-value dictionary 
    
    input:
        lrsPath - path to the LRS as a shapefile
        
    output:
        mValueDict - a python dictionary containing m-values
    """
    mValueDict = {}
    with shapefile.Reader(lrsPath) as shp:
            for row in shp.iterShapeRecords():
                try:
                    record = row.record
                    shape = row.shape
                    rte_nm = record['RTE_NM']
                    mValues = shape.m
                    mValueDict[rte_nm] = mValues
                except:
                    # print('Error finding m-value for row')
                    continue

    return mValueDict

# Create LRS GeoDataFrame
lrs = gp.read_file(lrsPath)
lrs = lrs.to_crs(epsg=3968) # If projection to Virginia Lambert is needed

# Create m-value dictionary
mValueDict = load_m_values(lrsPath)


