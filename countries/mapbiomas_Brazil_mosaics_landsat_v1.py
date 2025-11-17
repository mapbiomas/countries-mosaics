# Import Google Earth Engine and system libraries
import ee
import sys
import os

# Add parent directory and mapbiomas-mosaics directory to the Python path
# This allows importing custom modules from these locations
sys.path.append(os.path.abspath('../'))
sys.path.append(os.path.abspath('..\\mapbiomas-mosaics'))

# Import custom modules for mosaic processing
from modules.Mosaic import *
from modules.DataType import *
from modules.BandNames import *
from modules.Collection import *
from modules.SmaAndNdfi import *
from modules.Miscellaneous import *
from modules.SpectralIndexes import *
from modules.CloudAndShadowMaskC2 import *

# Prevent Python from writing .pyc files
sys.dont_write_bytecode = True

# Initialize Google Earth Engine with the MapBiomas Paraguay project
ee.Initialize(project = "mapbiomas-paraguay")

# Version number for the mask assets
versionMasks = '2'

# Asset path for the grid/carta system (map sheets)
gridsAsset = 'projects/mapbiomas-workspace/AUXILIAR/cartas'

# Asset path for Landsat masks
assetMasks = "projects/mapbiomas-workspace/AUXILIAR/landsat-mask"

# List of biome names to process (without spaces)
# Currently only MATAATLANTICA is active, others are commented out
biomeNames = [
    # 'AMAZONIA',
    # 'CAATINGA',
    'MATAATLANTICA',
    # 'CERRADO',
    # 'PAMPA',
    # 'PANTANAL',
]

# Version numbers for each biome's processing
version = {
    'CAATINGA': '1',
    'CERRADO': '1',
    'MATAATLANTICA': '1',
    'PAMPA': '1',
    'PANTANAL': '1',
    'AMAZONIA': '1',
}

# Data filtering parameters for each biome
# Defines the optimal date ranges and cloud cover thresholds for each biome
dataFilter = {
    'CAATINGA': {
        'dateStart': '01-01',  # Start of date range (month-day)
        'dateEnd': '06-30',    # End of date range (month-day)
        'cloudCover': 80       # Maximum cloud cover percentage
    },
    'CERRADO': {
        'dateStart': '04-01',
        'dateEnd': '09-30',
        'cloudCover': 50
    },
    'MATAATLANTICA': {
        'dateStart': '04-01',
        'dateEnd': '10-31',
        'cloudCover': 80
    },
    'PAMPA': {
        'dateStart': '09-01',
        'dateEnd': '11-30',
        'cloudCover': 80
    },
    'PANTANAL': {
        'dateStart': '01-01',
        'dateEnd': '12-31',
        'cloudCover': 100
    },
    'AMAZONIA': {
        'dateStart': '01-01',
        'dateEnd': '12-31',
        # 'dateStart': '06-01',  # Alternative date range (commented)
        # 'dateEnd': '10-31',
        'cloudCover': 50
    },
}

