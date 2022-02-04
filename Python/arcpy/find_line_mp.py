#===============================================================================
# Find Begin and End MP of a Line
#===============================================================================
# Given a line geometry, how do I find the begin and end point of the line
# on the LRS?
# 
# This is fairly straitforward if you know the rte_nm that the output event should
# be on.  You simply need to find the coordinates of the input geometry's begin 
# and end points, find the closest point on the route to those points, and return
# the M value.
#
# If the rte_nm is unknown, then the problem becomes much more difficult.  See
# match_line_to_rte_nm.py for more details. If a line spans multiple lrs routes,
# the function below would need to be called for each rte_nm.
#
# It's important that the spatial reference of the input geometry matches the
# spatial reference of the LRS.  Many tools within ArcGIS handle projection for
# you, but when making your own tools, you must handle it yourself.  If you're
# not careful with spatial reference, this code will return the incorrect value!
#===============================================================================
# Written for ArcGIS Pro in Python 3.7
# By Dan Fourquet
#===============================================================================


def get_line_mp(inputPolyline, lrs, rte_nm):
    """ Locates the begin and end MP values of an input line along the LRS
        ** The spatial reference of the input must match the spatial reference
           of the lrs! **
    Input:
        inputPolyline - an arcpy Polyline object
        lrs - a reference to the lrs layer
        rte_nm - the lrs rte_nm that the polyline will be placed on
    Output:
        (beginMP, endMP)
    """

    try:
        # Get the geometry for the LRS route
        RouteGeom = None
        if lrs.getSelectionSet():
            arcpy.management.SelectLayerByAttribute(lrs, 'CLEAR_SELECTION')
        with arcpy.da.SearchCursor(lrs, "SHAPE@", "RTE_NM = '{}'".format(rte_nm)) as cur:
            for row in cur:
                RouteGeom = row[0]

        if not RouteGeom:
            print(f'Route "{rte_nm}" not found')
            return None, None

        # Check for multipart geometry.  If multipart, find closest part to
        # ensure that the correct MP is returned
        if geom.isMultipart:
            # Get list of parts
            parts = [arcpy.Polyline(RouteGeom[i], has_m=True) for i in range(RouteGeom.partCount)]

            # Get input polyline midpoint
            midPoint = inputPolyline.positionAlongLine(0.5, use_percentage=True)

            # Get distances from inputPolyline's mid-point to each route part
            partDists = {midPoint.distanceTo(part):part for part in parts}

            # Replace RouteGeom with closest polyline part
            RouteGeom = partDists[min(partDists)]

        def get_mp_from_point(route, point):
            """ Returns the m-value along the input route geometry
                given an input point geometry """
            rteMeasure = route.measureOnLine(point)
            rtePosition = route.positionAlongLine(rteMeasure)
            mp = rtePosition.firstPoint.M
            return mp

        beginPt = inputPolyline.firstPoint
        beginMP = get_mp_from_point(RouteGeom, beginPt)

        endPt = inputPolyline.lastPoint
        endMP = get_mp_from_point(RouteGeom, endPt)

        return round(beginMP, 3), round(endMP, 3)

    except Exception as e:
        print(e)
        return None, None
        


#===============================================================================
# Example - print the begin and end MPs of each line geometry.  In a real-world
# situation, the rte_nm may not be known.  See match_line_to_rte_nm.py
#===============================================================================

import arcpy

lrs = r'path\to\lrs'
inputLines = r'path\to\line\feature\class'

# For each line in inputLines, print rte_nm, beginMP, and endMP
with arcpy.da.SearchCursor(inputLines, ['rte_nm', 'SHAPE@']) as cur:
    for rte_nm, geom in cur:
        beginMP, endMP = get_line_mp(geom, lrs, rte_nm)
        print(rte_nm, beginMP, endMP)
