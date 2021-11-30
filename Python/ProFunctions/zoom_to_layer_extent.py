#===============================================================================
# Zoom to layer extent
#===============================================================================
# How do I zoom the map camera to the extent of an input layer?
# 
# First the camera object of the map must be selected, then the extent attribute
# of the camera needs to be updated to match the extent of the input layer.  If
# any records in the input layer are selected, then the selected features extent
# will be used
#===============================================================================
# Written for ArcGIS Pro in Python 3.7
# By Dan Fourquet
#===============================================================================


def zoom_to_layer(layerName):
    """ Zooms to the selected features of the input layer.  The layerName
        attribute is a string representing the layer name as it appears
        in the table of contents 
        
        Important caveat - the Map tab must be selected for this to work
        (if something else like the attributes table is active, it will return
        an error).  This is a built-in limitation of arcpy. """
    prj = arcpy.mp.ArcGISProject("CURRENT")
    map = prj.listMaps()[0]

    mapView = prj.activeView
    camera = mapView.camera

    layer = map.listLayers(layerName)[0]
    newExtent = mapView.getLayerExtent(layer)
    camera.setExtent(newExtent)

layerName = "LaneCountUpdate"
zoom_to_layer(layerName)