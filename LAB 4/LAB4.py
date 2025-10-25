import arcpy
import os

path = os.getcwd()
arcpy.env.workspace = path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DB_PATH = os.path.join(BASE_DIR, 'Lab4_Data', 'Campus.gdb')
CSV_PATH = os.path.join(BASE_DIR, 'Lab4_Data', 'garages.csv')
OUTPUT_DB_PATH = os.path.join(BASE_DIR, 'Lab4_Data', 'Campus_Updated.gdb')

# make input GDB path as the base working path 
arcpy.env.workspace = INPUT_DB_PATH

# Create the output geodatabase in the Lab4_Data folder
output_folder = os.path.dirname(OUTPUT_DB_PATH)
output_gdb_name = os.path.basename(OUTPUT_DB_PATH)
arcpy.management.CreateFileGDB(output_folder, output_gdb_name)

arcpy.management.XYTableToPoint(BASE_DIR + '/Lab4_Data/garages.csv',
                               OUTPUT_DB_PATH + '/Garages_Updated',)

# Print spatial references before re-projection
print(arcpy.Describe("garages").spatialReference.name)
print(arcpy.Describe("Structures").spatialReference.name)

# re-project
target_ref = arcpy.SpatialReference("NAD 1983 UTM Zone 11N")
arcpy.management.Project(
   "garages",
   "structures_reprojected",
   target_ref
)

# print spatial references after re-projection
print(arcpy.Describe("******").spatialReference.name)
print(arcpy.Describe("******").spatialReference.name)