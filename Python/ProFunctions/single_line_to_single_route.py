#===============================================================================
# Single line to single LRS route
#===============================================================================
# This tool is designed to be used within the python window in Pro.  It will
# allow you to select a single polyline feature in one layer and a single route
# in the lrs layer.  The rte_nm, begin_msr, and end_msr of the layer will be
# found on the selected lrs route.  if the *_update input parameters are
# provided, then this information will automatically be updated in the input
# layer.  Otherwise the values will be printed.
#===============================================================================
# Written for ArcGIS Pro in Python 3
# By Dan Fourquet
#===============================================================================


import arcpy

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
        if RouteGeom.isMultipart:
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


def single_line_to_single_route(layer, lrs, rte_nm_update=None, begin_msr_update=None, end_msr_update=None):
    """ This tool is designed to be used within the python window in Pro.  It will allow you to select
        a single polyline feature in one layer and a single route in the lrs layer.  The rte_nm, begin_msr,
        and end_msr of the layer will be found on the selected lrs route.  if the *_update input parameters
        are provided, then this information will automatically be updated in the input layer.  Otherwise
        the values will be printed.
        
        input:
            layer (string or layer) - the layer that is to be found on the LRS (only one feature is selected)
            lrs (string or layer) - a copy of the lrs (only one feature is selected)
            rte_nm_update - the field in the input layer that will be updated with rte_nm information
            begin_msr_update - the field in the input layer that will be updated with begin_msr information
            end_msr_update - the field in the input layer that will be updated with end_msr information
        """
    def get_layer(name):
        prj = arcpy.mp.ArcGISProject("CURRENT")
        map = prj.listMaps()[0]
        layer = map.listLayers(name)[0]
        return layer

    if type(layer) == str:
        layer = get_layer(layer)
    if type(lrs) == str:
        lrs = get_layer(lrs)

    
    
    # Ensure only one feature is selected in both layers
    def only_one_selected(*layers):
        for layer in layers:
            x = layer.getSelectionSet()
            if x and len(x) > 1:
                print(f'{len(x)} features selected in {layer.name}')
                return False

            if not x:
                print(f'0 features selected in {layer.name}')
                return False
            
        return True
    
    if not only_one_selected(layer, lrs):
        print('Error - Only one feature may be selected in each layer')
        return

    layer_geom = [row[0] for row in arcpy.da.SearchCursor(layer, 'SHAPE@')][0]
    rte_nm = [row[0] for row in arcpy.da.SearchCursor(lrs, 'RTE_NM')][0]
    begin_msr, end_msr = get_line_mp(layer_geom, lrs, rte_nm)
    
    if rte_nm_update:
        with arcpy.da.UpdateCursor(layer, [rte_nm_update, begin_msr_update, end_msr_update]) as cur:
            for row in cur:
                row[0] = rte_nm
                row[1] = begin_msr
                row[2] = end_msr
                cur.updateRow(row)
                
    else:
        print(rte_nm, begin_msr, end_msr)
