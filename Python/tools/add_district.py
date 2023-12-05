#===============================================================================
# Add districts to input FC
#===============================================================================
# Given an input feature class (point, line, or polygon), this function will
# assign the district name to the input feature class based on its center point.
#
# If district_field does not exist in the input feature class, then it will
# be added.
#
# This can easily be modified to work with any other polygon layer, such as
# jurisdictions for example.
#===============================================================================
# Written for ArcGIS Pro in Python 3
# By Dan Fourquet
#===============================================================================

def add_districts(inputFC, districtFC, district_field="Districts", district_name_field="DISTRICT_NAME"):
    # Check if district_field_name exists in inputFC
    if district_field not in [field for field in arcpy.ListFields(inputFC)]:
        arcpy.AddField_management(inputFC, district_field, 'TEXT')

    # Get list of districts
    districts = [row[0] for row in arcpy.da.SearchCursor(districtFC, district_name_field)]

    # Add districts to inputFC by location
    for district in districts:
        arcpy.management.SelectLayerByAttribute(districtFC, 'NEW_SELECTION', f"{district_name_field} = '{district}'")
        arcpy.management.SelectLayerByLocation(inputFC, 'HAVE_THEIR_CENTER_IN', districtFC)

        with arcpy.da.UpdateCursor(inputFC, district_field) as cur:
            for row in cur:
                row[0] = district
                cur.updateRow(row)