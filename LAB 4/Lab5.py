import os
import sys

# Try to import arcpy, but fail gracefully with a helpful message so the
# script can be run in non-ArcGIS environments for testing.
try:
    import arcpy
    ARCPY_AVAILABLE = True
except Exception:
    ARCPY_AVAILABLE = False

### >>>>>> Add your code here
"""
Here are some hints of what values the following variables should accept.
When running, the following code section will accept user input from terminal
Use `input()` method.

GDB_Folder = "***/Labs/Lab5"
GDB_Name = "Lab5.gdb"
Garage_CSV_File = "***/Labs/Lab5/garages.csv"
Garage_Layer_Name = "garages"
Campus_GDB = "***/Labs/Lab5/Campus.gdb"
Selected_Garage_Name = "Northside Parking Garage"
Buffer_Radius = "150 meter"
"""
### >>>>>> Add your code here
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Prompt the user only for the garage name; use a fixed buffer distance
Selected_Garage_Name = input("Enter the name of the garage to buffer: ").strip()
if not Selected_Garage_Name:
    print("No garage name provided. Exiting.")
    sys.exit(1)

# Fixed buffer radius for simplicity
Buffer_Radius = "150 Meters"

# Data and output paths
DATA_FOLDER = os.path.join(BASE_DIR, 'Lab4_Data')
# Source Campus geodatabase containing Structures
CAMPUS_GDB = os.path.join(DATA_FOLDER, 'Campus.gdb')
# Optional CSV path for garage points (unused in this script but kept for reference)
CSV_PATH = os.path.join(DATA_FOLDER, 'garages.csv')
# Output GDB for Lab5 results
LAB5_GDB = os.path.join(DATA_FOLDER, 'Lab5.gdb')




if not ARCPY_AVAILABLE:
    print("ArcPy module not available. This script requires ArcGIS Pro's Python environment.")
    print("Run this script inside an ArcGIS Pro Python environment or install ArcPy where available.")
    sys.exit(1)


if not arcpy.Exists(CAMPUS_GDB):
    print(f"Campus geodatabase not found at {CAMPUS_GDB}. Exiting.")
    sys.exit(1)


lab5_folder = os.path.dirname(LAB5_GDB)
# CreateFileGDB expects an output name (without extension) in some contexts,
# so strip the .gdb extension if present.
lab5_name = os.path.basename(LAB5_GDB)
lab5_name_no_ext = os.path.splitext(lab5_name)[0]

if not arcpy.Exists(LAB5_GDB):
    if not os.path.exists(lab5_folder):
        os.makedirs(lab5_folder)
    # Use the management tool to create the file geodatabase
    arcpy.management.CreateFileGDB(lab5_folder, lab5_name_no_ext)

# Feature class to query and clip
structures_fc = os.path.join(CAMPUS_GDB, 'Structures')
if not arcpy.Exists(structures_fc):
    print(f"Structures feature class not found in {CAMPUS_GDB}. Exiting.")
    sys.exit(1)

esc_name = Selected_Garage_Name.replace("'", "''")
where_clause = f"BldgName = '{esc_name}'"


found = False
try:
    # Use a data-access cursor for efficient attribute queries
    with arcpy.da.SearchCursor(structures_fc, ['BldgName'], where_clause) as cursor:
        for row in cursor:
            # row is a tuple; first element is BldgName
            if row[0] == Selected_Garage_Name:
                found = True
                break
except Exception as e:
    print(f"Error checking for building: {e}")
    sys.exit(1)

if not found:
    print(f"The specified garage '{Selected_Garage_Name}' does not exist in {structures_fc}.")
    sys.exit(1)


# Prepare in-memory intermediate names and sanitized output name
selected_in_memory = "in_memory/selected_garage"
buffer_in_memory = "in_memory/garage_buffer"

safe_name = ''.join(c if (c.isalnum() or c == '_') else '_' for c in Selected_Garage_Name)
clipped_out = os.path.join(LAB5_GDB, f"{safe_name}_structures_clipped")

# Remove any existing outputs to avoid "already exists" errors
for path in (selected_in_memory, buffer_in_memory, clipped_out):
    if arcpy.Exists(path):
        try:
            arcpy.management.Delete(path)
        except Exception:
            # best-effort cleanup; continue even if delete fails
            pass


try:
    # Allow outputs to be overwritten to avoid errors when rerunning
    arcpy.env.overwriteOutput = True
    
    # Select the garage by attribute into memory
    arcpy.analysis.Select(in_features=structures_fc, out_feature_class=selected_in_memory, where_clause=where_clause)
    print("Selected garage feature.")

    # Create buffer around the selected garage (distance specified by Buffer_Radius)
    arcpy.analysis.Buffer(in_features=selected_in_memory, out_feature_class=buffer_in_memory, buffer_distance_or_field=Buffer_Radius)
    print(f"Buffer created with distance {Buffer_Radius}.")

    # Clip Structures to the buffer and save result to Lab5.gdb
    arcpy.analysis.Clip(in_features=structures_fc, clip_features=buffer_in_memory, out_feature_class=clipped_out)
    print(f"Clipped structures written to: {clipped_out}")

    print('Success: Lab5 processing complete.')
except arcpy.ExecuteError:
   
    msgs = arcpy.GetMessages(2)
    print(f"ArcPy geoprocessing error:\n{msgs}")
    sys.exit(1)
except Exception as ex:
    print(f"Unexpected error: {ex}")
    sys.exit(1)
