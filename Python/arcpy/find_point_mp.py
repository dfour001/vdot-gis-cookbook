#===============================================================================
# Find MP of a point
#===============================================================================
# Given a point geometry and rte_nm, how do I find the MP on the LRS?
# 
# If the rte_nm is known, the MP of a point can be found using arcpy's Polyline
# object methods.  First the measureOnLine method is called to locate the measure
# of the input point along the route geometry.  Then the positionAlongLine method
# is called to return a point geometry containing the M-value for that location.
#
# If the rte_nm is unknown, see match_point_to_rte_nm.py.
#
# It's important that the spatial reference of the input geometry matches the
# spatial reference of the LRS.  Many tools within ArcGIS handle projection for
# you, but when making your own tools, you must handle it yourself.  If you're
# not careful with spatial reference, this code will return the incorrect value!
#===============================================================================
# Written for ArcGIS Pro in Python 3.7
# By Dan Fourquet
#===============================================================================

def get_point_mp(inputPointGeometry, lrs, rte_nm):
    """ Locates the MP value of an input point along the LRS

        ** The spatial reference of the input must match the spatial reference
           of the lrs! **

    Input:
        inputPointGeometry - an arcpy PointGeometry object
        lrs - a reference to the lrs layer
        rte_nm - the lrs rte_nm that the polyline will be placed on

    Output:
        mp - the m-value of the input point
    """
    try:
        # Get the geometry for the LRS route
        with arcpy.da.SearchCursor(lrs, "SHAPE@", "RTE_NM = '{}'".format(rte_nm)) as cur:
            for row in cur:
                RouteGeom = row[0]


        rteMeasure = RouteGeom.measureOnLine(inputPointGeometry)
        rtePosition = RouteGeom.positionAlongLine(rteMeasure)
        mp = rtePosition.firstPoint.M
        return round(mp, 3)
    
    except Exception as e:
        print(e)
        return None


#===============================================================================
# Example - Print the MP value of an input point.  In a real-world
# situation, the rte_nm may not be known.  See match_point_to_rte_nm.py
#===============================================================================

import arcpy

lrs = r'path\to\lrs'
rte_nm = 'R-VA009SC00691EB'

# Example point uses WGS84 coordinates (EPSG 4326)
point = arcpy.Point(-79.605, 37.28)
PointGeometry = arcpy.PointGeometry(point, spatial_reference=arcpy.SpatialReference(4326))

# Point must be projected to Web Mercator (EPSG 3857) to match the LRS
PointGeometry = PointGeometry.projectAs(arcpy.SpatialReference(3857))


mp = get_point_mp(PointGeometry, lrs, rte_nm)
print(mp)