# Dictionary containing grid names (map sheet codes) for each biome
# These are standardized Brazilian cartographic grid codes
gridNames = {
    "AMAZONIA": [
        # teste
        # "SC-21-X-C",
        # "SB-20-Z-B", "SB-20-Z-C", "SB-20-Z-D", "SB-21-V-D",
        # "SB-21-X-C", "SB-21-X-D", "SB-21-Y-A", "SB-21-Y-B",
        # "SB-21-Y-C", "SB-21-Y-D", "SB-21-Z-A", "SB-21-Z-B",
        # "SB-21-Z-C", "SB-21-Z-D", "SC-20-X-A", "SC-20-X-B",
        # "SC-21-V-B", "SC-21-X-A", "SC-21-X-B"
        # #
        # Complete list of grid codes for the Amazon biome
        "SB-23-V-D", "SB-23-X-A", "SB-23-V-B", "SA-23-Y-D",
        "SA-23-Z-C", "SA-23-Z-B", "SA-23-X-C", "SA-23-Z-A",
        "SA-23-Y-B", "SA-23-V-D", "SA-23-V-B", "NB-22-Y-D",
        "NA-22-V-B", "NA-22-X-A", "NA-22-X-C", "NA-22-Z-A",
        "SA-23-V-A", "NA-22-Z-D", "SA-22-X-B", "NA-22-Z-C",
        "SA-22-X-A", "NA-22-Y-D", "SA-22-V-B", "SA-22-V-A",
        "NA-22-Y-C", "NA-22-Y-B", "NA-22-Y-A", "NA-22-V-D",
        "NA-22-V-C", "NA-21-Z-B", "NA-21-X-D", "NA-21-Z-D",
        "SA-21-X-B", "SA-21-X-A", "NA-21-Z-C", "NA-21-Z-A",
        "NA-21-X-C", "NA-21-Y-B", "NA-21-V-D", "NA-21-Y-D",
        "SA-21-V-B", "SA-21-V-A", "NA-21-Y-C", "NA-21-Y-A",
        "SA-20-X-B", "NA-20-Z-D", "NA-20-Z-B", "NA-20-X-D",
        "NA-21-V-C", "NA-21-V-A", "NA-20-X-B", "NB-20-Z-D",
        "NB-21-Y-C", "NB-20-Z-B", "NB-21-Y-A", "NB-20-Z-C",
        "NB-20-Y-D", "NB-20-Y-C", "NA-20-V-A", "NA-19-X-D",
        "NA-20-V-D", "NA-20-V-B", "NA-20-X-A", "NA-20-X-C",
        "NA-20-Y-B", "NA-20-Z-A", "NA-20-Z-C", "SA-20-X-A",
        "SA-20-V-B", "NA-20-Y-D", "SA-20-V-A", "NA-20-Y-C",
        "NA-20-Y-A", "NA-19-Z-B", "NA-19-Z-D", "SA-19-X-B",
        "SA-19-X-A", "NA-19-Z-C", "NA-19-Z-A", "SA-19-V-B",
        "NA-19-Y-D", "NA-19-Y-B", "NA-19-X-C", "SC-19-Y-D",
        "SC-19-Y-A", "SC-19-Y-B", "SC-19-V-D", "SC-19-Z-A",
        "SC-19-X-C", "SC-19-Z-C", "SC-19-Z-B", "SC-19-X-D",
        "SC-19-X-B", "SC-19-X-A", "SC-19-V-B", "SB-19-Z-C",
        "SB-19-Y-D", "SB-19-Z-D", "SB-19-Z-A", "SB-19-Z-B",
        "SB-19-X-C", "SB-19-X-D", "SB-19-X-A", "SB-19-X-B",
        "SB-19-Y-B", "SB-19-V-D", "SB-19-V-B", "SB-19-Y-C",
        "SB-19-Y-A", "SB-19-V-C", "SB-19-V-A", "SB-18-Z-B",
        "SB-18-X-D", "SB-18-X-B", "SB-18-Z-D", "SC-18-X-B",
        "SC-19-V-A", "SC-19-V-C", "SC-18-X-D", "SC-18-X-A",
        "SB-18-Z-C", "SB-18-Z-A", "SA-19-V-D", "SA-19-Y-B",
        "SA-19-Y-D", "SA-19-Z-A", "SA-19-Z-C", "SA-19-Z-D",
        "SA-19-Z-B", "SA-19-X-D", "SA-19-X-C", "SA-20-V-C",
        "SA-20-Y-A", "SA-20-Y-B", "SA-20-V-D", "SA-20-X-C",
        "SA-20-X-D", "SA-20-Z-A", "SA-20-Z-B", "SA-20-Y-D",
        "SA-20-Z-C", "SA-20-Z-D", "SB-20-X-A", "SB-20-X-B",
        "SB-20-V-B", "SB-20-V-A", "SA-20-Y-C", "SB-20-V-C",
        "SB-20-V-D", "SB-20-Y-A", "SB-20-Y-B", "SB-20-Y-D",
        "SB-20-Y-C", "SC-20-V-A", "SC-20-V-C", "SC-20-V-D",
        "SC-20-V-B", "SB-20-Z-A", "SB-20-Z-C", "SC-20-X-A",
        "SC-20-X-C", "SC-20-X-D", "SC-20-X-B", "SB-20-Z-D",
        "SB-20-Z-B", "SB-20-X-C", "SB-20-X-D", "SB-21-V-C",
        "SB-21-V-A", "SB-21-V-B", "SB-21-V-D", "SB-21-Y-A",
        "SB-21-Y-B", "SB-21-Y-C", "SC-21-V-C", "SC-21-V-A",
        "SC-21-V-B", "SC-21-V-D", "SB-21-Y-D", "SB-21-Z-A",
        "SB-21-Z-C", "SC-21-X-A", "SC-21-X-B", "SB-21-Z-D",
        "SB-21-Z-B", "SB-21-X-C", "SB-21-X-D", "SB-21-X-A",
        "SB-21-X-B", "SA-21-Z-C", "SA-21-Z-D", "SA-21-Z-B",
        "SA-21-Z-A", "SA-21-Y-D", "SA-21-Y-B", "SA-21-Y-C",
        "SA-21-Y-A", "SA-21-V-D", "SA-21-V-C", "SA-21-X-C",
        "SA-21-X-D", "SA-22-V-C", "SB-22-V-A", "SA-22-Y-C",
        "SA-22-Y-A", "SA-22-V-D", "SA-22-Y-B", "SA-22-Y-D",
        "SB-22-V-B", "SA-22-Z-A", "SA-22-Z-C", "SA-22-X-C",
        "SA-22-X-D", "SA-23-V-C", "SA-23-Y-A", "SA-23-Y-C",
        "SA-22-Z-D", "SA-22-Z-B", "SB-22-X-A", "SB-22-X-B",
        "SB-22-X-C", "SB-22-X-D", "SB-23-V-C", "SB-23-V-A",
        "SB-23-Y-A", "SB-22-Z-D", "SC-22-X-B", "SB-22-Z-B",
        "SB-22-Z-A", "SB-22-Z-C", "SC-22-X-A", "SB-22-Y-D",
        "SC-22-V-B", "SC-22-V-A", "SB-22-Y-C", "SB-22-Y-B",
        "SB-22-Y-A", "SB-22-V-D", "SB-22-V-C", "SC-21-X-D",
        "SC-22-V-C", "SC-22-Y-A", "SC-21-Z-B", "SC-22-Y-C",
        "SC-21-Z-D", "SD-21-X-B", "SD-21-X-D", "SD-22-V-A",
        "SD-22-V-C", "SC-22-Y-B", "SC-22-Y-D", "SD-22-V-B",
        "SD-22-V-D", "SC-22-Z-A", "SC-22-X-C", "SC-22-V-D",
        "SC-22-X-D", "SE-21-V-B", "SE-21-V-A", "SD-21-Y-C",
        "SD-21-Y-D", "SE-20-X-B", "SD-20-Z-D", "SD-20-Z-B",
        "SD-21-Y-A", "SD-21-Y-B", "SD-21-V-D", "SD-21-X-C",
        "SD-21-Z-A", "SD-21-Z-C", "SD-21-X-A", "SD-21-V-B",
        "SC-21-Y-D", "SC-21-Z-C", "SC-21-Z-A", "SC-21-X-C",
        "SC-21-Y-B", "SC-21-Y-C", "SC-21-Y-A", "SC-20-Z-B",
        "SC-20-Z-D", "SD-20-X-B", "SD-20-X-D", "SD-21-V-A",
        "SD-21-V-C", "SD-20-X-C", "SD-20-V-B", "SD-20-X-A",
        "SC-20-Z-C", "SC-20-Z-A", "SC-20-Y-B", "SC-20-Y-D",
        "SD-20-V-A", "SC-20-Y-C", "SC-20-Y-A"
    ],
    "CERRADO": [
        # Grid codes for Cerrado biome
        "SF-23-V-D", "SF-23-X-A", "SF-23-V-B", "SE-23-Y-D",
        "SE-23-Z-C", "SE-23-Z-D", "SE-23-Z-A", "SE-23-Y-B",
        "SE-23-X-C", "SE-23-V-D", "SE-23-V-B", "SE-23-X-A",
        "SE-23-X-D", "SE-23-Z-B", "SE-23-X-B", "SD-23-X-B",
        "SD-23-X-D", "SD-24-Y-A", "SD-23-Z-B", "SD-24-Y-C",
        "SE-24-V-A", "SD-23-Z-D", "SD-23-Z-A", "SD-23-Z-C",
        "SD-23-Y-D", "SD-23-Y-B", "SD-23-X-C", "SD-23-V-D",
        "SD-23-V-B", "SD-23-X-A", "SC-23-Z-C", "SC-23-Y-D",
        "SC-23-Z-A", "SC-23-Y-B", "SC-23-X-C", "SC-23-V-D",
        "SB-23-Z-D", "SB-23-Z-C", "SC-23-X-A", "SC-23-V-B",
        "SB-23-Y-D", "SB-23-Y-B", "SB-23-Z-A", "SB-23-Z-B",
        "SB-23-X-D", "SB-23-X-C", "SB-23-V-D", "SB-23-X-A",
        "SB-23-V-B", "SA-23-Z-C", "SB-23-X-B", "SA-23-Z-D",
        "SB-24-V-C", "SB-24-V-A", "SA-24-Y-C", "SB-24-Y-A",
        "SA-24-Y-A", "SA-23-Z-B", "SA-23-Z-A", "SB-22-X-D",
        "SB-23-V-C", "SB-23-Y-A", "SB-23-Y-C", "SB-22-Z-D",
        "SC-22-X-B", "SB-22-Z-B", "SB-22-Z-C", "SC-22-X-A",
        "SD-21-X-B", "SD-21-X-D", "SD-22-V-C", "SC-22-Y-B",
        "SC-22-Y-D", "SD-22-V-B", "SD-22-V-D", "SC-22-Z-C",
        "SD-22-X-A", "SC-22-Z-A", "SC-22-X-C", "SC-22-X-D",
        "SC-22-Z-B", "SC-23-V-C", "SC-23-Y-A", "SC-23-V-A",
        "SC-23-Y-C", "SD-23-V-A", "SD-22-X-B", "SC-22-Z-D",
        "SD-22-X-C", "SD-22-X-D", "SD-22-Z-A", "SD-22-Z-B",
        "SD-22-Z-C", "SD-22-Z-D", "SD-23-Y-A", "SD-23-V-C",
        "SD-23-Y-C", "SE-23-V-A", "SE-23-V-C", "SE-22-X-B",
        "SE-22-X-D", "SE-22-X-A", "SE-22-X-C", "SE-22-V-D",
        "SE-22-V-B", "SE-22-Y-B", "SE-22-Y-A", "SE-22-V-C",
        "SE-22-V-A", "SD-22-Y-D", "SD-22-Y-C", "SD-22-Y-B",
        "SD-22-Y-A", "SE-21-X-B", "SD-21-Z-D", "SD-21-Z-B",
        "SE-21-X-D", "SE-21-Z-B", "SE-21-Z-C", "SE-21-X-A",
        "SE-21-V-B", "SE-21-Y-D", "SD-21-Y-C", "SD-21-Y-D",
        "SD-21-Y-A", "SD-21-Y-B", "SD-21-V-D", "SD-21-X-C",
        "SD-21-Z-A", "SD-21-Z-C", "SD-21-X-A", "SD-21-V-B",
        "SC-21-Y-D", "SC-21-Y-C", "SD-20-X-B", "SD-21-V-A",
        "SD-21-V-C", "SG-21-X-B", "SF-21-Z-C", "SF-21-Z-D",
        "SF-21-Z-A", "SF-21-Z-B", "SF-21-X-C", "SF-21-X-D",
        "SF-21-Y-B", "SF-21-V-D", "SF-21-V-B", "SF-21-X-A",
        "SF-21-X-B", "SE-21-Z-D", "SE-22-Y-C", "SF-22-V-A",
        "SF-22-V-C", "SF-22-Y-A", "SF-22-V-D", "SF-22-V-B",
        "SF-22-Y-B", "SF-22-Z-A", "SF-22-Z-C", "SF-22-X-A",
        "SE-22-Z-C", "SE-22-Z-A", "SE-22-Y-D", "SE-22-Z-B",
        "SE-22-Z-D", "SF-22-X-B", "SE-23-Y-A", "SE-23-Y-C",
        "SF-23-V-A", "SF-23-V-C", "SF-23-Y-A", "SF-22-X-D",
        "SF-22-Z-B", "SF-22-Z-D", "SG-22-X-A", "SG-22-X-B",
        "SF-23-Y-C"
    ],
    "CAATINGA": [
        # Grid codes for Caatinga biome
        "SE-23-V-B", "SE-23-X-A", "SE-23-X-B", "SB-25-V-C",
        "SB-25-Y-A", "SB-25-Y-C", "SC-25-V-A", "SC-24-X-D",
        "SC-24-Z-B", "SC-24-X-B", "SC-24-X-A", "SC-24-X-C",
        "SC-24-V-B", "SC-24-V-D", "SC-24-Z-A", "SC-24-Y-B",
        "SC-24-Z-C", "SD-24-X-A", "SC-24-Y-D", "SD-24-V-B",
        "SD-24-Y-B", "SD-24-V-D", "SD-24-V-A", "SD-24-V-C",
        "SD-23-X-B", "SD-23-X-D", "SD-24-Y-A", "SD-23-Z-B",
        "SD-24-Y-C", "SD-23-Z-D", "SD-23-Z-A", "SD-23-Z-C",
        "SD-23-Y-D", "SD-23-X-C", "SD-23-X-A", "SC-23-Z-C",
        "SC-23-Z-A", "SC-23-X-C", "SC-23-Z-B", "SC-23-Z-D",
        "SC-23-X-D", "SC-24-Y-C", "SC-24-Y-A", "SC-24-V-C",
        "SC-23-X-B", "SC-24-V-A", "SB-24-Y-C", "SB-23-Z-D",
        "SB-23-Z-C", "SC-23-X-A", "SB-23-Z-B", "SB-24-V-C",
        "SB-24-V-A", "SA-24-Y-C", "SB-24-V-B", "SA-24-Y-D",
        "SB-24-V-D", "SB-24-Y-A", "SB-24-Y-B", "SB-24-Y-D",
        "SB-24-Z-C", "SB-24-Z-A", "SB-24-Z-B", "SB-24-Z-D",
        "SB-24-X-D", "SB-24-X-B", "SB-24-X-A", "SA-24-Z-C",
        "SB-24-X-C", "SA-24-Y-B", "SA-24-Y-A"
    ],
    "MATAATLANTICA": [
        "SC-20-Y-A" # carta falsa para teste
        # Complete list of Mata Atlântica grids (commented out)
        # "SG-23-V-B", "SF-23-Y-D", "SF-23-Z-C", "SF-24-Y-C",
        # "SF-23-Z-D", "SF-23-Z-B", "SF-23-X-D", "SF-24-Y-A",
        # "SF-23-X-C", "SF-23-Z-A", "SF-23-Y-B", "SF-23-V-D",
        # "SF-23-X-A", "SF-23-V-B", "SE-23-Y-D", "SE-23-Z-C",
        # "SF-23-X-B", "SE-23-Z-D", "SE-23-Z-A", "SE-23-X-D",
        # "SE-23-Z-B", "SE-23-X-B", "SE-24-Y-C", "SE-24-Y-A",
        # "SE-24-V-C", "SE-24-Y-B", "SE-24-V-D", "SE-24-Y-D",
        # "SF-24-V-A", "SF-24-V-B", "SF-24-V-C", "SB-25-V-C",
        # "SB-25-Y-A", "SB-25-Y-C", "SC-25-V-A", "SC-25-V-C",
        # "SC-24-X-D", "SC-24-Z-B", "SC-24-Z-D", "SC-24-X-B",
        # "SC-24-Z-A", "SC-24-Z-C", "SD-24-X-A", "SC-24-Y-D",
        # "SD-24-V-B", "SD-24-X-C", "SD-24-Z-C", "SE-24-X-A",
        # "SE-24-V-B", "SD-24-Y-D", "SD-24-Y-B", "SD-24-Z-A",
        # "SD-24-V-D", "SD-24-V-C", "SD-24-Y-A", "SD-24-Y-C",
        # "SE-24-V-A", "SD-23-Z-D", "SE-22-X-D", "SE-22-Y-B",
        # "SH-21-X-D", "SH-21-X-B", "SG-21-Z-D", "SG-21-X-D",
        # "SG-21-X-B", "SF-21-Z-D", "SF-21-Z-B", "SF-21-X-D",
        # "SF-22-V-C", "SF-22-Y-A", "SF-22-Y-C", "SF-22-V-D",
        # "SF-22-V-B", "SF-22-Y-B", "SF-22-Y-D", "SF-22-X-C",
        # "SF-22-Z-A", "SF-22-Z-C", "SF-22-X-A", "SE-22-Z-C",
        # "SE-22-Z-A", "SE-22-Y-D", "SE-22-Z-B", "SE-22-Z-D",
        # "SF-22-X-B", "SE-23-Y-C", "SF-23-V-A", "SF-23-V-C",
        # "SF-23-Y-A", "SF-22-X-D", "SF-22-Z-B", "SF-22-Z-D",
        # "SG-22-X-A", "SG-22-X-B", "SG-22-X-C", "SG-22-X-D",
        # "SF-23-Y-C", "SG-23-V-A", "SG-23-V-C", "SG-22-Z-B",
        # "SG-22-Z-D", "SG-22-Z-A", "SG-22-Z-C", "SH-22-X-A",
        # "SG-22-Y-D", "SG-22-Y-B", "SH-22-V-B", "SH-22-V-A",
        # "SG-22-Y-C", "SG-22-Y-A", "SG-22-V-D", "SG-22-V-B",
        # "SG-22-V-A", "SG-22-V-C", "SH-22-V-C", "SH-22-X-C",
        # "SH-22-V-D", "SH-22-X-B", "SH-22-X-D"
    ],
    "PANTANAL": [
        # Grid codes for Pantanal biome
        "SE-21-X-B", "SE-21-X-D", "SE-21-Z-B", "SE-21-Z-C",
        "SE-21-Z-A", "SE-21-X-C", "SE-21-X-A", "SE-21-Y-B",
        "SE-21-V-D", "SE-21-V-B", "SE-21-Y-D", "SE-21-V-A",
        "SD-21-Y-C", "SD-21-Y-D", "SD-21-Z-C", "SF-21-Y-B",
        "SF-21-V-D", "SF-21-V-B", "SF-21-X-A", "SE-21-Z-D"
    ],
    "PAMPA": [
        # Grid codes for Pampa biome
        "SH-21-Y-B", "SH-21-V-D", "SH-21-X-A", "SH-21-X-C",
        "SH-21-X-D", "SH-21-X-B", "SG-21-Z-D", "SG-22-Y-D",
        "SH-22-V-B", "SH-22-V-A", "SG-22-Y-C", "SH-22-V-C",
        "SH-21-Z-B", "SH-22-Y-A", "SH-21-Z-D", "SH-22-Y-C",
        "SI-22-V-A", "SI-22-V-C", "SH-22-Y-D", "SH-22-Y-B",
        "SI-22-V-B", "SH-22-Z-C", "SH-22-Z-A", "SH-22-X-C",
        "SH-22-V-D", "SH-21-Z-C", "SH-21-Z-A"
    ]
}

