"""
Google Earth Engine Landsat Mosaic Generator for Argentina
===========================================================

This script generates annual Landsat mosaics for Argentina using Google Earth Engine.
It processes Landsat Collection 2 imagery (Landsat 4-9) with cloud/shadow masking,
spectral indices calculation, and SMA (Spectral Mixture Analysis) to create
analysis-ready composite images organized by grid tiles.

Version: 1
Dependencies: earthengine-api, custom MapBiomas modules
"""

import ee
import sys
import os

# Add custom module paths to Python path
sys.path.append(os.path.abspath('..\\'))
sys.path.append(os.path.abspath('..\\mapbiomas-mosaics'))

print(sys.path)

# Import custom MapBiomas modules for processing
from modules.CloudAndShadowMaskC2 import *
from modules.SpectralIndexes import *
from modules.Miscellaneous import *
from modules.SmaAndNdfi import *
from modules.Collection import *
from modules.BandNames import * 
from modules.DataType import *
from modules.Mosaic import *

# Prevent Python from writing .pyc files
sys.dont_write_bytecode = True


ee.Initialize()


versionMasks = '2'

gridsAsset = 'projects/mapbiomas-workspace/AUXILIAR/cim-world-1-250000'

assetMasks = "projects/mapbiomas-workspace/AUXILIAR/landsat-mask"

# nome do bioma sem espaço
territoryNames = [
    'ARGENTINA',
    'CUYO',
    'PATAGONIA',
]

version = {
    'CUYO': '1',
    'PATAGONIA': '1',
    'ARGENTINA': '1',
}

dataFilter = {
    'CUYO': {
        'dateStart': '01-01',
        'dateEnd': '12-31',
        'cloudCover': 80
    },
    'PATAGONIA': {
        'dateStart': '01-01',
        'dateEnd': '12-31',
        'cloudCover': 80
    },
    'ARGENTINA': {
        'dateStart': '01-01',
        'dateEnd': '12-31',
        'cloudCover': 80
    }
}

