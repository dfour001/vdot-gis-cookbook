#===============================================================================
# Get Field Min/Max/Sum/Average Values
#===============================================================================
# How do I get a list of minimum, maxmimum, sum, and average  values for each 
# number field in a feature class?
# 
# The function below will find each of the number fields in the input feature
# class and provide statistic values.
#===============================================================================
# Written for ArcGIS Pro in Python 3
# By Dan Fourquet
#===============================================================================

import arcpy
import pandas as pd

def get_field_statistics(featureClass, csvPath=None, scale=2):
    """ Calculates the minimum, maximum, sum, and average of each number field
        in the input feature class
        
        featureClass = The input feature class
        csvPath = Path to output CSV.  If None, results will only be printed
        scale = The number of digits to the right of the decimal.    
    """
    # Get list of number field names
    numberFieldTypes = ["Double","Integer","Single","SmallInteger"]
    fields = [field.name for field in arcpy.ListFields(featureClass) if field.type in numberFieldTypes]

    output = []
    for field in fields:
        print(f"Calculating field {field}")
        values = [row[0] for row in arcpy.da.SearchCursor(featureClass, field) if row[0] is not None]
        statMin = round(min(values), scale)
        statMax = round(max(values), scale)
        statSum = round(sum(values), scale)
        statAvg = round(statSum / len(values), scale)

        if scale == 0: # Stats will return as integers if scale == 0
            statMin = int(statMin)
            statMax = int(statMax)
            statSum = int(statSum)
            statAvg = int(statAvg)

        output.append({
            "field": field,
            "min": statMin,
            "max": statMax,
            "sum": statSum,
            "avg": statAvg
        })


    df = pd.DataFrame(output)
    print(df.to_string(index=False))
    
    if csvPath:
        df.to_csv(csvPath, index=False)



#===============================================================================
# Example - The statistics for an AADT layer will be printed
#===============================================================================

fc = "https://services6.arcgis.com/V7U0SOtZo77TJV8c/arcgis/rest/services/Truck_AADT/FeatureServer/0"

get_field_statistics(fc)