# Dictionary mapping Landsat satellite identifiers to their Google Earth Engine collection IDs
# These are Landsat Collection 2, Tier 1, Level 2 Surface Reflectance products
collectionIds = {
    'l4': 'LANDSAT/LT04/C02/T1_L2',  # Landsat 4 TM
    'l5': 'LANDSAT/LT05/C02/T1_L2',  # Landsat 5 TM
    'l7': 'LANDSAT/LE07/C02/T1_L2',  # Landsat 7 ETM+
    'l8': 'LANDSAT/LC08/C02/T1_L2',  # Landsat 8 OLI/TIRS
    'l9': 'LANDSAT/LC09/C02/T1_L2',  # Landsat 9 OLI-2/TIRS-2
}

# Dictionary mapping satellite identifiers to their standardized names
landsatIds = {
    'l4': 'landsat-4',
    'l5': 'landsat-5',
    'l7': 'landsat-7',
    'l8': 'landsat-8',
    'l9': 'landsat-9',
}

# Dictionary specifying output collection paths for each satellite
# All satellites write to the same base collection path
outputCollections = {
    'l4': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',
    'l5': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',
    'l7': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',
    'l8': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',
    'l9': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2'
}

# Buffer size in meters to expand grid boundaries
# This ensures overlap between adjacent tiles to avoid edge effects
bufferSize = 100

