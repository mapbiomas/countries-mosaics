"""
Google Earth Engine Landsat Mosaic Generator for Indonesia
===========================================================

This script generates annual Landsat mosaics for Indonesia using Google Earth Engine.
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

# Initialize Google Earth Engine with MapBiomas Indonesia project
ee.Initialize(project = "mapbiomas-indonesia")



versionMasks = '2'

gridsAsset = 'projects/mapbiomas-indonesia/ANCILLARY_DATA/grids'

assetMasks = "projects/mapbiomas-workspace/AUXILIAR/landsat-mask"'          '   

# nome do bioma sem espaço
territoryNames = [
    'INDONESIA'
]

version = {
    'INDONESIA': '2',
}

dataFilter = {
    'INDONESIA': {
        'dateStart': '01-01',
        'dateEnd': '12-31',
        'cloudCover': 80
    },
}

gridNames = {
    "INDONESIA": [
        "SB-50-Y-C",
        "SB-49-Z-D",
        "SB-49-Z-C",
        "SC-51-V-B",
        "SC-51-V-A",
        "SC-50-X-B",
        "SC-50-X-A",
        "SC-50-V-B",
        "SC-50-V-A",
        "SC-49-X-B",
        "SC-49-X-A",
        "SC-50-V-D",
        "SC-50-X-C",
        "SC-50-X-D",
        "SC-51-V-C",
        "SC-50-Z-B",
        "SC-51-Y-A",
        "SC-51-Y-B",
        "SB-49-X-D",
        "SB-50-Y-B",
        "SB-49-Z-B",
        "SB-50-Y-A",
        "SB-49-Z-A",
        "SA-53-X-A",
        "SA-53-Z-B",
        "SA-54-Y-A",
        "SA-54-Y-B",
        "SA-53-Z-A",
        "SA-54-Z-A",
        "SA-54-Y-C",
        "SA-54-Y-D",
        "SA-54-Z-C",
        "SB-54-V-B",
        "SB-54-V-A",
        "SB-54-X-A",
        "SB-54-V-C",
        "SB-54-V-D",
        "SB-54-X-C",
        "SB-54-Y-A",
        "SB-54-Y-B",
        "SB-54-Z-A",
        "SB-53-Z-D",
        "SB-54-Y-C",
        "SB-54-Y-D",
        "SB-54-Z-C",
        "SC-54-V-A",
        "SC-54-V-B",
        "SC-54-X-A",
        "SC-53-X-B",
        "SC-54-X-C",
        "SC-54-V-D",
        "SA-53-X-C",
        "SA-53-X-D",
        "SA-54-V-C",
        "SA-47-X-B",
        "SA-47-X-A",
        "SA-47-V-B",
        "NA-47-Y-A",
        "NA-47-Y-B",
        "NA-47-Z-A",
        "NA-47-Z-B",
        "NA-46-X-D",
        "NA-47-V-C",
        "NA-47-V-D",
        "NA-47-X-C",
        "NA-47-X-D",
        "NA-47-V-B",
        "NA-47-X-A",
        "NA-47-V-A",
        "NB-46-Z-D",
        "NB-47-Y-D",
        "NB-47-Y-C",
        "NB-46-Z-B",
        "NB-47-Y-B",
        "NB-47-Y-A",
        "NA-47-Z-D",
        "NA-47-Z-C",
        "NA-47-Y-D",
        "NA-47-Y-C",
        "SA-48-V-B",
        "SA-48-V-A",
        "NA-48-Y-B",
        "NA-48-Y-A",
        "NA-48-Y-D",
        "NA-48-Y-C",
        "SA-49-Y-A",
        "SA-48-Z-B",
        "SA-48-Z-A",
        "SA-48-Y-B",
        "SA-48-Y-A",
        "SA-49-Y-C",
        "SA-48-Z-D",
        "SA-48-Y-C",
        "SA-48-Y-D",
        "SA-48-Z-C",
        "SA-48-X-C",
        "SA-48-V-D",
        "SA-48-V-C",
        "SA-53-Z-D",
        "SA-53-Z-C",
        "SB-53-X-A",
        "SB-53-X-B",
        "SB-53-X-D",
        "SA-53-V-A",
        "SA-53-V-B",
        "SA-52-X-B",
        "SA-52-X-A",
        "SA-52-V-B",
        "SA-52-V-A",
        "NA-52-Y-A",
        "NA-52-Y-B",
        "SA-52-Z-B",
        "SA-52-Z-A",
        "SA-53-Y-A",
        "SA-53-Y-B",
        "SA-52-Y-B",
        "SA-52-Y-A",
        "SA-51-Z-B",
        "NA-52-V-D",
        "SA-52-Y-D",
        "SA-52-Z-C",
        "SA-53-Y-D",
        "SA-53-Y-C",
        "SA-52-Z-D",
        "SA-52-Y-C",
        "SB-52-X-A",
        "SB-53-V-A",
        "SB-53-V-B",
        "SB-52-X-B",
        "NA-52-Z-C",
        "NA-52-Y-D",
        "NA-52-Y-C",
        "SA-52-X-C",
        "SA-52-X-D",
        "SA-53-V-C",
        "SA-53-V-D",
        "SA-52-V-D",
        "SA-52-V-C",
        "SA-49-Z-B",
        "SA-50-Y-A",
        "SA-50-Y-B",
        "SA-49-Z-A",
        "SA-49-Z-D",
        "SA-50-Y-C",
        "SA-50-Y-D",
        "SA-49-Z-C",
        "SA-49-Y-D",
        "SB-50-V-B",
        "SB-50-V-A",
        "SA-50-V-D",
        "SA-50-V-C",
        "SA-49-X-D",
        "SA-49-X-C",
        "SB-50-X-B",
        "SB-51-V-A",
        "SB-51-V-B",
        "SB-51-X-A",
        "SB-51-X-C",
        "SB-51-V-D",
        "SB-50-X-D",
        "SB-51-V-C",
        "NA-51-Z-D",
        "NA-51-Z-C",
        "NA-51-Y-D",
        "NA-51-Y-C",
        "SA-51-X-D",
        "SA-51-X-C",
        "SA-51-V-D",
        "SA-51-V-C",
        "SB-51-Y-A",
        "SB-51-Y-D",
        "SB-51-Y-C",
        "SA-50-X-B",
        "SA-50-X-D",
        "NA-51-X-D",
        "NA-51-X-B",
        "NA-52-V-A",
        "NB-51-Z-D",
        "NB-52-Y-C",
        "SB-51-Z-A",
        "SA-51-X-A",
        "SA-51-V-B",
        "SA-51-V-A",
        "NA-51-Y-A",
        "NA-51-Y-B",
        "NA-51-Z-A",
        "NA-51-Z-B",
        "SA-51-Z-A",
        "SA-51-Y-B",
        "SA-50-Z-B",
        "SA-51-Y-A",
        "SA-51-Y-C",
        "SA-51-Y-D",
        "SA-50-Z-D",
        "SA-51-Z-C",
        "SA-47-Z-B",
        "SA-47-Z-A",
        "SA-47-Z-D",
        "SA-47-Z-C",
        "SB-48-V-A",
        "SB-47-X-B",
        "SB-48-V-B",
        "SB-48-X-A",
        "SB-48-X-D",
        "SB-48-X-C",
        "SB-48-V-D",
        "SB-48-V-C",
        "SB-48-Z-A",
        "SB-48-Z-B",
        "SB-49-Y-A",
        "SB-49-Y-B",
        "SB-48-Z-C",
        "SB-48-Z-D",
        "SB-49-Y-D",
        "SB-49-Y-C",
        "SC-49-V-B",
        "SA-47-X-D",
        "SA-47-V-D",
        "SA-47-X-C",
        "SA-49-X-B",
        "SA-49-X-A",
        "SA-49-V-B",
        "SA-49-V-A",
        "NA-48-Z-B",
        "NA-49-Y-A",
        "NA-49-Y-B",
        "NA-49-Z-B",
        "NA-49-Z-A",
        "SA-49-Y-B",
        "NA-49-V-C",
        "NA-49-V-D",
        "NA-48-X-C",
        "NA-48-X-D",
        "NA-49-V-A",
        "NA-48-X-A",
        "NA-48-X-B",
        "NB-49-Y-C",
        "NB-48-Z-D",
        "NA-49-Z-D",
        "NA-49-Z-C",
        "NA-49-Y-D",
        "NA-49-Y-C",
        "NA-48-Z-D",
        "SA-49-V-D",
        "SA-49-V-C",
        "SB-53-V-C",
        "SB-53-V-D",
        "SB-52-Z-B",
        "SB-53-Y-A",
        "SB-53-Y-B",
        "SB-52-Z-D",
        "SB-51-Z-D",
        "SB-52-Y-C",
        "SB-52-Z-C",
        "SB-52-Y-D",
        "SC-51-X-A",
        "SC-51-X-B",
        "SC-52-X-B",
        "SC-52-X-A",
        "SC-52-V-B",
        "SC-52-V-A",
        "SC-51-X-C",
        "SC-51-X-D",
        "SC-51-Z-A",
        "SC-51-Z-B",
        "SA-50-X-A",
        "SA-50-V-B",
        "SA-50-V-A",
        "NA-50-Y-A",
        "NA-50-Y-B",
        "NA-50-Z-A",
        "NA-50-Z-B",
        "NA-50-V-C",
        "NA-50-V-D",
        "NA-50-X-C",
        "NA-50-X-D",
        "NA-50-V-B",
        "NA-50-X-A",
        "NA-50-V-A",
        "NB-50-Z-C",
        "NB-50-Y-D",
        "NA-50-Z-D",
        "NA-50-Z-C",
        "NA-50-Y-D",
        "NA-50-Y-C",
        "SA-50-X-C"
    ],
}

collectionIds = {
    'l4': 'LANDSAT/LT04/C02/T1_TOA',
    'l5': 'LANDSAT/LT05/C02/T1_TOA',
    'l7': 'LANDSAT/LE07/C02/T1_TOA',
    'l8': 'LANDSAT/LC08/C02/T1_TOA',
    'l9': 'LANDSAT/LC09/C02/T1_TOA',
}

landsatIds = {
    'l4': 'landsat-4',
    'l5': 'landsat-5',
    'l7': 'landsat-7',
    'l8': 'landsat-8',
    'l9': 'landsat-9',
}

outputCollections = {
    'l4': 'projects/nexgenmap/MapBiomas2/LANDSAT/INDONESIA/mosaics-2',
    'l5': 'projects/nexgenmap/MapBiomas2/LANDSAT/INDONESIA/mosaics-2',
    'l7': 'projects/nexgenmap/MapBiomas2/LANDSAT/INDONESIA/mosaics-2',
    'l8': 'projects/nexgenmap/MapBiomas2/LANDSAT/INDONESIA/mosaics-2',
    'l9': 'projects/nexgenmap/MapBiomas2/LANDSAT/INDONESIA/mosaics-2'
}

bufferSize = 100

yearsSat = [
    [2023, 'l8'],
    [2023, 'l9'],
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
    # [2012, 'l7'],
    # [2002, 'l7'],
    # [2001, 'l7'],
    # [2000, 'l7'],
    # [2005, 'l7'],
    # [2004, 'l7'],
    # [2003, 'l7'],
    # [2022, 'l7'],
    # [2021, 'l7'],
    # [2020, 'l7'],
    # [2019, 'l7'],
    # [2018, 'l7'],
    # [2017, 'l7'],
    # [2016, 'l7'],
    # [2015, 'l7'],
    # [2014, 'l7'],
    # [2013, 'l7'],
    # [2011, 'l7'],
    # [2010, 'l7'],
    # [2009, 'l7'],
    # [2008, 'l7'],
    # [2007, 'l7'],
    # [2006, 'l7'],
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
                                   cloudBand='cloudScoreMask')

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


# get all tile names
collectionTiles = ee.ImageCollection(assetMasks)

allTiles = collectionTiles.reduceColumns(
    ee.Reducer.toList(), ['tile']).get('list').getInfo()

for territoryName in territoryNames:

    grids = ee.FeatureCollection(gridsAsset)\
        .filter(ee.Filter.inList('name', gridNames[territoryName])
    )

    for year, satellite in yearsSat:

        dateStart = '{}-{}'.format(year,
                                   dataFilter[territoryName]['dateStart'])
        dateEnd = '{}-{}'.format(year, dataFilter[territoryName]['dateEnd'])
        cloudCover = dataFilter[territoryName]['cloudCover']

        for gridName in gridNames[territoryName]:
            print(gridName)
            try:
                # if True:
                alreadyInCollection = ee.ImageCollection(outputCollections[satellite]) \
                    .filter(ee.Filter.eq('year', year)) \
                    .filter(ee.Filter.eq('territory', territoryName)) \
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
                                               trashList=excluded,
                                               scaleFactor=True,
                                               collectionType='TOA'
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

                    print(len(tiles))
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
                        bands = getBandNames(satellite + 'c2toa')
                        # bands = getBandNames(satellite + 'c2')

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
                        collection = (
                            collection
                            .map(divideBy10000)
                            .map(getCAI)
                            .map(getEVI2)
                            .map(getGCVI)
                            .map(getHallCover)
                            .map(getHallHeigth)
                            .map(getNDVI)
                            .map(getNDWI)
                            .map(getPRI)
                            .map(getSAVI)
                            .map(multiplyBy10000)
                        )

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
                        mosaic = setBandTypes(mosaic, mtype='indonesia')

                        mosaic = mosaic.set('year', year)
                        mosaic = mosaic.set('collection', 2.0)
                        mosaic = mosaic.set('name', gridName)
                        mosaic = mosaic.set(
                            'version', str(version[territoryName]))
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
                print(e)
                if e == msg:
                    raise Exception(e)
