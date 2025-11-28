"""
lab7.py

Script for GEOG-392 Lab 07

Tasks implemented:
- Compute HillShade and Slope from a DEM (arcpy.ddd.HillShade, arcpy.ddd.Slope)
- Create RGB composite from LandSAT bands (arcpy.management.CompositeBands)
- Compute ESRI NDVI from NIR and RED bands using Raster math (arcpy.sa)

Usage:
    python lab7.py --dem <dem_folder_or_file> --landsat <landsat_folder> --out <output_folder> [--dry-run]

If no paths are provided the script will look for `DEM/` and `LandSAT/` folders next to this script.
"""
import os
import sys
import glob
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def find_first_tif(folder):
    if os.path.isfile(folder) and folder.lower().endswith('.tif'):
        return folder
    pattern = os.path.join(folder, '*.tif')
    files = sorted(glob.glob(pattern))
    return files[0] if files else None


def find_landsat_bands(folder):
    """Return dict with keys 'B1','B2','B3','B4' pointing to band file paths if present."""
    bands = {}
    # Accept common naming: *_B1.tif, *_B2.tif, etc (case-insensitive)
    for p in glob.glob(os.path.join(folder, '*.tif')):
        name = os.path.basename(p).upper()
        if '_B1' in name:
            bands['B1'] = p
        elif '_B2' in name:
            bands['B2'] = p
        elif '_B3' in name:
            bands['B3'] = p
        elif '_B4' in name:
            bands['B4'] = p
    return bands


def safe_mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def main():
    parser = argparse.ArgumentParser(description='Lab07 raster processing: DEM (hillshade/slope), LandSAT composite and NDVI')
    parser.add_argument('--dem', help='Path to DEM file or folder containing DEM tif')
    parser.add_argument('--landsat', help='Path to LandSAT folder containing band tifs')
    parser.add_argument('--out', help='Output folder (will be created if needed)')
    parser.add_argument('--dry-run', action='store_true', help='Print planned actions and exit')
    args = parser.parse_args()

    dem_input = args.dem or os.path.join(BASE_DIR, '..', 'Lab 7.1', 'DEM')
    landsat_input = args.landsat or os.path.join(BASE_DIR, '..', 'Lab 7.1', 'LandSAT')
    out_folder = args.out or os.path.join(BASE_DIR, 'outputs')

    dem_input = os.path.abspath(dem_input)
    landsat_input = os.path.abspath(landsat_input)
    out_folder = os.path.abspath(out_folder)

    print('DEM source:', dem_input)
    print('LandSAT source:', landsat_input)
    print('Output folder:', out_folder)

    dem_tif = find_first_tif(dem_input)
    if not dem_tif:
        print('ERROR: No DEM tif found at', dem_input)
        sys.exit(1)

    bands = find_landsat_bands(landsat_input)
    required = ['B1', 'B2', 'B3', 'B4']
    if not all(k in bands for k in required):
        print('ERROR: Could not find all required LandSAT bands (B1-B4) in', landsat_input)
        missing = [k for k in required if k not in bands]
        print('Missing:', missing)
        sys.exit(1)

    print('Found DEM:', dem_tif)
    for k in required:
        print(f'Found band {k}:', bands[k])

    if args.dry_run:
        print('\nDry-run: planned outputs:')
        print('  HillShade ->', os.path.join(out_folder, 'DEM_hillshade.tif'))
        print('  Slope     ->', os.path.join(out_folder, 'DEM_slope.tif'))
        print('  Composite ->', os.path.join(out_folder, 'LANDSAT_RGB.tif'))
        print('  NDVI      ->', os.path.join(out_folder, 'LANDSAT_NDVI_ESRI.tif'))
        return

    # Now import arcpy and run processing
    try:
        import arcpy
        from arcpy.sa import Raster
    except Exception as e:
        print('ERROR: ArcPy is required to run this script. ', e)
        sys.exit(1)

    # Ensure extensions
    try:
        if arcpy.CheckExtension('3D') == 'Available':
            arcpy.CheckOutExtension('3D')
        else:
            print('WARNING: 3D Analyst extension not available; HillShade/Slope may fail')
        if arcpy.CheckExtension('Spatial') == 'Available':
            arcpy.CheckOutExtension('Spatial')
        else:
            print('WARNING: Spatial Analyst extension not available; NDVI may fail')
    except Exception:
        pass

    arcpy.env.overwriteOutput = True
    safe_mkdir(out_folder)

    # DEM hillshade and slope
    hill_out = os.path.join(out_folder, 'DEM_hillshade.tif')
    slope_out = os.path.join(out_folder, 'DEM_slope.tif')
    try:
        print('\nRunning HillShade...')
        arcpy.ddd.HillShade(dem_tif, hill_out, 315, 45, 'NO_SHADOWS', 1)
        print('HillShade written to', hill_out)
    except Exception as ex:
        print('HillShade failed:', ex)

    try:
        print('\nRunning Slope...')
        arcpy.ddd.Slope(dem_tif, slope_out, 'DEGREE', 1)
        print('Slope written to', slope_out)
    except Exception as ex:
        print('Slope failed:', ex)

    # Composite RGB - order must be RED, GREEN, BLUE (B3, B2, B1)
    composite_out = os.path.join(out_folder, 'LANDSAT_RGB.tif')
    try:
        print('\nCreating RGB composite (RED, GREEN, BLUE)...')
        red = bands['B3']
        green = bands['B2']
        blue = bands['B1']
        arcpy.management.CompositeBands(f"{red};{green};{blue}", composite_out)
        print('Composite written to', composite_out)
    except Exception as ex:
        print('CompositeBands failed:', ex)

    # NDVI using ESRI formula: ((NIR - RED)/(NIR + RED))*100 + 100
    ndvi_out = os.path.join(out_folder, 'LANDSAT_NDVI_ESRI.tif')
    try:
        print('\nCalculating ESRI NDVI...')
        nir = Raster(bands['B4'])
        redr = Raster(bands['B3'])
        ndvi = ((nir - redr) / (nir + redr)) * 100 + 100
        ndvi.save(ndvi_out)
        print('NDVI written to', ndvi_out)
    except Exception as ex:
        print('NDVI calculation failed:', ex)

    # Check in extensions
    try:
        arcpy.CheckInExtension('3D')
    except Exception:
        pass
    try:
        arcpy.CheckInExtension('Spatial')
    except Exception:
        pass

    print('\nProcessing complete. Place screenshots into your PDF submission as required by the lab.')


if __name__ == '__main__':
    main()