# List of year-satellite combinations to process
# Each entry is [year, satellite_code]
# Currently only processing 2025 with Landsat 8 and 9
yearsSat = [
    [2025, 'l8'],
    [2025, 'l9'],
    # [2024, 'l8'],
    # [2024, 'l9'],
    # [2023, 'l8'],
    # [2023, 'l9'],
    # [2022, 'l8'],
    # [2022, 'l9'],
    # [2021, 'l8'],
    # [2020, 'l8'],
    # [2019, 'l8'],
    # [2018, 'l8'],
    # [2017, 'l8'],
    # [2016, 'l8'],
    # [2015, 'l8'],
    # [2014, 'l8'],
    # [2013, 'l8'],
    # [2011, 'l5'],
    # [2010, 'l5'],
    # [2009, 'l5'],
    # [2008, 'l5'],
    # [2007, 'l5'],
    # [2006, 'l5'],
    # [2005, 'l5'],
    # [2004, 'l5'],
    # [2003, 'l5'],
    # [2002, 'l5'],
    # [2001, 'l5'],
    # [2000, 'l5'],
    # [1999, 'l5'],
    # [1998, 'l5'],
    # [1997, 'l5'],
    # [1996, 'l5'],
    # [1995, 'l5'],
    # [1994, 'l5'],
    # [1993, 'l5'],
    # [1992, 'l5'],
    # [1991, 'l5'],
    # [1990, 'l5'],
    # [1989, 'l5'],
    # [1988, 'l5'],
    # [1987, 'l5'],
    # [1986, 'l5'],
    # [1985, 'l5'],
    # [2012, 'l7'],
    # [2021, 'l7'],
    # [2020, 'l7'],
    # [2019, 'l7'],
    # [2018, 'l7'],
    # [2017, 'l7'],
    # [2016, 'l7'],
    # [2015, 'l7'],
    # [2014, 'l7'],
    # [2013, 'l7'],
    # [2012, 'l7'],
    # [2011, 'l7'],
    # [2010, 'l7'],
    # [2009, 'l7'],
    # [2008, 'l7'],
    # [2007, 'l7'],
    # [2006, 'l7'],
    # [2005, 'l7'],
    # [2004, 'l7'],
    # [2003, 'l7'],
    # [2002, 'l7'],
    # [2001, 'l7'],
    # [2000, 'l7'],
    # [1982, 'l4'],
    # [1983, 'l4'],
    # [1984, 'l4'],
]


