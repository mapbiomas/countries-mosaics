import ee
import sys
import os

sys.path.append(os.path.abspath('../'))

from modules.CloudAndShadowMaskC2 import *
from modules.SpectralIndexes import *
from modules.Miscellaneous import *
from modules.SmaAndNdfi import *
from modules.Collection import *
from modules.BandNames import * 
from modules.DataType import *
from modules.Mosaic import *

sys.dont_write_bytecode = True

ee.Initialize()


versionMasks = '2'

gridsAsset = 'projects/mapbiomas-workspace/AUXILIAR/cim-world-1-250000'

assetMasks = "projects/mapbiomas-workspace/AUXILIAR/landsat-mask"


# nome do bioma sem espaço
territoryNames = [
    'MEXICO',
]

version = {
    'MEXICO': '1',
}

dataFilter = {
    'MEXICO': {
        'dateStart': '01-01',
        'dateEnd': '12-31',
        'cloudCover': 80
    },
}

gridNames = {
    "MEXICO": [
        "NE-12-X-A",
        "NE-12-X-B",
        "NE-12-X-C",
        "NE-12-X-D",
        "NF-12-X-A",
        "NF-12-X-B",
        "NF-12-X-C",
        "NF-12-X-D",
        "NF-12-Z-A",
        "NF-12-Z-B",
        "NF-12-Z-C",
        "NF-12-Z-D",
        "NE-13-V-A",
        "NE-13-V-B",
        "NE-13-V-C",
        "NE-13-V-D",
        "NE-13-X-A",
        "NE-13-X-B",
        "NE-13-X-C",
        "NE-13-X-D",
        "NF-13-V-A",
        "NF-13-V-B",
        "NF-13-V-C",
        "NF-13-V-D",
        "NF-13-X-A",
        "NF-13-X-B",
        "NF-13-X-C",
        "NF-13-X-D",
        "NF-13-Y-A",
        "NF-13-Y-B",
        "NF-13-Y-C",
        "NF-13-Y-D",
        "NF-13-Z-A",
        "NF-13-Z-B",
        "NF-13-Z-C",
        "NF-13-Z-D",
        "NE-14-V-A",
        "NE-14-V-B",
        "NE-14-V-C",
        "NE-14-V-D",
        "NE-14-X-A",
        "NE-14-X-B",
        "NE-14-X-C",
        "NE-14-X-D",
        "NF-14-V-A",
        "NF-14-V-B",
        "NF-14-V-C",
        "NF-14-V-D",
        "NF-14-X-A",
        "NF-14-X-B",
        "NF-14-X-C",
        "NF-14-X-D",
        "NF-14-Y-A",
        "NF-14-Y-B",
        "NF-14-Y-C",
        "NF-14-Y-D",
        "NF-14-Z-A",
        "NF-14-Z-B",
        "NF-14-Z-C",
        "NF-14-Z-D",
        "NE-15-V-A",
        "NE-15-V-C",
        "NF-15-V-A",
        "NF-15-V-C",
        "NF-15-Y-A",
        "NF-15-Y-C"
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

outputCollections = {
    'l4': 'projects/mapbiomas-mosaics/assets/LANDSAT/LULC/MEXICO/mosaics-1',
    'l5': 'projects/mapbiomas-mosaics/assets/LANDSAT/LULC/MEXICO/mosaics-1',
    'l7': 'projects/mapbiomas-mosaics/assets/LANDSAT/LULC/MEXICO/mosaics-1',
    'l8': 'projects/mapbiomas-mosaics/assets/LANDSAT/LULC/MEXICO/mosaics-1',
    'l9': 'projects/mapbiomas-mosaics/assets/LANDSAT/LULC/MEXICO/mosaics-1'
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
