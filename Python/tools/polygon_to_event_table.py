import arcpy

def polygon_to_event_csv(lrs, input_polygon, output_path, output_filename):
    """ Given an input polygon feature class, this function
        will return an event table """

    # Clip lrs by input_polygon
    arcpy.Clip_analysis(lrs, input_polygon, 'memory/lrs_clip')

    # Remove multipart geometries
    arcpy.MultipartToSinglepart_management('memory/lrs_clip', 'memory/lrs_clip_explode')

    # Identify begin/end points
    arcpy.AddField_management('memory/lrs_clip_explode', 'BEGIN_MSR', 'DOUBLE')
    arcpy.AddField_management('memory/lrs_clip_explode', 'END_MSR', 'DOUBLE')
    with arcpy.da.UpdateCursor('memory/lrs_clip_explode', ['BEGIN_MSR','END_MSR', 'SHAPE@']) as cur:
        for row in cur:
            geom = row[-1]
            begin_msr = geom.firstPoint.M
            end_msr = geom.lastPoint.M
            row[0] = begin_msr
            row[1] = end_msr
            cur.updateRow(row)

    # Export event table to csv
    import pandas as pd
    import os
    data = [(row[0], row[1], row[2]) for row in arcpy.da.SearchCursor('memory/lrs_clip_explode', ['RTE_NM','BEGIN_MSR','END_MSR'])]
    df = pd.DataFrame(data, columns=(['RTE_NM','BEGIN_MSR','END_MSR']))
    df.to_csv(os.path.join(output_path, output_filename), index=False)