gridNames = {
    "ARGENTINA": [
        "SG-22-Y-C",
        "SG-19-Z-D",
        "SH-19-X-B",
        "SH-19-X-C",
        "SH-19-X-D",
        "SH-19-Z-A",
        "SH-19-Z-B",
        "SH-19-Z-D",
        "SI-19-X-B",
        "SI-19-X-D",
        "SI-19-Z-B",
        "SI-19-Z-D",
        "SJ-19-X-B",
        "SJ-19-X-D",
        "SF-20-V-C",
        "SF-20-V-D",
        "SF-20-X-C",
        "SF-20-Y-A",
        "SF-20-Y-B",
        "SF-20-Y-C",
        "SF-20-Y-D",
        "SF-20-Z-A",
        "SF-20-Z-C",
        "SF-20-Z-D",
        "SG-20-V-A",
        "SG-20-V-B",
        "SG-20-V-C",
        "SG-20-V-D",
        "SG-20-X-A",
        "SG-20-X-B",
        "SG-20-X-C",
        "SG-20-X-D",
        "SG-20-Y-A",
        "SG-20-Y-B",
        "SG-20-Y-C",
        "SG-20-Y-D",
        "SG-20-Z-A",
        "SG-20-Z-B",
        "SG-20-Z-C",
        "SG-20-Z-D",
        "SH-20-V-A",
        "SH-20-V-B",
        "SH-20-V-C",
        "SH-20-V-D",
        "SH-20-X-A",
        "SH-20-X-B",
        "SH-20-X-C",
        "SH-20-X-D",
        "SH-20-Y-A",
        "SH-20-Y-B",
        "SH-20-Y-C",
        "SH-20-Y-D",
        "SH-20-Z-A",
        "SH-20-Z-B",
        "SH-20-Z-C",
        "SH-20-Z-D",
        "SI-20-V-A",
        "SI-20-V-B",
        "SI-20-V-C",
        "SI-20-V-D",
        "SI-20-X-A",
        "SI-20-X-B",
        "SI-20-X-C",
        "SI-20-X-D",
        "SI-20-Y-A",
        "SI-20-Y-B",
        "SI-20-Y-C",
        "SI-20-Y-D",
        "SI-20-Z-A",
        "SI-20-Z-B",
        "SI-20-Z-C",
        "SI-20-Z-D",
        "SJ-20-V-A",
        "SJ-20-V-B",
        "SJ-20-V-C",
        "SJ-20-V-D",
        "SJ-20-X-A",
        "SJ-20-X-B",
        "SJ-20-X-C",
        "SJ-20-X-D",
        "SJ-20-Y-B",
        "SJ-20-Z-A",
        "SJ-20-Z-B",
        "SG-21-V-A",
        "SG-21-V-B",
        "SG-21-V-C",
        "SG-21-V-D",
        "SG-21-X-D",
        "SG-21-Y-A",
        "SG-21-Y-B",
        "SG-21-Y-C",
        "SG-21-Y-D",
        "SG-21-Z-B",
        "SG-21-Z-C",
        "SG-21-Z-D",
        "SH-21-V-A",
        "SH-21-V-B",
        "SH-21-V-C",
        "SH-21-V-D",
        "SH-21-X-A",
        "SH-21-X-B",
        "SH-21-X-C",
        "SH-21-Y-A",
        "SH-21-Y-B",
        "SH-21-Y-C",
        "SH-21-Y-D",
        "SI-21-V-A",
        "SI-21-V-B",
        "SI-21-V-C",
        "SI-21-V-D",
        "SI-21-Y-A",
        "SI-21-Y-B",
        "SI-21-Y-C",
        "SI-21-Y-D",
        "SJ-21-V-A",
        "SJ-21-V-B",
        "SJ-21-V-C",
        "SJ-21-V-D",
        "SJ-21-Y-A",
        "SJ-21-Y-B",
        "SG-22-V-C",
        "SG-22-Y-A"
        ],
    "CUYO": [
        "SF-19-X-D",
        "SF-19-Z-B",
        "SF-19-Z-D",
        "SG-19-X-A",
        "SG-19-X-B",
        "SG-19-X-C",
        "SG-19-X-D",
        "SG-19-Y-D",
        "SG-19-Z-A",
        "SG-19-Z-B",
        "SG-19-Z-C",
        "SG-19-Z-D",
        "SH-19-V-B",
        "SH-19-V-D",
        "SH-19-X-A",
        "SH-19-X-B",
        "SH-19-X-C",
        "SH-19-X-D",
        "SH-19-Y-B",
        "SH-19-Y-C",
        "SH-19-Y-D",
        "SH-19-Z-A",
        "SH-19-Z-C",
        "SH-19-Z-D",
        "SI-19-V-B",
        "SI-19-V-D",
        "SI-19-X-A",
        "SI-19-X-B",
        "SI-19-X-C",
        "SI-19-X-D",
        "SI-19-Y-B",
        "SI-19-Y-C",
        "SI-19-Y-D",
        "SI-19-Z-A",
        "SI-19-Z-B",
        "SI-19-Z-C",
        "SI-19-Z-D",
        "SJ-19-V-B",
        "SJ-19-V-D",
        "SJ-19-X-A",
        "SJ-19-X-B",
        "SJ-19-X-C",
        "SJ-19-X-D",
        "SJ-19-Z-A",
        "SJ-19-Z-B",
        "SF-20-V-C",
        "SF-20-Y-A",
        "SF-20-Y-C",
        "SG-20-V-A",
        "SG-20-V-C",
        "SG-20-Y-A",
        "SG-20-Y-C",
        "SJ-20-V-C",
        "SJ-20-Y-A",
        "SJ-20-Y-B"
    ],
    "PATAGONIA": [
        "SN-21-V-B",
        "SK-18-Z-B",
        "SK-18-Z-D",
        "SL-18-X-B",
        "SL-18-Z-D",
        "SM-18-X-B",
        "SM-18-X-C",
        "SM-18-X-D",
        "SM-18-Z-A",
        "SM-18-Z-B",
        "SM-18-Z-D",
        "SJ-19-V-A",
        "SJ-19-V-B",
        "SJ-19-V-C",
        "SJ-19-V-D",
        "SJ-19-X-C",
        "SJ-19-Y-A",
        "SJ-19-Y-B",
        "SJ-19-Y-C",
        "SJ-19-Y-D",
        "SJ-19-Z-A",
        "SJ-19-Z-B",
        "SJ-19-Z-C",
        "SJ-19-Z-D",
        "SK-19-V-A",
        "SK-19-V-B",
        "SK-19-V-C",
        "SK-19-V-D",
        "SK-19-X-A",
        "SK-19-X-B",
        "SK-19-X-C",
        "SK-19-X-D",
        "SK-19-Y-A",
        "SK-19-Y-B",
        "SK-19-Y-C",
        "SK-19-Y-D",
        "SK-19-Z-A",
        "SK-19-Z-B",
        "SK-19-Z-C",
        "SK-19-Z-D",
        "SL-19-V-A",
        "SL-19-V-B",
        "SL-19-V-C",
        "SL-19-V-D",
        "SL-19-X-A",
        "SL-19-X-B",
        "SL-19-X-C",
        "SL-19-X-D",
        "SL-19-Y-A",
        "SL-19-Y-B",
        "SL-19-Y-C",
        "SL-19-Y-D",
        "SL-19-Z-A",
        "SL-19-Z-B",
        "SL-19-Z-C",
        "SL-19-Z-D",
        "SM-19-V-A",
        "SM-19-V-B",
        "SM-19-V-C",
        "SM-19-V-D",
        "SM-19-X-A",
        "SM-19-X-B",
        "SM-19-X-C",
        "SM-19-Y-A",
        "SM-19-Y-B",
        "SM-19-Y-C",
        "SM-19-Y-D",
        "SM-19-Z-A",
        "SM-19-Z-C",
        "SN-19-V-B",
        "SN-19-X-A",
        "SN-19-X-C",
        "SN-19-X-D",
        "SN-19-Z-A",
        "SN-19-Z-B",
        "SN-19-Z-D",
        "SJ-20-Y-A",
        "SJ-20-Y-B",
        "SJ-20-Y-C",
        "SJ-20-Y-D",
        "SJ-20-Z-A",
        "SJ-20-Z-C",
        "SK-20-V-A",
        "SK-20-V-B",
        "SK-20-V-C",
        "SK-20-V-D",
        "SK-20-X-A",
        "SK-20-X-C",
        "SK-20-Y-A",
        "SK-20-Y-B",
        "SK-20-Y-C",
        "SK-20-Y-D",
        "SL-20-V-A",
        "SL-20-V-C",
        "SL-20-Y-C",
        "SM-20-V-A",
        "SM-20-Z-D",
        "SN-20-X-B",
        "SN-20-Y-A",
        "SN-20-Y-B",
        "SM-21-Y-C",
        "SM-21-Y-D",
        "SN-21-V-A"
    ],
}

