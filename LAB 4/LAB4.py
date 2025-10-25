import arcpy
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

### >>>>>> Add your code here
INPUT_DB_PATH = os.path.join(BASE_DIR, 'Labs', 'GIS-Programming-LABS', 'LAB 4', 'Lab4_Data', 'Campus.gdb')
CSV_PATH = os.path.join(BASE_DIR, 'Labs', 'GIS-Programming-LABS', 'LAB 4', 'Lab4_Data', 'garages.csv')
OUTPUT_DB_PATH = os.path.join(BASE_DIR, 'Labs', 'GIS-Programming-LABS', 'LAB 4', 'Lab4_Data', 'Campus_Updated.gdb')
### <<<<<< End of your code here

arcpy.env.workspace = INPUT_DB_PATH

# Layers need to be kept
layers_to_keep = ["GaragePoints", "LandUse", "Structures", "Trees"]

# list all feature clases
feature_classes = arcpy.ListFeatureClasses()

# delete other classes
for fc in feature_classes:
    if fc not in layers_to_keep:
        arcpy.management.Delete(fc)

# create GDB management
if not os.path.exists(OUTPUT_DB_PATH):
    # Create the output file geodatabase
    out_folder = os.path.dirname(OUTPUT_DB_PATH)
    out_name = os.path.basename(OUTPUT_DB_PATH)
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    arcpy.management.CreateFileGDB(out_folder, out_name)

# Load .csv file to input GDB
### >>>>>> Add your code here
garages_fc_name = 'GaragePoints'
if not arcpy.Exists(os.path.join(INPUT_DB_PATH, garages_fc_name)):
    x_field = 'X'
    y_field = 'Y'
    if os.path.exists(CSV_PATH):
        arcpy.management.XYTableToPoint(CSV_PATH, os.path.join(INPUT_DB_PATH, garages_fc_name), x_field, y_field)
    else:
        print(f"CSV not found at {CSV_PATH}; skipping CSV->point conversion")
else:
    print(f"{garages_fc_name} already exists in the input geodatabase")
### <<<<<< End of your code here

# Print spatial references before re-projection
print(f"Before Re-Projection...")
print(f"garages layer spatial reference: {arcpy.Describe('GaragePoints').spatialReference.name}.")
print(f"Structures layer spatial reference: {arcpy.Describe('Structures').spatialReference.name}.")

# Re-project
## >>>>>>>>> change the codes below
TARGET_EPSG = 4326
target_ref = arcpy.SpatialReference(TARGET_EPSG)


structures_in = 'Structures'
structures_out = os.path.join(OUTPUT_DB_PATH, 'Structures_proj')
if arcpy.Exists(structures_out):
    arcpy.management.Delete(structures_out)
arcpy.management.Project(structures_in, structures_out, target_ref)


garages_in = 'GaragePoints'
garages_out = os.path.join(OUTPUT_DB_PATH, 'GaragePoints_proj')
if arcpy.Exists(garages_out):
    arcpy.management.Delete(garages_out)
arcpy.management.Project(garages_in, garages_out, target_ref)
## <<<<<<<< End of your code here
# print spatial references after re-projection
print(f"After Re-Projection...")
print(f"garages layer spatial reference: {arcpy.Describe(garages_out).spatialReference.name}.")
print(f"re-projected Structures layer spatial reference: {arcpy.Describe(structures_out).spatialReference.name}")

### >>>>>> Add your code here
# Buffer analysis
radiumStr = "150 meter"

buffers_out = os.path.join(OUTPUT_DB_PATH, 'GarageBuffers')
arcpy.analysis.Buffer(garages_out, buffers_out, radiumStr)

# Intersect analysis: intersect buffers with reprojected structures
intersect_out = os.path.join(OUTPUT_DB_PATH, 'Buffer_Structures_Intersect')
arcpy.analysis.Intersect([buffers_out, structures_out], intersect_out)

# Output features are written to the created GDB (OUTPUT_DB_PATH)
print(f"Output at {OUTPUT_DB_PATH}:")
for name in [structures_out, garages_out, buffers_out, intersect_out]:
    print(f" - {name}")
### <<<<<< End of your code here
