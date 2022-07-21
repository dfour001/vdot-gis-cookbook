""" This tool is intended for use in the python window in ArcGIS Pro.  It will
    help to automatically find and update the begin and end msr values based
    on begin and end coordinates if only the RTE_NM needs to be updated. """

print("Functions:")
print("    * sd(jrstagid) - Sets the definition queries for the event layers\n")
print("    * gm() - With only one record selected in the spatial table, updates the begin and end msr values.  Requires a rte_nm\n")
print("    * coords() - Converts coordinates from DD to individual lat and lng values to copy and paste into the attributes table\n")
print("    * p() - Draws begin and end points for one selected record in the spatial table\n")
print("    * compare() - Compares the lengths between the edit spatial table and the original spatial table\n")
print("    * m() - Matches the definition query between the spatial table and the spatial table events layer\n")



def compare():
    editLen = 0
    oriLen = 0
    with arcpy.da.SearchCursor(TRS21, ["BEGIN_MSR","END_MSR"]) as cur:
     for row in cur:
        editLen += abs(row[0]-row[1])
    with arcpy.da.SearchCursor(TRS20, ['BEGIN_MSR','END_MSR']) as cur:
     for row in cur:
        oriLen += abs(row[0]-row[1])
    print(f'{round(oriLen, 3)} => {round(editLen,3)}')
    print(f'Difference: {round(abs(oriLen - editLen),3)}')



def m():
    TRS21Events.definitionQuery = TRS21.definitionQuery


def sd(x):
    arcpy.management.SelectLayerByAttribute(TRS21, 'CLEAR_SELECTION')
    x = str(x)
    sql = f"ALTERNATE_RTE = '{x}'"
    TRS20.definitionQuery = sql
    TRS20.visible = True
    TRS21.definitionQuery = sql
    TRS21Events.definitionQuery = sql
    zoom_to_layer(TRS20.name)
    p(updateWithoutSelection=True)


def zoom_to_layer(layerName):
    """ Zooms to the selected features of the input layer.  The layerName
        attribute is a string representing the layer name as it appears
        in the table of contents

        Important caveat - the Map tab must be selected for this to work
        (if something else like the attributes table is active, it will return
        an error).  This is a built-in limitation of arcpy. """
    print(f'Zooming to {layerName}...')
    layer = map.listLayers(layerName)[0]
    newExtent = mapView.getLayerExtent(layer)
    camera.setExtent(newExtent)


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
            print('  Multipart route geometry.  Finding closest part...')
            # Get list of parts
            parts = [arcpy.Polyline(RouteGeom[i], has_m=True) for i in range(RouteGeom.partCount)]
            print(f'  {len(parts)} parts')

            # Get input polyline midpoint
            midPoint = inputPolyline.positionAlongLine(0.5, use_percentage=True)

            # Get distances from inputPolyline's mid-point to each route part
            partDists = {midPoint.distanceTo(part):part for part in parts}
            print(partDists)

            # Replace RouteGeom with closest polyline part
            print(f'  Min Distance: {min(partDists)}')
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


def gm():
    if TRS21.getSelectionSet():
        with arcpy.da.UpdateCursor(TRS21, ['RTE_NM','BEGIN_MSR','END_MSR','BEGIN_LAT','BEGIN_LONG','END_LAT','END_LONG', 'JURIS_NO','ROUTE_NO','SEQ_NO']) as cur:
            for row in cur:
                print(row[0])
                beginPoint = arcpy.Point(row[4], row[3])
                endPoint = arcpy.Point(row[6], row[5])
                polyline = arcpy.Polyline(arcpy.Array([beginPoint, endPoint]), arcpy.SpatialReference(4326)).projectAs(arcpy.SpatialReference(3857))
                print(beginPoint.X, beginPoint.Y)
                print(endPoint.X, endPoint.Y)
                print(polyline.firstPoint.X, polyline.firstPoint.Y)
                print(polyline.lastPoint.X, polyline.lastPoint.Y)
                begin_msr, end_msr = get_line_mp(polyline, lrs, row[0])

                print(begin_msr, end_msr)
                row[1] = begin_msr
                row[2] = end_msr
                cur.updateRow(row)

                # Compare Distance to TRS20
                sql = f"JURIS_NO = '{row[7]}' AND ROUTE_NO = '{row[8]}' AND SEQ_NO = '{row[9]}'"
                with arcpy.da.SearchCursor(TRS20, ['BEGIN_MSR', 'END_MSR'], sql) as cur2:
                    for old_begin_msr, old_end_msr in cur2:
                        print('\n\nLength Comparison:')
                        oldLength = round(abs(old_begin_msr - old_end_msr), 3)
                        newLength = round(abs(begin_msr - end_msr), 3)
                        diffLength = round(abs(oldLength - newLength), 3)
                        print(f'    {oldLength} => {newLength}')
                        print(f'    difference: {diffLength}')
                        if diffLength > 0.15:
                            print('\n\n\nWARNING - large difference in new mileage\n\n\n')


def coords(coordStr):
    # 77.4091688?W 37.5253562?N

    lng = coordStr.split(' ')[0].split(u"\N{DEGREE SIGN}")[0]
    lng = float(lng)*-1
    lat = coordStr.split(' ')[1].split(u"\N{DEGREE SIGN}")[0]
    lt = float(lat)
    print(f'lat:\n{lat}')
    print(f'\nlng:\n{lng}')