collectionIds = {
    'l4': 'LANDSAT/LT04/C02/T1_L2',
    'l5': 'LANDSAT/LT05/C02/T1_L2',
    'l7': 'LANDSAT/LE07/C02/T1_L2',
    'l8': 'LANDSAT/LC08/C02/T1_L2',
    'l9': 'LANDSAT/LC09/C02/T1_L2',
}

landsatIds = {
    'l4': 'landsat-4',
    'l5': 'landsat-5',
    'l7': 'landsat-7',
    'l8': 'landsat-8',
    'l9': 'landsat-9',
}

outputCollections = {
    'l4': 'projects/nexgenmap/MapBiomas2/LANDSAT/ARGENTINA/mosaics-1',
    'l5': 'projects/nexgenmap/MapBiomas2/LANDSAT/ARGENTINA/mosaics-1',
    'l7': 'projects/nexgenmap/MapBiomas2/LANDSAT/ARGENTINA/mosaics-1',
    'l8': 'projects/nexgenmap/MapBiomas2/LANDSAT/ARGENTINA/mosaics-1',
    'l9': 'projects/nexgenmap/MapBiomas2/LANDSAT/ARGENTINA/mosaics-1'
}

bufferSize = 100

yearsSat = [
    [2025, 'l9'],
    [2025, 'l8'],
    # [2024, 'l9'],
    # [2024, 'l8'],
    # [2023, 'l9'],
    # [2023, 'l8'],
    # [2022, 'l8'],
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
    # [2003, 'l7'],
    # [2002, 'l7'], 
    # [2001, 'l7'], 
    # [2000, 'l7'],
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
]


