#===============================================================================
# Flip Event Table
#===============================================================================
# This will ensure that all events in the input event table exist on both the
# prime and non-prime side of a route so that, if drawn on the Overlap LRS, both
# directions will be drawn.  Divided centerline segments will have one copy on
# each direction.  Non-divided centerline segments will have two copies for each
# direction.
#
# This was originally created for VTrans Mid-Term needs, which
# requires input datasets to be directional, but often the input datasets are
# only on the master rote in the prime direction.
#===============================================================================
# Written for ArcGIS Pro in Python 3
# By Dan Fourquet
#===============================================================================


import arcpy
import pandas as pd
import os

def get_point_mp(inputPointGeometry, RouteGeom):
    """ Locates the MP value of an input point along the LRS

        ** The spatial reference of the input must match the spatial reference
           of the lrs! **

    Input:
        inputPointGeometry - an arcpy PointGeometry object
        RouteGeom - route geometry from the LRS

    Output:
        mp - the m-value of the input point
    """
    try:

        # Check for route multipart geometry.  If multipart, find closest part to
        # ensure that the correct MP is returned
        if RouteGeom.isMultipart:
            # Get list of parts
            parts = [arcpy.Polyline(RouteGeom[i], has_m=True) for i in range(RouteGeom.partCount)]

            # Get distances from inputPolyline's mid-point to each route part
            partDists = {inputPointGeometry.distanceTo(part):part for part in parts}

            # Replace RouteGeom with closest polyline part
            RouteGeom = partDists[min(partDists)]

        rteMeasure = RouteGeom.measureOnLine(inputPointGeometry)
        rtePosition = RouteGeom.positionAlongLine(rteMeasure)
        mp = rtePosition.firstPoint.M
        return round(mp, 3)
    
    except Exception as e:
        print(e)
        return None


