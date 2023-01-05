# KML-Polygon-to-Points
Generates many points within the boundaries of given kml of a polygon

## How To Use:

* In google earth, enclose the area of interest with polygon and save it (the polygon) as a kml file.
eg: Area of interest maybe tentative catchment area to be properly deleneated or command area for contour mapping.

* Run the program. If the input polygon contains hundreds of edges, long run time is to be expected. The developers are looking to optimize the speed in subsequent versions.

* Give the generated *.kml file as input

* Select a suitable spacing (in degrees). In most applications, the default value is quite appropriate.

* Choose weather you want all points in a single file or multiple files
(Tip: if you want to obtain elevation information from the https://www.gpsvisualizer.com/elevation site, you might want to split into multiple files of 50 000 points each, which is the default, because it has been observed that files with large number of points requires a lot of time to convert to *.gpx format. You can later merge these in arcgis after creating feature files.)

* Outputs the same *.kml file(s) with all the generated points.


### Additional steps in arcGIS(if converted to *.gpx format):

* In arcGIS, search GPX to feature

* Input the *.gpx file downloaded from the aforementioned. Do this for each file in case you have multiple files.

* In case of multiple files, search merge and select all the *.shp files.
* Don't forget to interpolate using suitable method.
