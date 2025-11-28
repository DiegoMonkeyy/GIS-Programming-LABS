import os, glob
import arcpy
from arcpy.sa import Raster

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dem = glob.glob(os.path.join(BASE_DIR, '..', 'Lab 7.1', 'DEM', '*.tif'))[0]
band1 = glob.glob(os.path.join(BASE_DIR, '..', 'Lab 7.1', 'LandSAT', '*_B1*.tif'))[0]
band2 = glob.glob(os.path.join(BASE_DIR, '..', 'Lab 7.1', 'LandSAT', '*_B2*.tif'))[0]
band3 = glob.glob(os.path.join(BASE_DIR, '..', 'Lab 7.1', 'LandSAT', '*_B3*.tif'))[0]
band4 = glob.glob(os.path.join(BASE_DIR, '..', 'Lab 7.1', 'LandSAT', '*_B4*.tif'))[0]

out = os.path.join(BASE_DIR, 'outputs')
os.makedirs(out, exist_ok=True)
arcpy.env.overwriteOutput = True

# HillShade
arcpy.ddd.HillShade(dem, os.path.join(out, 'DEM_hillshade.tif'), 315, 45, 'NO_SHADOWS', 1)

# Slope
arcpy.ddd.Slope(dem, os.path.join(out, 'DEM_slope.tif'), 'DEGREE', 1)

# Composite (RED=B3, GREEN=B2, BLUE=B1)
arcpy.management.CompositeBands(f"{band3};{band2};{band1}", os.path.join(out, 'LANDSAT_RGB.tif'))

# NDVI ESRI formula: ((NIR - RED)/(NIR + RED))*100 + 100
nir = Raster(band4)
red = Raster(band3)
ndvi = ((nir - red) / (nir + red)) * 100 + 100
ndvi.save(os.path.join(out, 'LANDSAT_NDVI_ESRI.tif'))