def setup_points():
    try:
        map.listLayers('EventPoints')[0]
    except:
        arcpy.management.CreateFeatureclass('memory','EventPoints','POINT')
        arcpy.management.AddField('memory/EventPoints','type','TEXT')
        with arcpy.da.InsertCursor('memory/EventPoints',['type']) as cur:
            cur.insertRow(['Begin'])
            cur.insertRow(['End'])


def p(BeginLng=None, BeginLat=None, EndLng=None, EndLat=None, updateWithoutSelection=False):
    if TRS21.getSelectionSet() or updateWithoutSelection:
        if not updateWithoutSelection and len(TRS21.getSelectionSet()) > 1:
            print('Select only one record in the spatial table.')
            return
        else:
            print('Updating Points...')
            with arcpy.da.SearchCursor(TRS21, ['BEGIN_LAT','BEGIN_LONG','END_LAT','END_LONG']) as cur:
                for begin_lat, begin_long, end_lat, end_long in cur:
                    BeginLng = begin_long
                    BeginLat = begin_lat
                    EndLng = end_long
                    EndLat = end_lat

            BeginPt = arcpy.PointGeometry(arcpy.Point(BeginLng, BeginLat), arcpy.SpatialReference(4326)).projectAs(arcpy.SpatialReference(3857))
            EndPt = arcpy.PointGeometry(arcpy.Point(EndLng, EndLat), arcpy.SpatialReference(4326)).projectAs(arcpy.SpatialReference(3857))
            print(BeginPt.firstPoint.X,BeginPt.firstPoint.Y)
            print(EndPt.firstPoint.X,EndPt.firstPoint.Y)
            with arcpy.da.UpdateCursor('memory/EventPoints',['type', 'SHAPE@']) as cur:
                for row in cur:
                    if row[0] == 'Begin':
                        row[1] = BeginPt
                    if row[0] == 'End':
                        row[1] = EndPt
                    cur.updateRow(row)
    else:
        print('No record selected in the spatial table.')

def compare_tables(min=0.15, max=9999):
    TRS20.definitionQuery = ""
    TRS21.definitionQuery = ""

    OldLengths = {}
    with arcpy.da.SearchCursor(TRS20, ['JURIS_NO','ROUTE_NO','SEQ_NO','BEGIN_MSR','END_MSR']) as cur:
        for juris_no, route_no, seq_no, begin_msr, end_msr in cur:
            try:
                jrs = f'{juris_no}{route_no}{seq_no}'
                length = round(abs(begin_msr - end_msr),3)
                OldLengths[jrs] = length
            except:
                continue

    NewLengthsSplits = {}
    with arcpy.da.SearchCursor(TRS21, ['JURIS_NO','ROUTE_NO','SEQ_NO','BEGIN_MSR','END_MSR','JRSTAG_ORI','CHANGE_TYPE_ID'], "STATUS_ID IS NULL AND CHANGE_TYPE_ID = 'I'") as cur:
        for juris_no, route_no, seq_no, begin_msr, end_msr, jrstag_ori, change_type_id in cur:
            jrs = f'{juris_no}{route_no}{seq_no}'
            jrsOri = f'{jrstag_ori[:3]}0{jrstag_ori[3:]}'
            length = round(abs(begin_msr - end_msr),3)
            if jrsOri in NewLengthsSplits:
                NewLengthsSplits[jrsOri].append(length)
            else:
                NewLengthsSplits[jrsOri] = [length]

    NewLengths = {}
    with arcpy.da.SearchCursor(TRS21, ['JURIS_NO','ROUTE_NO','SEQ_NO','BEGIN_MSR','END_MSR','JRSTAG_ORI','CHANGE_TYPE_ID'], "STATUS_ID IS NULL AND CHANGE_TYPE_ID NOT IN ('I','A','D')") as cur:
        for juris_no, route_no, seq_no, begin_msr, end_msr, jrstag_ori, change_type_id in cur:
            try:
                jrs = f'{juris_no}{route_no}{seq_no}'
                length = round(abs(begin_msr - end_msr),3)
                if jrs in NewLengthsSplits:
                    length = length + sum(NewLengthsSplits[jrs])
                NewLengths[jrs] = length
            except:
                continue

    LengthDiff = {}
    for segment in NewLengths:
        if segment in OldLengths:
            newL = NewLengths[segment]
            oldL = OldLengths[segment]
            diff = round(abs(newL-oldL),3)
            LengthDiff[segment] = diff

    for key, value in LengthDiff.items():
        if max > value > min:
            print(f'{key}: {value}')



prj = arcpy.mp.ArcGISProject("CURRENT")
map = prj.listMaps('Map')[0]
lrs = map.listLayers('SDE_VDOT_RTE_MASTER_LRS')[0]
TRS20 = map.listLayers('TBL_RDSEG_SPATIAL_21')[0]
TRS21 = map.listTables('TBL_RDSEG_SPATIAL_EDIT')[0]
TRS21Events = map.listLayers('TBL_RDSEG_SPATIAL_EDIT Events')[0]
setup_points()
EventPoints = map.listLayers('EventPoints')[0]
try:
    mapView = prj.activeView
    camera = mapView.camera
except:
    print('Failed to get active view.  Make sure map tab is active and try again')
