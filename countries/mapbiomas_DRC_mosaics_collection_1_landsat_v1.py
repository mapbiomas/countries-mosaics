"""
Google Earth Engine Landsat Mosaic Generator for DRC
===========================================================

This script generates annual Landsat mosaics for DRC using Google Earth Engine.
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

# Initialize Google Earth Engine with MapBiomas DRC project
ee.Initialize(project = "mapbiomas-drc")


versionMasks = '2'

gridsAsset = 'projects/mapbiomas-workspace/AUXILIAR/cim-world-1-250000'

assetMasks = "projects/mapbiomas-workspace/AUXILIAR/landsat-mask"

# nome do bioma sem espaço
territoryNames = [
    'DRC',
]

version = {
    'DRC': '1',
}

dataFilter = {
    'DRC': {
        'dateStart': '01-01',
        'dateEnd': '12-31',
        'cloudCover': 80
    },
}

gridNames = {
    "DRC": [
        "NA-33-X-B",
        "NA-33-X-D",
        "NA-33-Z-B",
        "NA-33-Z-D",
        "NA-34-V-A",
        "NA-34-V-B",
        "NA-34-V-C",
        "NA-34-V-D",
        "NA-34-X-A",
        "NA-34-X-B",
        "NA-34-X-C",
        "NA-34-X-D",
        "NA-34-Y-A",
        "NA-34-Y-B",
        "NA-34-Y-C",
        "NA-34-Y-D",
        "NA-34-Z-A",
        "NA-34-Z-B",
        "NA-34-Z-C",
        "NA-34-Z-D",
        "NB-34-Y-A",
        "NB-34-Y-B",
        "NB-34-Y-C",
        "NB-34-Y-D",
        "NB-34-Z-A",
        "NB-34-Z-B",
        "NB-34-Z-C",
        "NB-34-Z-D",
        "NA-35-V-A",
        "NA-35-V-B",
        "NA-35-V-C",
        "NA-35-V-D",
        "NA-35-X-A",
        "NA-35-X-B",
        "NA-35-X-C",
        "NA-35-X-D",
        "NA-35-Y-A",
        "NA-35-Y-B",
        "NA-35-Y-C",
        "NA-35-Y-D",
        "NA-35-Z-A",
        "NA-35-Z-B",
        "NA-35-Z-C",
        "NA-35-Z-D",
        "NB-35-Y-A",
        "NB-35-Y-B",
        "NB-35-Y-C",
        "NB-35-Y-D",
        "NB-35-Z-A",
        "NB-35-Z-B",
        "NB-35-Z-C",
        "NB-35-Z-D",
        "NA-36-V-A",
        "NA-36-V-B",
        "NA-36-V-C",
        "NA-36-V-D",
        "NA-36-Y-A",
        "NA-36-Y-B",
        "NA-36-Y-C",
        "NB-36-Y-A",
        "NB-36-Y-C",
        "SB-32-X-B",
        "SB-32-X-D",
        "SB-32-Z-B",
        "SA-33-X-A",
        "SA-33-X-B",
        "SA-33-X-C",
        "SA-33-X-D",
        "SA-33-Y-D",
        "SA-33-Z-A",
        "SA-33-Z-B",
        "SA-33-Z-C",
        "SA-33-Z-D",
        "SB-33-V-A",
        "SB-33-V-B",
        "SB-33-V-C",
        "SB-33-V-D",
        "SB-33-X-A",
        "SB-33-X-B",
        "SB-33-X-C",
        "SB-33-X-D",
        "SB-33-Y-A",
        "SB-33-Y-B",
        "SB-33-Z-A",
        "SB-33-Z-B",
        "SB-33-Z-C",
        "SB-33-Z-D",
        "SC-33-X-B",
        "SA-34-V-A",
        "SA-34-V-B",
        "SA-34-V-C",
        "SA-34-V-D",
        "SA-34-X-A",
        "SA-34-X-B",
        "SA-34-X-C",
        "SA-34-X-D",
        "SA-34-Y-A",
        "SA-34-Y-B",
        "SA-34-Y-C",
        "SA-34-Y-D",
        "SA-34-Z-A",
        "SA-34-Z-B",
        "SA-34-Z-C",
        "SA-34-Z-D",
        "SB-34-V-A",
        "SB-34-V-B",
        "SB-34-V-C",
        "SB-34-V-D",
        "SB-34-X-A",
        "SB-34-X-B",
        "SB-34-X-C",
        "SB-34-X-D",
        "SB-34-Y-A",
        "SB-34-Y-B",
        "SB-34-Y-C",
        "SB-34-Y-D",
        "SB-34-Z-A",
        "SB-34-Z-B",
        "SB-34-Z-C",
        "SB-34-Z-D",
        "SC-34-V-A",
        "SC-34-V-B",
        "SC-34-X-A",
        "SC-34-X-B",
        "SC-34-X-C",
        "SC-34-X-D",
        "SC-34-Z-A",
        "SC-34-Z-B",
        "SC-34-Z-C",
        "SC-34-Z-D",
        "SD-34-X-A",
        "SD-34-X-B",
        "SA-35-V-A",
        "SA-35-V-B",
        "SA-35-V-C",
        "SA-35-V-D",
        "SA-35-X-A",
        "SA-35-X-B",
        "SA-35-X-C",
        "SA-35-X-D",
        "SA-35-Y-A",
        "SA-35-Y-B",
        "SA-35-Y-C",
        "SA-35-Y-D",
        "SA-35-Z-A",
        "SA-35-Z-B",
        "SA-35-Z-C",
        "SA-35-Z-D",
        "SB-35-V-A",
        "SB-35-V-B",
        "SB-35-V-C",
        "SB-35-V-D",
        "SB-35-X-A",
        "SB-35-X-B",
        "SB-35-X-C",
        "SB-35-X-D",
        "SB-35-Y-A",
        "SB-35-Y-B",
        "SB-35-Y-C",
        "SB-35-Y-D",
        "SB-35-Z-A",
        "SB-35-Z-B",
        "SB-35-Z-C",
        "SB-35-Z-D",
        "SC-35-V-A",
        "SC-35-V-B",
        "SC-35-V-C",
        "SC-35-V-D",
        "SC-35-X-A",
        "SC-35-X-B",
        "SC-35-X-C",
        "SC-35-X-D",
        "SC-35-Y-A",
        "SC-35-Y-B",
        "SC-35-Y-C",
        "SC-35-Y-D",
        "SC-35-Z-A",
        "SC-35-Z-B",
        "SC-35-Z-C",
        "SC-35-Z-D",
        "SD-35-V-A",
        "SD-35-V-B",
        "SD-35-V-D",
        "SD-35-X-A",
        "SD-35-X-B",
        "SD-35-X-C",
        "SD-35-X-D",
        "SD-35-Z-B",
        "SA-36-V-A",
        "SA-36-V-C",
        "SA-36-Y-A",
        "SA-36-Y-C",
        "SB-36-V-A",
        "SB-36-V-C",
        "SB-36-Y-A",
        "SB-36-Y-C",
        "SC-36-V-A",
        "SC-36-V-B",
        "SC-36-Y-C",
        "SD-36-V-A",
        "SD-36-V-C",
        "SD-36-Y-A"
        ]
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
# 
outputCollections = {
    'l4': 'projects/nexgenmap/MapBiomas2/LANDSAT/DRC/mosaics-1',
    'l5': 'projects/nexgenmap/MapBiomas2/LANDSAT/DRC/mosaics-1',
    'l7': 'projects/nexgenmap/MapBiomas2/LANDSAT/DRC/mosaics-1',
    'l8': 'projects/nexgenmap/MapBiomas2/LANDSAT/DRC/mosaics-1',
    'l9': 'projects/nexgenmap/MapBiomas2/LANDSAT/DRC/mosaics-1'
}

bufferSize = 100

yearsSat = [
    [2024, 'l9'],
    [2024, 'l8'],
    [2023, 'l9'],
    [2023, 'l8'],
    [2022, 'l8'],
    [2021, 'l8'], 
    [2020, 'l8'], 
    [2019, 'l8'],
    [2018, 'l8'], 
    [2017, 'l8'], 
    [2016, 'l8'],
    [2015, 'l8'], 
    [2014, 'l8'], 
    [2013, 'l8'],
    [2011, 'l5'], 
    [2010, 'l5'], 
    [2009, 'l5'],
    [2008, 'l5'], 
    [2007, 'l5'], 
    [2006, 'l5'],
    [2005, 'l5'], 
    [2004, 'l5'], 
    [2003, 'l5'],
    [2002, 'l5'], 
    [2001, 'l5'], 
    [2000, 'l5'],
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

    for gridName in gridNames[territoryName]:


        for year, satellite in yearsSat:
            print(year, satellite)
            dateStart = '{}-{}'.format(year, dataFilter[territoryName]['dateStart'])
            dateEnd = '{}-{}'.format(year, dataFilter[territoryName]['dateEnd'])
            cloudCover = dataFilter[territoryName]['cloudCover']
            
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