def flip_event_table(tbl_input, attribute_field, master_lrs, overlap_lrs, output_tbl_path, rte_nm='RTE_NM', begin_msr='BEGIN_MSR', end_msr='END_MSR', attribute_field_type='TEXT', export_both_directions=True):
    """ Description

    Input:
        tbl_input - Input event table or feature layer with LRS referencing data
        attribute_field - the field in tbl_input to preserve 
        master_lrs - a reference to the lrs layer
        overlap_lrs - the lrs rte_nm that the polyline will be placed on
        output_tbl_path - gdb path for output event table
        rte_nm - the field name that contains the RTE_NM data from the LRS
        begin_msr - the field name that contains the from M-value
        end_msr - the field naem that contains the to M-value
        attribute_field_type - the field type for the attribute field (eg 'TEXT', 'LONG')
        export_both_directions - *NOT YET IMPLEMENTED* both directions will be exported
            to the output event table.  If False, only opposite direction routes from
            the input will be exported
    Output:
        Event table with both directions included
    """
    arcpy.env.overwriteOutput = True
    print('Create a copy of the input')
    arcpy.TableToTable_conversion(tbl_input, 'memory', 'tbl_input')
    tbl_input = 'memory//tbl_input'
    

    print('Create route event layer')
    arcpy.lr.MakeRouteEventLayer(overlap_lrs, "RTE_NM", tbl_input, f"{rte_nm}; Line; {begin_msr}; {end_msr}", "tbl_input Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
    arcpy.conversion.FeatureClassToFeatureClass("tbl_input Events", 'memory', "tbl_input_events")
    arcpy.Delete_management("tbl_input Events")
    tbl_input_events = 'memory//tbl_input_events'


    print('Input layer must not contain multipart geometry')
    # Check for multipart geometry
    isMultipart = False
    with arcpy.da.SearchCursor(tbl_input_events, 'SHAPE@') as cur:
        for row in cur:
            if row[0] and row[0].isMultipart:
                isMultipart = True
                break
    
    if isMultipart:
        print('    Multipart geometry found')
        print('    Converting to single part')
        tbl_input_events_singlepart = 'memory\\tbl_input_event_singlepart'
        arcpy.MultipartToSinglepart_management(tbl_input_events, tbl_input_events_singlepart)
        tbl_input_events = 'memory\\tbl_input_event_singlepart'
        arcpy.Delete_management('memory\\tbl_input_events')
    else:
        print('    No multipart geometry found')



    
    print('Add new_rte_nm, new_begin_msr, new_end_msr fields')
    arcpy.AddField_management(tbl_input_events, 'NEW_RTE_NM', 'TEXT')
    arcpy.AddField_management(tbl_input_events, 'NEW_BEGIN_MSR', 'DOUBLE')
    arcpy.AddField_management(tbl_input_events, 'NEW_END_MSR', 'DOUBLE')
        

    print('Calculate new_rte_nm as opposite route from old rte_nm')
    print('    Build opposite route dictionary')
    opp_route_dict = {row[0]:row[1] for row in arcpy.da.SearchCursor(overlap_lrs, ['RTE_NM', 'RTE_OPPOSITE_DIRECTION_RTE_NM'])}
    
    print('    Calculate opposite route')
    with arcpy.da.UpdateCursor(tbl_input_events, [rte_nm, 'NEW_RTE_NM']) as cur:
        for row in cur:
            new_rte_nm = opp_route_dict.get(row[0])
            row[1] = new_rte_nm
            cur.updateRow(row)


    print('Prepare LRS')
    print('    Identify required route names')
    required_routes = set([row[0] for row in arcpy.da.SearchCursor(tbl_input_events, 'NEW_RTE_NM')])
    
    print('    Create route geometry dictionary')
    route_geom_dict = {row[0]:row[1] for row in arcpy.da.SearchCursor(overlap_lrs, ['RTE_NM', 'SHAPE@']) if row[0] in required_routes}


    print('Locate new begin and end measures based on old geometry')
    with arcpy.da.UpdateCursor(tbl_input_events, ['SHAPE@', 'NEW_RTE_NM', 'NEW_BEGIN_MSR', 'NEW_END_MSR']) as cur:
        for row in cur:
            geom = row[0]
            new_rte_nm = row[1]

            firstPoint = arcpy.PointGeometry(geom.firstPoint)
            lastPoint = arcpy.PointGeometry(geom.lastPoint)
            lrs_geom = route_geom_dict.get(new_rte_nm)
            if lrs_geom:
                this_begin_msr = get_point_mp(firstPoint, lrs_geom)
                this_end_msr = get_point_mp(lastPoint, lrs_geom)
                row[2] = this_begin_msr
                row[3] = this_end_msr
                cur.updateRow(row)


    print('Create DataFrame with new data')
    cols = [rte_nm, begin_msr, end_msr, 'NEW_RTE_NM', 'NEW_BEGIN_MSR', 'NEW_END_MSR', attribute_field]
    print(cols)
    df = pd.DataFrame([row for row in arcpy.da.SearchCursor(tbl_input_events, cols)], columns=cols)
    df.rename(columns={rte_nm: 'RTE_NM', begin_msr: 'BEGIN_MSR', end_msr: 'END_MSR'}, inplace=True)
    df_ori = df[['RTE_NM', 'BEGIN_MSR', 'END_MSR', attribute_field]]
    df_flipped = df[['NEW_RTE_NM', 'NEW_BEGIN_MSR', 'NEW_END_MSR', attribute_field]]
    df_flipped.rename(columns={'NEW_RTE_NM':'RTE_NM', 'NEW_BEGIN_MSR':'BEGIN_MSR', 'NEW_END_MSR':'END_MSR'}, inplace=True)
    df_flipped = df_flipped.loc[df_flipped['RTE_NM'].notnull()]

    df_merge = df_ori.merge(df_flipped, 'outer')
    df_dte = df_merge.loc[df_merge['RTE_NM'].str.startswith('D-TE')].index
    df_merge.drop(df_dte, inplace=True)


    print('Create output table')
    arcpy.CreateTable_management('memory', 'output_table')
    arcpy.AddField_management('memory\\output_table', 'RTE_NM', 'TEXT')
    arcpy.AddField_management('memory\\output_table', 'BEGIN_MSR', 'DOUBLE')
    arcpy.AddField_management('memory\\output_table', 'END_MSR', 'DOUBLE')
    arcpy.AddField_management('memory\\output_table', attribute_field, attribute_field_type)

    output_table_records = df_merge.values.tolist()
    print(output_table_records[:4])
    with arcpy.da.InsertCursor('memory\\output_table', ['RTE_NM', 'BEGIN_MSR', 'END_MSR', attribute_field]) as cur:
        for row in output_table_records:
            cur.insertRow(row)

    print('Dissolve table')
    arcpy.lr.DissolveRouteEvents('memory\\output_table', f"RTE_NM; Line; BEGIN_MSR; END_MSR", attribute_field, output_tbl_path, f"RTE_NM; Line; BEGIN_MSR; END_MSR", "DISSOLVE", "INDEX")



if __name__ == '__main__':
    tbl_input = r'C:\Users\daniel.fourquet\Documents\Tasks\VTrans Update\2023-needs\A1 - Common Datasets\Urban Development Areas (UDAs) Needs\data\add_missing_udas.gdb\missing_uda_needs'
    attribute_field = 'UDA'
    master_lrs = r'C:\Users\daniel.fourquet\Documents\Tasks\VTrans Update\2023-needs\A1 - Common Datasets\Common_Datasets.gdb\SDE_VDOT_RTE_MASTER_LRS_DY'
    overlap_lrs = r'C:\Users\daniel.fourquet\Documents\Tasks\VTrans Update\2023-needs\A1 - Common Datasets\Common_Datasets.gdb\SDE_VDOT_RTE_OVERLAP_LRS_DY'
    output_tbl_path = r'C:\Users\daniel.fourquet\Documents\Tasks\VTrans Update\2023-needs\A1 - Common Datasets\Urban Development Areas (UDAs) Needs\data\add_missing_udas.gdb\tbl_missing_uda_needs'
    flip_event_table(tbl_input, attribute_field, master_lrs, overlap_lrs, output_tbl_path)