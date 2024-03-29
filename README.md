# VDOT GIS Cookbook
![](https://github.com/dfour001/vdot-gis-cookbook/blob/main/images/nook.png)
## Recipes
These are small snippets of code that will demonstrate how to accomplish a specific task.  Ideally they will be written in a way that they can be copied and pasted into a new program as needed.

### Python
#### arcpy (ArcGIS Pro)
- [Find MP of a point](https://github.com/dfour001/vdot-lrs-cookbook/blob/main/Python/arcpy/find_point_mp.py) - Given a point geometry and rte_nm, how do I find the MP on the LRS?
- [Find Begin and End MP of a Line](https://github.com/dfour001/vdot-lrs-cookbook/blob/main/Python/arcpy/find_line_mp.py) - Given a line geometry, how do I find the begin and end point of the line on the LRS?
- [Match Point to RTE_NM](https://github.com/dfour001/vdot-lrs-cookbook/blob/main/Python/arcpy/match_point_to_rte_nm.py) - How can I determine the RTE_NM that a point belongs to?
- [Match Line to RTE_NM](https://github.com/dfour001/vdot-lrs-cookbook/blob/main/Python/arcpy/match_line_to_rte_nm.py) - How can I determine the RTE_NM that a line belongs to?


#### GeoPandas
- [Load LRS into GeoPandas](https://github.com/dfour001/vdot-lrs-cookbook/blob/main/Python/GeoPandas/lrs_in_geopandas.py) - How do I bring the LRS and m-values into a GeoPandas script?
- [Selecting routes within a distance of a point](https://github.com/dfour001/vdot-lrs-cookbook/blob/main/Python/GeoPandas/select_nearby_routes.py) - How do find the rte_nm values in the lrs within a specific distance of a point?


#### Misc Python
- [Setting up logging](https://github.com/dfour001/vdot-lrs-cookbook/blob/main/Python/misc/logging_setup.py) - How do I use the logging module to write to a log file?
- [Sort list of class instances](https://github.com/dfour001/vdot-lrs-cookbook/blob/main/Python/misc/class_sorting.py) - How do I sort a list of class instances by an attribute?


## VDOT Tools
These are functions that can be copy/pasted into scripts that perform workflows that I often run into while doing GIS work at VDOT.
- [Add districts to input feature class](https://github.com/dfour001/vdot-lrs-cookbook/blob/main/Python/tools/add_district.py) - Given an input feature class (point, line, or polygon), this function will assign the district name to the input feature class based on its center point.
- [Flip Event Table](https://github.com/dfour001/vdot-lrs-cookbook/blob/main/Python/tools/flip_event_table.py) - This will "flip" events in a table that is only entered on the prime direction so that the output event table will have events in both directions.


## ArcGIS Pro Python Window Functions
These are functions that can be copy/pasted into the python window of ArcGIS Pro.
- [Open Google StreetView on line centerpoint](https://github.com/dfour001/vdot-lrs-cookbook/blob/main/Python/ProFunctions/StreetviewFromLine.py) - With a single segment of a specified line selected, this function will open the midpoint of that line in Google StreetView in a new browser window.
- [Zoom to a layer extent](https://github.com/dfour001/vdot-lrs-cookbook/blob/main/Python/ProFunctions/zoom_to_layer_extent.py) - This function will zoom the active map's extent to the selected features of the input layer.
- [Get Field Min/Max/Sum/Average Values](https://github.com/dfour001/vdot-lrs-cookbook/blob/main/Python/ProFunctions/GetFieldMinMaxValues.py) - This function will find each of the number fields in the input feature class and provide statistic values.
- [Single Line to Single LRS Route](https://github.com/dfour001/vdot-lrs-cookbook/blob/main/Python/ProFunctions/single_line_to_single_route.py) - This function will allow you to select a single polyline feature in one layer and a single route in the LRS layer.


## Conflation Resources
Data conflation is the bane of DOT GIS analysts.  You may have great data in one network dataset and need to match it with data in another network dataset, but how do you match the data between the two networks?  Like the foolish alchemist's attempts to turn lead into gold, I'm trying to create an automated conflation tool of reasonable accuracy.  Here are some resources showing methods that others have successfully used and that I have found helpful.
- [The ABC’s of Conflation: TMC, LRS, OSM – What Happens When You Muck It Up](https://www.youtube.com/watch?v=LXweP-jKMoA) - A presentation from the Eastern Transportation Coalition with multiple conflation methods.
- [An optimisation model for linear feature matching in geographical data conflation](https://people.geog.ucsb.edu/~good/papers/510.pdf)
- [Automatic and Accurate Conflation of Different Road-Network Vector Data towards Multi-Modal Navigation](https://www.mdpi.com/2220-9964/5/5/68/htm)
- [A Conflation Methodology for Two GIS Roadway Networks and Its Application in Performance Measurements](https://journals.sagepub.com/doi/full/10.1177/0361198118793000)


## Online Courses
This section isn't specific to VDOT, but lists free online courses that are relevant to a GIS analyst at VDOT

- [The Nature of Geographic Information](https://www.e-education.psu.edu/natureofgeoinfo/) - An "Open Geospatial Textbook" that promotes understanding of the Geographic Information Science and Technology enterprise (GIS&T, also known as "geospatial").
- [Spatial Data Analytics for Transportation](https://www.e-education.psu.edu/geog855/node/508) - From Penn State, this course explores the important role GIS plays in the transportation industry. This interdisciplinary field is often referred to GIS-T. There is a natural synergy between GIS and transportation and, as a result, GIS-T has given rise to a number of specialized techniques and a wide variety of applications.
- [Earth Lab](https://www.earthdatascience.org/courses/) - This site hosts resources developed by Earth Lab at University of Colorado, Boulder. This website contains tutorials course lessons and blog posts related to earth data science. Most of the data tutorials will teach you important R and Python techniques relevant to earth data analytics, including geospatial, social, biological, and earth systems data.
### Python
- [Advanced Python Programming for GIS](https://www.e-education.psu.edu/geog489/home.html) - This course from Penn State covers advanced applications of Python for developing and customizing GIS software, designing user interfaces, and solving complex geoprocessing tasks, on both proprietary and open source platforms. 
- [Geo-Python](https://geo-python-site.readthedocs.io/en/latest/) - Part 1 of the University of Helsinki's course on Python GIS programming
- [Automating GIS-processes](https://autogis-site.readthedocs.io/en/latest/) - Part 2 of the University of Helsinki's course on Python GIS programming
