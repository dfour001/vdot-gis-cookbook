#===============================================================================
# Open Google StreetView on line centerpoint
#===============================================================================
# With a single segment of a specified line selected, this function will open 
# the midpoint of that line in Google StreetView in a new browser window.
# 
# The lineLayerName variable must be replaced with the layer name as it appears
# in the Table of Contents.
#
# The function is called sv(), shorthand for "StreetView".
# 
#===============================================================================
# Written for ArcGIS Pro's Python Window
# By Dan Fourquet
#===============================================================================

import webbrowser

# This needs to be the layer name exactly as it appears in the table of contents
# It must also be a unique name
lineLayerName = "layerName"

def sv():
    prj = arcpy.mp.ArcGISProject("CURRENT")
    map = prj.listMaps()[0]
    layer = map.listLayers(lineLayerName)[0]
    
    # Make sure only one line segment is selected
    count = layer.getSelectionSet()
    if not count:
        print("No segments are selected")
        return

    if len(count) > 1:
        print("More than one segment is selected")
        return

    # Get line geometry and midpoint
    geom = [row[0] for row in arcpy.da.SearchCursor(layer, 'SHAPE@')][0]
    midpoint = geom.positionAlongLine(0.5, True).projectAs(arcpy.SpatialReference(4326)).firstPoint

    url = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={midpoint.Y},{midpoint.X}"
    webbrowser.open(url)