def multiplyBy10000(image):

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

    # Get cloud and shadow masks
    collectionWithMasks = getMasks(collection,
                                   cloudThresh=10,
                                   cloudFlag=True,
                                   cloudScore=True,
                                   cloudShadowFlag=True,
                                   cloudShadowTdom=True,
                                   zScoreThresh=-1,
                                   shadowSumThresh=4000,
                                   dilatePixels=4,
                                   cloudHeights=[
                                       200, 700, 1200, 1700, 2200, 2700,
                                       3200, 3700, 4200, 4700
                                   ],
                                   cloudBand='cloudShadowFlagMask')

    # get collection without clouds
    collectionWithoutClouds = collectionWithMasks \
        .map(
            lambda image: image.mask(
                image.select([
                    'cloudFlagMask',
                    'cloudShadowFlagMask'  # ,
                    # 'cloudScoreMask',
                    # 'cloudShadowTdomMask'
                ]).reduce(ee.Reducer.anyNonZero()).eq(0)
            )
        )

    return collectionWithoutClouds


def getTiles(collection):

    collection = collection.map(
        lambda image: image.set(
            'tile', {
                'path': image.get('WRS_PATH'),
                'row': image.get('WRS_ROW'),
                'id': ee.Number(image.get('WRS_PATH'))
                        .multiply(1000).add(image.get('WRS_ROW')).int32()
            }
        )
    )

    tiles = collection.distinct(['tile']).reduceColumns(
        ee.Reducer.toList(), ['tile']).get('list')

    return tiles.getInfo()


def getExcludedImages(biome, year):

    assetId = 'projects/mapbiomas-workspace/MOSAICOS/workspace-c5'

    collection = ee.ImageCollection(assetId) \
        .filterMetadata('region', 'equals', biome) \
        .filterMetadata('year', 'equals', str(year))

    excluded = ee.List(collection.reduceColumns(ee.Reducer.toList(), ['black_list']).get('list')) \
        .map(
            lambda names: ee.String(names).split(',')
    )

    return excluded.flatten().getInfo()


# get all tile names
collectionTiles = ee.ImageCollection(assetMasks)

allTiles = collectionTiles.reduceColumns(
    ee.Reducer.toList(), ['tile']).get('list').getInfo()

