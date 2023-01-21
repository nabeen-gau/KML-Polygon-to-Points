import functools
import os
def child_files(directory):
    prepend_dir = functools.partial(os.path.join, directory)

    for file_name in os.listdir(directory):
        if os.path.isfile(prepend_dir(file_name)):
            yield prepend_dir(os.path.relpath(file_name))
workingDirectory = "D:/Pulchowk/_Research/01112023/"
def files():
    return list(child_files(workingDirectory))
gpxFiles = list(filter(lambda f: os.path.splitext(f)[1] == ".gpx", list(files())))
for i, t in enumerate(gpxFiles):
    arcpy.GPXtoFeatures_conversion(Input_GPX_File=t, Output_Feature_class= workingDirectory + "Fea" + str(i) + ".shp" )
'''
shpFiles = list(filter(lambda f: os.path.splitext(f)[1] == ".shp", list(files())))
mergeInputext = ""
for i in len(shpFiles):
    mergeInputext = mergeInputext + "Fea" + i +";"
mergeInputext = mergeInputext[:-1]
arcpy.Merge_management(inputs=mergeInputext, output=workingDirectory+"mergedFea.shp", field_mappings='Id "Id" true true false 6 Long 0 6 ,First,#,Fea1,Id,-1,-1,Fea2,Id,-1,-1;Name "Name" true true false 254 Text 0 0 ,First,#,Fea1,Name,-1,-1,Fea2,Name,-1,-1;Descript "Descript" true true false 254 Text 0 0 ,First,#,Fea1,Descript,-1,-1,Fea2,Descript,-1,-1;Type "Type" true true false 254 Text 0 0 ,First,#,Fea1,Type,-1,-1,Fea2,Type,-1,-1;Comment "Comment" true true false 254 Text 0 0 ,First,#,Fea1,Comment,-1,-1,Fea2,Comment,-1,-1;Symbol "Symbol" true true false 254 Text 0 0 ,First,#,Fea1,Symbol,-1,-1,Fea2,Symbol,-1,-1;DateTimeS "DateTimeS" true true false 254 Text 0 0 ,First,#,Fea1,DateTimeS,-1,-1,Fea2,DateTimeS,-1,-1;Elevation "Elevation" true true false 19 Double 0 0 ,First,#,Fea1,Elevation,-1,-1,Fea2,Elevation,-1,-1')'''
# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "mergedFea"
arcpy.gp.Idw_sa("mergedFea", "Elevation", workingDirectory + "IDWmer", "1.19200000000001E-03", "2", "VARIABLE 12", "")
# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "IDWmer"
arcpy.gp.Fill_sa("IDWmer", workingDirectory + "fill", "")
# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "fill"
arcpy.gp.FlowDirection_sa("fill", workingDirectory + "flowdir", "NORMAL", "", "D8")
# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "flowdir"
arcpy.gp.FlowAccumulation_sa("flowdir", workingDirectory + "accum", "", "FLOAT", "D8")
# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "raptifeature", "accum"
arcpy.gp.SnapPourPoint_sa("raptifeature", "accum", workingDirectory + "snap", "0", "Elevation")
# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "flowdir", "snap"
arcpy.gp.Watershed_sa("flowdir", "snap", workingDirectory + "shed", "VALUE")
# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "shed"
arcpy.RasterToPolygon_conversion(in_raster="shed", out_polygon_features=workingDirectory + "shedpoly01102023.shp", simplify="SIMPLIFY", raster_field="VALUE", create_multipart_features="SINGLE_OUTER_PART", max_vertices_per_feature="")
# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "shedpoly01102023"
arcpy.LayerToKML_conversion(layer="shedpoly01102023", out_kmz_file=workingDirectory + "shedpoly01102023.kmz", layer_output_scale="0", is_composite="NO_COMPOSITE", boundary_box_extent="DEFAULT", image_size="1024", dpi_of_client="96", ignore_zvalue="CLAMPED_TO_GROUND")
