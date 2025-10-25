import arcpy
import os
import arcpy
import os
import csv

# Basic paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DB_PATH = os.path.join(BASE_DIR, 'Lab4_Data', 'Campus.gdb')
CSV_PATH = os.path.join(BASE_DIR, 'Lab4_Data', 'garages.csv')
OUTPUT_DB_PATH = os.path.join(BASE_DIR, 'Lab4_Data', 'Campus_Updated.gdb')

# Use the input geodatabase as the workspace so feature class names can be used directly
arcpy.env.workspace = INPUT_DB_PATH

# Ensure output geodatabase exists
if not arcpy.Exists(OUTPUT_DB_PATH):
   out_folder = os.path.dirname(OUTPUT_DB_PATH)
   out_name = os.path.basename(OUTPUT_DB_PATH)
   arcpy.management.CreateFileGDB(out_folder, out_name)

def safe_describe(dataset):
   """Return Describe object or None if dataset doesn't exist in workspace."""
   try:
      return arcpy.Describe(dataset)
   except Exception:
      return None

def find_xy_fields(csv_path):
   """Try to detect X/Y field names in a CSV. Returns (x_field, y_field) or (None, None)."""
   try:
      with open(csv_path, newline='') as f:
         reader = csv.DictReader(f)
         fields = reader.fieldnames or []
   except Exception:
      return None, None

   candidates_x = ['x', 'X', 'lon', 'Lon', 'longitude', 'Longitude', 'LONG', 'east', 'EAST']
   candidates_y = ['y', 'Y', 'lat', 'Lat', 'latitude', 'Latitude', 'LAT', 'north', 'NORTH']
   x_field = next((c for c in candidates_x if c in fields), None)
   y_field = next((c for c in candidates_y if c in fields), None)
   return x_field, y_field

# Names we'll use
garages_fc_name = 'garages'
structures_fc_name = 'Structures'

# If 'garages' is not a feature class but we have a CSV, try to convert it to points
if not arcpy.Exists(os.path.join(INPUT_DB_PATH, garages_fc_name)):
   x_field, y_field = find_xy_fields(CSV_PATH)
   if x_field and y_field:
      print(f"Converting CSV to points using fields X='{x_field}', Y='{y_field}'")
      out_fc = os.path.join(INPUT_DB_PATH, 'garages_points')
      # XYTableToPoint(in_table, out_feature_class, x_field, y_field, {z_field}, {coordinate_system})
      arcpy.management.XYTableToPoint(CSV_PATH, out_fc, x_field, y_field)
      garages_fc_name = 'garages_points'
   else:
      print("Cannot find a point feature class named 'garages' in the geodatabase and no suitable X/Y fields found in the CSV.")

# Helper to print spatial reference name
def print_sr(name):
   desc = safe_describe(name)
   if desc and hasattr(desc, 'spatialReference'):
      print(f"{name} spatial reference: {desc.spatialReference.name}")
   else:
      print(f"{name} not found or has no spatial reference")

print("-- Before reprojection --")
print_sr(garages_fc_name)
print_sr(structures_fc_name)

# Target spatial reference: change the factory code (EPSG) or name as needed.
# Using 4326 (WGS 1984) as a common example. Replace with your desired target.
TARGET_EPSG = 4326
target_ref = arcpy.SpatialReference(TARGET_EPSG)

def project_if_needed(in_name, out_name):
   desc = safe_describe(in_name)
   if not desc:
      print(f"Skipping projection; {in_name} not found.")
      return None
   current_sr = desc.spatialReference
   if current_sr.name == target_ref.name or (hasattr(current_sr, 'factoryCode') and getattr(current_sr, 'factoryCode', None) == getattr(target_ref, 'factoryCode', None)):
      print(f"{in_name} already in target spatial reference ({target_ref.name}), skipping Project.")
      return in_name
   out_fc = os.path.join(OUTPUT_DB_PATH, out_name)
   print(f"Projecting {in_name} -> {out_fc} to {target_ref.name}")
   arcpy.management.Project(in_name, out_fc, target_ref)
   return out_fc

# Project garages and Structures (if they exist)
proj_garages = project_if_needed(garages_fc_name, garages_fc_name + '_proj')
proj_structures = project_if_needed(structures_fc_name, structures_fc_name + '_proj')

print("-- After reprojection --")
if proj_garages:
   # when using full path out_fc, Describe can accept it; give friendly name for printing
   print_sr(proj_garages)
if proj_structures:
   print_sr(proj_structures)

print('Done')