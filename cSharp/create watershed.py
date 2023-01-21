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