def multiplyBy10000(image):
    """
    Multiply spectral bands and indices by 10000
    This scales float values to integers for efficient storage
    
    Args:
        image: Earth Engine image
    
    Returns:
        Image with scaled bands
    """

    bands = [
        'blue',
        'red',
        'green',
        'nir',
        'swir1',
        'swir2',
        'cai',
        'evi2',
        'gcvi',
        'hallcover',
        'hallheigth',
        'ndvi',
        'ndwi',
        'pri',
        'savi',
    ]

    return image.addBands(
        srcImg=image.select(bands).multiply(10000),
        names=bands,
        overwrite=True
    )


def divideBy10000(image):
    """
    Divide spectral bands by 10000
    This converts stored integer values back to reflectance (0-1 scale)
    
    Args:
        image: Earth Engine image
    
    Returns:
        Image with scaled bands
    """

    bands = [
        'blue',
        'red',
        'green',
        'nir',
        'swir1',
        'swir2'
    ]

    return image.addBands(
        srcImg=image.select(bands).divide(10000),
        names=bands,
        overwrite=True
    )


def applyCloudAndShadowMask(collection):
    """
    Apply comprehensive cloud and shadow masking to an image collection
    Uses multiple methods: cloud flags, cloud scores, and shadow detection
    
    Args:
        collection: Earth Engine ImageCollection
    
    Returns:
        ImageCollection with clouds and shadows masked out
    """

    # Get cloud and shadow masks using various detection methods
    collectionWithMasks = getMasks(collection,
                                   cloudThresh=10,           # Cloud probability threshold
                                   cloudFlag=True,           # Use QA_PIXEL cloud flag
                                   cloudScore=True,          # Use cloud score algorithm
                                   cloudShadowFlag=True,     # Use QA_PIXEL shadow flag
                                   cloudShadowTdom=True,     # Use TDOM shadow detection
                                   zScoreThresh=-1,          # Z-score threshold for TDOM
                                   shadowSumThresh=4000,     # Shadow sum threshold
                                   dilatePixels=4,           # Dilation to expand cloud/shadow areas
                                   cloudHeights=[            # Cloud heights for shadow projection (meters)
                                       200, 700, 1200, 1700, 2200, 2700,
                                       3200, 3700, 4200, 4700
                                   ],
                                   cloudBand='cloudScoreMask')

    # Apply the masks: keep only pixels where ALL masks indicate clear conditions
    collectionWithoutClouds = collectionWithMasks \
        .map(
            lambda image: image.mask(
                image.select([
                    'cloudFlagMask',        # QA_PIXEL cloud mask
                    'cloudScoreMask',       # Algorithm-based cloud mask
                    'cloudShadowFlagMask'   # QA_PIXEL shadow mask
                    # 'cloudShadowTdomMask' # TDOM shadow mask (commented out)
                ]).reduce(ee.Reducer.anyNonZero()).eq(0)  # Mask where any mask == 0 (clear)
            )
        )

    return collectionWithoutClouds