for territoryName in territoryNames:

    grids = ee.FeatureCollection(gridsAsset)\
        .filter(
        ee.Filter.inList('name', gridNames[territoryName])
    )

    for year, satellite in yearsSat:
        print(year, satellite)

        dateStart = '{}-{}'.format(year, dataFilter[territoryName]['dateStart'])
        dateEnd = '{}-{}'.format(year, dataFilter[territoryName]['dateEnd'])
        cloudCover = dataFilter[territoryName]['cloudCover']

        for gridName in gridNames[territoryName]:
            
            try:
            # if True:
                alreadyInCollection = ee.ImageCollection(outputCollections[satellite]) \
                    .filterMetadata('year', 'equals', year) \
                    .filterMetadata('territory', 'equals', territoryName) \
                    .reduceColumns(ee.Reducer.toList(), ['system:index']) \
                    .get('list') \
                    .getInfo()
                
                outputName = territoryName + '-' + \
                    gridName + '-' + \
                    str(year) + '-' + \
                    satellite.upper() + '-' + \
                    str(version[territoryName])
                
                if outputName not in alreadyInCollection:
                    
                    # define a geometry
                    grid = grids.filter(ee.Filter.eq(
                        'name', gridName))

                    grid = ee.Feature(grid.first()).geometry()\
                        .buffer(bufferSize).bounds()

                    excluded = []

                    # returns a collection containing the specified parameters
                    collection = getCollection(collectionIds[satellite],
                                               dateStart='{}-{}'.format(year, '01-01'),
                                               dateEnd='{}-{}'.format(year, '12-31'),
                                               cloudCover=cloudCover,
                                               geometry=grid,
                                               trashList=excluded
                                               )
                    
                    # detect the image tiles
                    tiles = getTiles(collection)
                    tiles = list(
                        filter(
                            lambda tile: tile['id'] in allTiles,
                            tiles
                        )
                    )

                    subcollectionList = []
                    
                    if len(tiles) > 0:
                        # apply tile mask for each image
                        for tile in tiles:
                            print(tile['path'], tile['row'])

                            subcollection = collection \
                                .filterMetadata('WRS_PATH', 'equals', tile['path']) \
                                .filterMetadata('WRS_ROW', 'equals', tile['row'])

                            tileMask = ee.Image(
                                '{}/{}-{}'.format(assetMasks, tile['id'], versionMasks))

                            subcollection = subcollection.map(
                                lambda image: image.mask(tileMask).selfMask()
                            )

                            subcollectionList.append(subcollection)

                        # merge collections
                        collection = ee.List(subcollectionList) \
                            .iterate(
                                lambda subcollection, collection:
                                    ee.ImageCollection(
                                        collection).merge(subcollection),
                                ee.ImageCollection([])
                        )

                        # flattens collections of collections
                        collection = ee.ImageCollection(collection)

                        # returns a pattern of landsat collection 2 band names
                        bands = getBandNames(satellite + 'c2')

                        # Rename collection image bands
                        collection = collection.select(
                            bands['bandNames'],
                            bands['newNames']
                        )

                        collection = applyCloudAndShadowMask(collection)

                        endmember = ENDMEMBERS[landsatIds[satellite]]

                        collection = collection.map(
                            lambda image: image.addBands(
                                getFractions(image, endmember))
                        )

                        # calculate SMA indexes
                        collection = collection\
                            .map(getNDFI)\
                            .map(getSEFI)\
                            .map(getWEFI)\
                            .map(getFNS)

                        # calculate Spectral indexes
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

                        # generate mosaic
                        if territoryName in ['PANTANAL']:
                            percentileBand = 'ndwi'
                        else:
                            percentileBand = 'ndvi'

                        mosaic = getMosaic(collection,
                                           percentileDry=25,
                                           percentileWet=75,
                                           percentileBand=percentileBand,
                                           dateStart=dateStart,
                                           dateEnd=dateEnd)

                        mosaic = getEntropyG(mosaic)
                        mosaic = getSlope(mosaic)
                        mosaic = setBandTypes(mosaic)

                        mosaic = mosaic.set('year', year)
                        mosaic = mosaic.set('collection', 1.0)
                        mosaic = mosaic.set('grid_name', gridName)
                        mosaic = mosaic.set('version', str(version[territoryName]))
                        mosaic = mosaic.set('territory', territoryName)
                        mosaic = mosaic.set('satellite', satellite)

                        print(outputName)

                        task = ee.batch.Export.image.toAsset(
                            image=mosaic,
                            description=outputName,
                            assetId=outputCollections[satellite] +
                            '/' + outputName,
                            region=grid.coordinates().getInfo(),
                            scale=30,
                            maxPixels=int(1e13)
                        )

                        task.start()

            except Exception as e:
                msg = 'Too many tasks already in the queue (3000). Please wait for some of them to complete.'
                if e == msg:
                    raise Exception(e)
                else:
                    print(e)
