"""
Google Earth Engine Landsat Mosaic Generator for Peru
===========================================================

This script generates annual Landsat mosaics for Peru using Google Earth Engine.
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


import pandas as pd
from datetime import datetime, timedelta

# sys.path.append(os.path.abspath('../gee_toolbox'))
# import gee as gee_toolbox

ee.Authenticate()
ee.Initialize(project='mapbiomas-peru')

# Set up account to use
# ACCOUNT = 'mapbiomas1'

# Set up version
version = '1'

versionMasks = '2'

gridsAsset = 'projects/mapbiomas-raisg/DATOS_AUXILIARES/VECTORES/grid-world'

assetMasks = "projects/mapbiomas-workspace/AUXILIAR/landsat-mask"

csvFile = '../data/peru_parametrizacion-2025-test-701-28-nov.csv'

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
    'l4': 'projects/mapbiomas-mosaics/assets/LANDSAT/LULC/CHILE/mosaics-1',
    'l5': 'projects/mapbiomas-mosaics/assets/LANDSAT/LULC/CHILE/mosaics-1',
    'l7': 'projects/mapbiomas-mosaics/assets/LANDSAT/LULC/CHILE/mosaics-1',
    'l8': 'projects/mapbiomas-mosaics/assets/LANDSAT/LULC/CHILE/mosaics-1',
    'l9': 'projects/mapbiomas-mosaics/assets/LANDSAT/LULC/CHILE/mosaics-1',
    'lx': 'projects/mapbiomas-mosaics/assets/LANDSAT/LULC/CHILE/mosaics-1',
    'ly': 'projects/mapbiomas-mosaics/assets/LANDSAT/LULC/CHILE/mosaics-1'
}

bufferSize = 100

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
        # 'hallheigth',
        'ndvi',
        # 'ndwi',
        'pri',
        'savi',
        'ndwi_gao',
        'ndwi_mcfeeters',
        'ndsi',
        'ndsi2',
        'ndbi',
        'ndmi',
        'gli',
        'mndwi',
        'ndmir',
        'ndrb',
        'ndgb'
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


def applyCloudAndShadowMask(collection,shadowsum, cloudThresh):

    # Get cloud and shadow masks
    collectionWithMasks = getMasks(collection,
                                   cloudThresh=cloudThresh,
                                   cloudFlag=True,
                                   cloudScore=True,
                                   cloudShadowFlag=True,
                                   cloudShadowTdom=True,
                                   zScoreThresh=-1,
                                   shadowSumThresh=shadowsum, # 3500
                                   dilatePixels=4,
                                   cloudHeights=[
                                       200, 700, 1200, 1700, 2200, 2700,
                                       3200, 3700, 4200, 4700
                                   ],
                                   cloudBand='cloudScoreMask') #cloudScoreMask,  'cloudFlagMask'

    # get collection without clouds
    collectionWithoutClouds = collectionWithMasks \
        .map(
            lambda image: image.mask(
                image.select([
                    'cloudFlagMask',
                    'cloudScoreMask',
                    'cloudShadowFlagMask',
                    'cloudShadowTdomMask'
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


def getExcludedImages(country, year):

    assetId = 'projects/mapbiomas-raisg/MOSAICOS/mosaics-2-temp2'

    collection = ee.ImageCollection(assetId) \
        .filterMetadata('region', 'equals', biome) \
        .filterMetadata('year', 'equals', str(year))

    excluded = ee.List(collection.reduceColumns(ee.Reducer.toList(), ['black_list']).get('list')) \
        .map(
            lambda names: ee.String(names).split(',')
    )

    return excluded.flatten().getInfo()

# Set up the blacklist of images
def sepReplace(images):
    separators = ['-','--', ';', '-', "'"]

    images = images.replace(' ', '').replace('\n', '').replace("'", '')

    for sep in separators:
        images = images.replace( sep, ',' )

    return images.split(',')

# gee_toolbox.switch_user(ACCOUNT)
# gee_toolbox.init()

# load csv file data
table = pd.read_csv(csvFile)
table = table[table.PROCESS == 1]

# load grids asset
grids = ee.FeatureCollection(gridsAsset)

# get all tile names  (why ?)
collectionTiles = ee.ImageCollection(assetMasks)

allTiles = collectionTiles.reduceColumns(
    ee.Reducer.toList(), ['tile']).get('list').getInfo()

contador = 1

for row in table.itertuples():
    
    dateStartP = datetime.strptime(row.T0_P, "%d/%m/%Y").strftime("%Y-%m-%d")
    dateEndP = datetime.strptime(row.T1_P, "%d/%m/%Y").strftime("%Y-%m-%d")
    dateStartS = datetime.strptime(row.T0_S, "%d/%m/%Y").strftime("%Y-%m-%d")
    dateEndS = datetime.strptime(row.T1_S, "%d/%m/%Y").strftime("%Y-%m-%d")
    blacklist = sepReplace(str(row.BLACKLIST))
    satelliteId = row.SATELLITE.lower()

    # add 1 day to dateEndP
    dateEndS = datetime.strptime(dateEndS, "%Y-%m-%d") + timedelta(days=1)
    dateEndS = dateEndS.strftime("%Y-%m-%d")

    # satellites = []
    # satellites = [row.SATELLITE.lower()]
    # if row.SATELLITE.lower() == 'lx':
    #     satellites = ['l5', 'l7']
    # else:
    #     satellites = [row.SATELLITE.lower()]

    try:
    # if True:
        alreadyInCollection = ee.ImageCollection(outputCollections[satelliteId]) \
            .filterMetadata('year', 'equals', int(row.YEAR)) \
            .filterMetadata('country', 'equals', row.COUNTRY) \
            .reduceColumns(ee.Reducer.toList(), ['system:index']) \
            .get('list') \
            .getInfo()

        outputName = row.COUNTRY + '-' + \
            row.GRID_NAME + '-' + \
            row.SATELLITE + '-' + \
            str(row.YEAR) + '-' + \
            str(row.REGION_CODE) + '-' + \
            str(version)
        
        if outputName not in alreadyInCollection:

            # define a geometry
            grid = grids.filterMetadata('name', 'equals', row.GRID_NAME)
                
            grid = ee.Feature(grid.first()).geometry()\
                .buffer(bufferSize).bounds()
            # grid = ee.Geometry.Polygon([[[-76.4956, -11.5040], [-76.4956, -11.5659], [-75.0180, -11.5659],[-75.0180, -11.50406]]])

            # excluded = []
            # if row.COUNTRY == 'ZPERU':
            #     excluded = getExcludedImages(row.COUNTRY, row.YEAR)
            if satelliteId != 'lx' and satelliteId != 'ly' :
                # returns a collection containing the specified parameters
                collection = getCollection(collectionIds[satelliteId],
                                        dateStart=dateStartS,
                                        dateEnd=dateEndS,
                                        cloudCover=row.CLOUD_COVER,
                                        geometry=grid,
                                        blacklist= blacklist
                                        )
                
                # returns a pattern of band names
                bands = getBandNames(satelliteId + 'c2')
            
                endmember = ENDMEMBERS[landsatIds[satelliteId]]
                
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
                        # print(tile['path'], tile['row'])

                        subcollection = collection \
                            .filterMetadata('WRS_PATH', 'equals', tile['path']) \
                            .filterMetadata('WRS_ROW', 'equals', tile['row'])
                        
                        # tileMask = ee.Image(
                        #     '{}/{}-{}'.format(assetMasks, tile['id'], versionMasks))
                        
                        # subcollection = subcollection.map(
                        #     lambda image: image.mask(tileMask).selfMask()
                        # )
                        
                        subcollectionList.append(subcollection)
                    
                    # merge collections
                    collection = ee.List(subcollectionList) \
                        .iterate(
                            lambda subcollection, collection:
                                ee.ImageCollection(collection).merge(subcollection),
                            ee.ImageCollection([])
                    )
                    
                    # flattens collections of collections
                    collection = ee.ImageCollection(collection)

                    # Rename collection image bands
                    collection = collection.select(
                        bands['bandNames'],
                        bands['newNames']
                    )

            elif satelliteId == 'lx':

                collectionl4 = getCollection(collectionIds['l4'],
                                        dateStart=dateStartS,
                                        dateEnd=dateEndS,
                                        cloudCover=row.CLOUD_COVER,
                                        geometry=grid,
                                        blacklist= blacklist
                                        )

                # returns a pattern of band names
                bandsl4 = getBandNames('l4'+ 'c2')
                # detect the image tiles
                tilesl4 = getTiles(collectionl4)
                tilesl4 = list(
                    filter(
                        lambda tile: tile['id'] in allTiles,
                        tilesl4
                    )
                )
                subcollectionListl4 = []

                if len(tilesl4) > 0:
                    # apply tile mask for each image
                    for tile in tilesl4:
                        # print(tile['path'], tile['row'])

                        subcollectionl4 = collectionl4 \
                            .filterMetadata('WRS_PATH', 'equals', tile['path']) \
                            .filterMetadata('WRS_ROW', 'equals', tile['row'])
                        
                        # tileMask = ee.Image(
                        #     '{}/{}-{}'.format(assetMasks, tile['id'], versionMasks))
                        
                        # subcollectionl5 = subcollectionl5.map(
                        #     lambda image: image.mask(tileMask).selfMask()
                        # )
                        
                        subcollectionListl4.append(subcollectionl4)
                    
                    # merge collections
                    collectionl4 = ee.List(subcollectionListl4) \
                        .iterate(
                            lambda subcollectionl4, collectionl4:
                                ee.ImageCollection(collectionl4).merge(subcollectionl4),
                            ee.ImageCollection([])
                    )
                    
                    # flattens collections of collections
                    collectionl4 = ee.ImageCollection(collectionl4)
                    # Rename collection image bands
                    collectionl4 = collectionl4.select(
                        bandsl4['bandNames'],
                        bandsl4['newNames']
                    )


                collectionl5 = getCollection(collectionIds['l5'],
                                        dateStart=dateStartS,
                                        dateEnd=dateEndS,
                                        cloudCover=row.CLOUD_COVER,
                                        geometry=grid,
                                        blacklist= blacklist
                                        )

                # returns a pattern of band names
                bandsl5 = getBandNames('l5'+ 'c2')
                # detect the image tiles
                tilesl5 = getTiles(collectionl5)
                tilesl5 = list(
                    filter(
                        lambda tile: tile['id'] in allTiles,
                        tilesl5
                    )
                )
                subcollectionListl5 = []

                if len(tilesl5) > 0:
                    # apply tile mask for each image
                    for tile in tilesl5:
                        # print(tile['path'], tile['row'])

                        subcollectionl5 = collectionl5 \
                            .filterMetadata('WRS_PATH', 'equals', tile['path']) \
                            .filterMetadata('WRS_ROW', 'equals', tile['row'])
                        
                        # tileMask = ee.Image(
                        #     '{}/{}-{}'.format(assetMasks, tile['id'], versionMasks))
                        
                        # subcollectionl5 = subcollectionl5.map(
                        #     lambda image: image.mask(tileMask).selfMask()
                        # )
                        
                        subcollectionListl5.append(subcollectionl5)
                    
                    # merge collections
                    collectionl5 = ee.List(subcollectionListl5) \
                        .iterate(
                            lambda subcollectionl5, collectionl5:
                                ee.ImageCollection(collectionl5).merge(subcollectionl5),
                            ee.ImageCollection([])
                    )
                    
                    # flattens collections of collections
                    collectionl5 = ee.ImageCollection(collectionl5)
                    # Rename collection image bands
                    collectionl5 = collectionl5.select(
                        bandsl5['bandNames'],
                        bandsl5['newNames']
                    )

                collectionl7 = getCollection(collectionIds['l7'],
                                        dateStart=dateStartS,
                                        dateEnd=dateEndS,
                                        cloudCover=row.CLOUD_COVER,
                                        geometry=grid,
                                        blacklist= blacklist
                                            )

                # returns a pattern of band names
                bandsl7 = getBandNames('l7'+ 'c2')
                # detect the image tiles
                tilesl7 = getTiles(collectionl7)
                tilesl7 = list(
                    filter(
                        lambda tile: tile['id'] in allTiles,
                        tilesl7
                    )
                )
                subcollectionListl7 = []

                if len(tilesl7) > 0:
                    # apply tile mask for each image
                    for tile in tilesl7:
                        # print(tile['path'], tile['row'])

                        subcollectionl7 = collectionl7 \
                            .filterMetadata('WRS_PATH', 'equals', tile['path']) \
                            .filterMetadata('WRS_ROW', 'equals', tile['row'])
                        
                        # tileMask = ee.Image(
                        #     '{}/{}-{}'.format(assetMasks, tile['id'], versionMasks))
                        
                        # subcollectionl7 = subcollectionl7.map(
                        #     lambda image: image.mask(tileMask).selfMask()
                        # )
                        
                        subcollectionListl7.append(subcollectionl7)
                    
                    # merge collections
                    collectionl7 = ee.List(subcollectionListl7) \
                        .iterate(
                            lambda subcollectionl7, collectionl7:
                                ee.ImageCollection(collectionl7).merge(subcollectionl7),
                            ee.ImageCollection([])
                    )
                    
                    # flattens collections of collections
                    collectionl7 = ee.ImageCollection(collectionl7)
                    # Rename collection image bands
                    collectionl7 = collectionl7.select(
                        bandsl7['bandNames'],
                        bandsl7['newNames']
                    )
                # merge collections
                collection = collectionl5.merge(collectionl7).merge(collectionl4)
                endmember = ENDMEMBERS[landsatIds['l5']]

            elif satelliteId == 'ly':
                collectionl8 = getCollection(collectionIds['l8'],
                                        dateStart=dateStartS,
                                        dateEnd=dateEndS,
                                        cloudCover=row.CLOUD_COVER,
                                        geometry=grid,
                                        blacklist= blacklist
                                        )

                # returns a pattern of band names
                bandsl8 = getBandNames('l8'+ 'c2')
                # detect the image tiles
                tilesl8 = getTiles(collectionl8)
                tilesl8 = list(
                    filter(
                        lambda tile: tile['id'] in allTiles,
                        tilesl8
                    )
                )
                subcollectionListl8 = []

                if len(tilesl8) > 0:
                    # apply tile mask for each image
                    for tile in tilesl8:
                        # print(tile['path'], tile['row'])

                        subcollectionl8 = collectionl8 \
                            .filterMetadata('WRS_PATH', 'equals', tile['path']) \
                            .filterMetadata('WRS_ROW', 'equals', tile['row'])
                        
                        # tileMask = ee.Image(
                        #     '{}/{}-{}'.format(assetMasks, tile['id'], versionMasks))
                        
                        # subcollectionl5 = subcollectionl5.map(
                        #     lambda image: image.mask(tileMask).selfMask()
                        # )
                        
                        subcollectionListl8.append(subcollectionl8)
                    
                    # merge collections
                    collectionl8 = ee.List(subcollectionListl8) \
                        .iterate(
                            lambda subcollectionl8, collectionl8:
                                ee.ImageCollection(collectionl8).merge(subcollectionl8),
                            ee.ImageCollection([])
                    )
                    
                    # flattens collections of collections
                    collectionl8 = ee.ImageCollection(collectionl8)
                    # Rename collection image bands
                    collectionl8 = collectionl8.select(
                        bandsl8['bandNames'],
                        bandsl8['newNames']
                    )

                collectionl9 = getCollection(collectionIds['l9'],
                                        dateStart=dateStartS,
                                        dateEnd=dateEndS,
                                        cloudCover=row.CLOUD_COVER,
                                        geometry=grid,
                                        blacklist= blacklist
                                            )

                # returns a pattern of band names
                bandsl9 = getBandNames('l9'+ 'c2')
                # detect the image tiles
                tilesl9 = getTiles(collectionl9)
                tilesl9 = list(
                    filter(
                        lambda tile: tile['id'] in allTiles,
                        tilesl9
                    )
                )
                subcollectionListl9 = []

                if len(tilesl9) > 0:
                    # apply tile mask for each image
                    for tile in tilesl9:
                        # print(tile['path'], tile['row'])

                        subcollectionl9 = collectionl9 \
                            .filterMetadata('WRS_PATH', 'equals', tile['path']) \
                            .filterMetadata('WRS_ROW', 'equals', tile['row'])
                        
                        # tileMask = ee.Image(
                        #     '{}/{}-{}'.format(assetMasks, tile['id'], versionMasks))
                        
                        # subcollectionl7 = subcollectionl7.map(
                        #     lambda image: image.mask(tileMask).selfMask()
                        # )
                        
                        subcollectionListl9.append(subcollectionl9)
                    
                    # merge collections
                    collectionl9 = ee.List(subcollectionListl9) \
                        .iterate(
                            lambda subcollectionl9, collectionl9:
                                ee.ImageCollection(collectionl9).merge(subcollectionl9),
                            ee.ImageCollection([])
                    )
                    
                    # flattens collections of collections
                    collectionl9 = ee.ImageCollection(collectionl9)
                    # Rename collection image bands
                    collectionl9 = collectionl9.select(
                        bandsl9['bandNames'],
                        bandsl9['newNames']
                    )
                # merge collections
                collection = collectionl8.merge(collectionl9)
                endmember = ENDMEMBERS[landsatIds['l8']]



            collection = applyCloudAndShadowMask(collection, row.SHADOWSUM, row.CLOUD_THRESH)
            
            collection = collection.map(
                lambda image: image.addBands(getFractions(image, endmember[:4]))
            )
            
            # calculate SMA indexes
            collection = collection\
                .map(
                    lambda image: getNDFIb(image, endmember)
                    ) \
                .map(getNDFI)\
                .map(getSEFI)\
                .map(getWEFI)\
                .map(getFNS)


            
            # calculate Spectral indexes
            collection = collection\
                .map(divideBy10000)\
                .map(getHallCover ) \
                .map(getNDVI ) \
                .map(getEVI2 ) \
                .map(getNDWIGao ) \
                .map(getNDWI_mcfeeters ) \
                .map(getNDSI ) \
                .map(getPRI ) \
                .map(getSAVI ) \
                .map(getGCVI ) \
                .map(getNUACI ) \
                .map(getNDBI ) \
                .map(getCAI ) \
                .map(getNDSI2 ) \
                .map(getNDMI ) \
                .map(getGLI ) \
                .map(getMNDWI ) \
                .map(getNDMIR ) \
                .map(getNDRB ) \
                .map(getNDGB ) \
                .map(multiplyBy10000)

                # .map(getTextG ) \

            # generate mosaic       
            mosaic = getMosaic(collection,
                            percentileDry=25,
                            percentileWet=75,
                            dateStart=dateStartP,
                            dateEnd=dateEndP)

            nimage = collection.filterDate(dateStartP, dateEndP)\
                                .size().getInfo()

            mosaic = getEntropyG(mosaic)
            # mosaic = getSlope(mosaic)
            mosaic = setBandTypes(mosaic)

            mosaic = mosaic.set('year', int(row.YEAR))
            mosaic = mosaic.set('collection', 4.0)
            mosaic = mosaic.set('grid_name', row.GRID_NAME)
            mosaic = mosaic.set('version', str(version))
            mosaic = mosaic.set('country', row.COUNTRY)
            mosaic = mosaic.set('satellite', satelliteId)
            mosaic = mosaic.set('region', row.REGION_NAME)
            mosaic = mosaic.set('region_code', int(row.REGION_CODE))
            mosaic = mosaic.set('nimages', nimage)
            mosaic = mosaic.set('dtstartp', dateStartP)
            mosaic = mosaic.set('dtendp', dateEndP)
            mosaic = mosaic.set('cloud_cover', row.CLOUD_COVER)
            mosaic = mosaic.set('processed', date.today().strftime("%Y-%m-%d"))

            # print(outputName)
            print(str(contador) + '-' + outputName)
            contador = contador + 1

            task = ee.batch.Export.image.toAsset(
                image=mosaic,
                description=outputName,
                assetId=outputCollections[satelliteId] + '/' + outputName,
                region=grid.coordinates().getInfo(),
                scale=30,
                maxPixels=int(1e13),

            )
            
            task.start()

    except Exception as e:
        print(e)

# gee_toolbox.switch_user('joao')
# gee_toolbox.init()