def getTiles(collection):
    """
    Extract unique Landsat WRS path/row combinations from a collection
    WRS (Worldwide Reference System) defines Landsat scene locations
    
    Args:
        collection: Earth Engine ImageCollection
    
    Returns:
        List of dictionaries with tile information (path, row, id)
    """

    # Add a tile property to each image containing path, row, and unique ID
    collection = collection.map(
        lambda image: image.set(
            'tile', {
                'path': image.get('WRS_PATH'),   # WRS path number
                'row': image.get('WRS_ROW'),     # WRS row number
                'id': ee.Number(image.get('WRS_PATH'))
                        .multiply(1000).add(image.get('WRS_ROW')).int32()  # Unique tile ID
            }
        )
    )

    # Get list of unique tiles in the collection
    tiles = collection.distinct(['tile']).reduceColumns(
        ee.Reducer.toList(), ['tile']).get('list')

    return tiles.getInfo()


def getExcludedImages(biome, year):
    """
    Retrieve blacklisted image IDs for a specific biome and year
    These are problematic images that should be excluded from processing
    
    Args:
        biome: Name of the biome
        year: Year to check
    
    Returns:
        List of image IDs to exclude
    """

    # Asset containing blacklist information from Collection 5
    assetId = 'projects/mapbiomas-workspace/MOSAICOS/workspace-c5'

    # Filter collection by biome and year
    collection = ee.ImageCollection(assetId) \
        .filterMetadata('region', 'equals', biome) \
        .filterMetadata('year', 'equals', str(year))

    # Extract and flatten the blacklist
    excluded = ee.List(collection.reduceColumns(ee.Reducer.toList(), ['black_list']).get('list')) \
        .map(
            lambda names: ee.String(names).split(',')  # Split comma-separated lists
    )

    return excluded.flatten().getInfo()


