import os
import arcpy
from arcpy.sa import Raster

# Hardcoded absolute paths for DEM and LandSAT bands
DEM_PATH = r"C:\Users\diego\Downloads\Labs\GIS-Programming-LABS\LAB 7\Lab 7.1\DEM\n30_w097_1arc_v3.tif"
BAND_BLUE = r"C:\Users\diego\Downloads\Labs\GIS-Programming-LABS\LAB 7\Lab 7.1\LandSAT\LT05_L2SP_026039_20110803_20200820_02_T1_SR_B1.TIF"
BAND_GREEN = r"C:\Users\diego\Downloads\Labs\GIS-Programming-LABS\LAB 7\Lab 7.1\LandSAT\LT05_L2SP_026039_20110803_20200820_02_T1_SR_B2.TIF"
BAND_RED = r"C:\Users\diego\Downloads\Labs\GIS-Programming-LABS\LAB 7\Lab 7.1\LandSAT\LT05_L2SP_026039_20110803_20200820_02_T1_SR_B3.TIF"
BAND_NIR = r"C:\Users\diego\Downloads\Labs\GIS-Programming-LABS\LAB 7\Lab 7.1\LandSAT\LT05_L2SP_026039_20110803_20200820_02_T1_SR_B4.TIF"
OUTPUT_DIR = r"C:\Users\diego\Downloads\Labs\GIS-Programming-LABS\outputs"


os.makedirs(OUTPUT_DIR, exist_ok=True)
arcpy.env.overwriteOutput = True

print("Starting HillShade...")
try:
    arcpy.ddd.HillShade(
        DEM_PATH,
        os.path.join(OUTPUT_DIR, 'DEM_hillshade.tif'),
        315,  # azimuth
        45,   # altitude
        'NO_SHADOWS',
        1     # z_factor
    )
    print("HillShade completed.")
    print(arcpy.GetMessages())
except Exception as e:
    print("HillShade error:", e)

print("Starting Slope...")
try:
    arcpy.ddd.Slope(
        DEM_PATH,
        os.path.join(OUTPUT_DIR, 'DEM_slope.tif'),
        'DEGREE',
        1     # z_factor
    )
    print("Slope completed.")
    print(arcpy.GetMessages())
except Exception as e:
    print("Slope error:", e)

print("Starting RGB Composite...")
try:
    arcpy.management.CompositeBands(
        f"{BAND_RED};{BAND_GREEN};{BAND_BLUE}",
        os.path.join(OUTPUT_DIR, 'LANDSAT_RGB.tif')
    )
    print("RGB Composite completed.")
    print(arcpy.GetMessages())
except Exception as e:
    print("RGB Composite error:", e)

print("Starting NDVI Calculation...")
try:
    nir = Raster(BAND_NIR)
    red = Raster(BAND_RED)
    ndvi = ((nir - red) / (nir + red)) * 100 + 100
    ndvi.save(os.path.join(OUTPUT_DIR, 'LANDSAT_NDVI_ESRI.tif'))
    print("NDVI Calculation completed.")
    print(arcpy.GetMessages())
except Exception as e:
    print("NDVI Calculation error:", e)