# Get collection of all available tile masks
collectionTiles = ee.ImageCollection(assetMasks)

# Extract list of all tile IDs that have masks available
allTiles = collectionTiles.reduceColumns(
    ee.Reducer.toList(), ['tile']).get('list').getInfo()

# Main processing loop: iterate through biomes
for biomeName in biomeNames:

    # Get the feature collection of grids for this biome
    grids = ee.FeatureCollection(gridsAsset)\
        .filter(
        ee.Filter.inList('grid_name', gridNames[biomeName])
    )

    # Iterate through year-satellite combinations
    for year, satellite in yearsSat:

        # Construct date range strings for this biome and year
        dateStart = '{}-{}'.format(year, dataFilter[biomeName]['dateStart'])
        dateEnd = '{}-{}'.format(year, dataFilter[biomeName]['dateEnd'])
        cloudCover = dataFilter[biomeName]['cloudCover']

        # Iterate through each grid tile for this biome
        for gridName in gridNames[biomeName]:

            try:
                # Check if this mosaic already exists in the output collection
                # if True:
                alreadyInCollection = ee.ImageCollection(outputCollections[satellite]) \
                    .filterMetadata('year', 'equals', year) \
                    .filterMetadata('biome', 'equals', biomeName) \
                    .reduceColumns(ee.Reducer.toList(), ['system:index']) \
                    .get('list') \
                    .getInfo()

                # Construct output mosaic name following naming convention
                # Format: BIOME-GRID-YEAR-SATELLITE-VERSION
                outputName = biomeName + '-' + \
                    gridName + '-' + \
                    str(year) + '-' + \
                    satellite.upper() + '-' + \
                    str(version[biomeName])

                # Only process if mosaic doesn't already exist
                if outputName not in alreadyInCollection:

                    # Get the geometry for this specific grid
                    grid = grids.filterMetadata(
                        'grid_name', 'equals', gridName)

                    # Extract geometry and buffer it to ensure tile overlap
                    grid = ee.Feature(grid.first()).geometry()\
                        .buffer(bufferSize).bounds()

                    # Initialize excluded images list (currently empty)
                    excluded = []
                    # Optional: Get excluded images for specific biomes
                    # if biomeName in ['PANTANAL', 'MATAATLANTICA']:
                    #     excluded = getExcludedImages(biomeName, year)

                    # Get Landsat image collection for this grid and year
                    # Note: Uses full year date range, not biome-specific range
                    collection = getCollection(collectionIds[satellite],
                                               dateStart='{}-{}'.format(
                                                   year, '01-01'),
                                               dateEnd='{}-{}'.format(
                                                   year, '12-31'),
                                               cloudCover=cloudCover,
                                               geometry=grid,
                                               trashList=excluded
                                               )

                    # Detect which WRS path/row tiles intersect this grid
                    tiles = getTiles(collection)
                    # Filter to only tiles that have available masks
                    tiles = list(
                        filter(
                            lambda tile: tile['id'] in allTiles,
                            tiles
                        )
                    )

                    subcollectionList = []

                    # Process each tile separately if tiles exist
                    if len(tiles) > 0:
                        # Apply tile-specific mask for each path/row
                        for tile in tiles:
                            print(tile['path'], tile['row'])

                            # Filter collection to this specific tile
                            subcollection = collection \
                                .filterMetadata('WRS_PATH', 'equals', tile['path']) \
                                .filterMetadata('WRS_ROW', 'equals', tile['row'])

                            # Load the pre-computed mask for this tile
                            tileMask = ee.Image(
                                '{}/{}-{}'.format(assetMasks, tile['id'], versionMasks))

                            # Apply the tile mask to all images in this subcollection
                            subcollection = subcollection.map(
                                lambda image: image.mask(tileMask).selfMask()
                            )

                            subcollectionList.append(subcollection)

                        # Merge all tile-specific subcollections into one collection
                        collection = ee.List(subcollectionList) \
                            .iterate(
                                lambda subcollection, collection:
                                    ee.ImageCollection(
                                        collection).merge(subcollection),
                                ee.ImageCollection([])
                        )

                        # Convert from iterated result back to ImageCollection
                        collection = ee.ImageCollection(collection)

                        # Get standardized band names for this satellite
                        bands = getBandNames(satellite + 'c2')

                        # Rename bands to standardized names (blue, green, red, nir, etc.)
                        collection = collection.select(
                            bands['bandNames'],
                            bands['newNames']
                        )

                        # Apply cloud and shadow masking
                        collection = applyCloudAndShadowMask(collection)

                        # Get spectral endmembers for SMA (Spectral Mixture Analysis)
                        endmember = ENDMEMBERS[landsatIds[satellite]]

                        # Calculate SMA fractions (vegetation, soil, shade, etc.)
                        collection = collection.map(
                            lambda image: image.addBands(
                                getFractions(image, endmember))
                        )

                        # Calculate SMA-based indices
                        collection = collection\
                            .map(getNDFI)\
                            .map(getSEFI)\
                            .map(getWEFI)\
                            .map(getFNS)

                        # Calculate spectral vegetation indices
                        collection = collection\
                            .map(divideBy10000)\
                            .map(getCAI)\
                            .map(getEVI2)\
                            .map(getGCVI)\
                            .map(getHallCover)\
                            .map(getHallHeigth)\
                            .map(getNDVI)\
                            .map(getNDWI)\
                            .map(getPRI)\
                            .map(getSAVI)\
                            .map(multiplyBy10000)

                        # Generate mosaic from the processed collection
                        # Use different percentile bands for different biomes
                        if biomeName in ['PANTANAL']:
                            percentileBand = 'ndwi'  # Water index for wetland biome
                        else:
                            percentileBand = 'ndvi'  # Vegetation index for other biomes

                        # Create composite using percentile-based pixel selection
                        mosaic = getMosaic(collection,
                                           percentileDry=25,              # 25th percentile (dry season)
                                           percentileWet=75,              # 75th percentile (wet season)
                                           percentileBand=percentileBand,  # Band for percentile calculation
                                           dateStart=dateStart,            # Biome-specific date range
                                           dateEnd=dateEnd)

                        # Add texture and terrain bands
                        mosaic = getEntropyG(mosaic)  # Entropy (texture measure)
                        mosaic = getSlope(mosaic)      # Terrain slope
                        mosaic = setBandTypes(mosaic)  # Set appropriate data types

                        # Add metadata properties to the mosaic
                        mosaic = mosaic.set('year', year)
                        mosaic = mosaic.set('collection', 8.0)
                        mosaic = mosaic.set('grid_name', gridName)
                        mosaic = mosaic.set('version', str(version[biomeName]))
                        mosaic = mosaic.set('biome', biomeName)
                        mosaic = mosaic.set('satellite', satellite)

                        print(outputName)

                        # Export mosaic to Earth Engine asset
                        task = ee.batch.Export.image.toAsset(
                            image=mosaic,
                            description=outputName,
                            assetId=outputCollections[satellite] +
                            '/' + outputName,
                            region=grid.coordinates().getInfo(),
                            scale=30,                    # 30m spatial resolution (Landsat native)
                            maxPixels=int(1e13)          # Maximum pixels to export
                        )

                        # Start the export task
                        task.start()

            except Exception as e:
                # Handle errors, particularly task queue limits
                msg = 'Too many tasks already in the queue (3000). Please wait for some of them to complete.'
                print(e)
                # Re-raise exception if it's the queue limit error
                if e == msg:
                    raise Exception(e)
