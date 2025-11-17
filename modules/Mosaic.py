"""
Google Earth Engine Mosaic Generation Module
=============================================

This module provides functions to generate different types of composite mosaics
from satellite image collections using various statistical reducers. It supports
three specialized mosaic types optimized for different land use applications:
1. General LULC (Land Use Land Cover) mosaics
2. Agriculture-focused mosaics
3. Urban area mosaics

Dependencies: earthengine-api, custom BandNames module
"""

import ee
from modules.BandNames import getBandNames
from pprint import pprint

# Uncomment to initialize Earth Engine (typically done in main script)
# ee.Initialize()


def getMosaic(
        collection,
        percentileDry=25,
        percentileWet=75,
        percentileBand='ndvi',
        dateStart='2020-01-01',
        dateEnd='2020-12-31'):
    """
    Generate a comprehensive multi-temporal mosaic with dry/wet season statistics.
    
    This function creates a composite image that captures seasonal variations by
    identifying dry and wet seasons based on vegetation index percentiles. It's
    particularly useful for phenology analysis and land cover classification in
    regions with distinct wet/dry seasons.
    
    The algorithm works by:
    1. Computing percentile thresholds on a quality band (typically NDVI)
    2. Subsetting images into dry season (low percentile) and wet season (high percentile)
    3. Calculating statistics (median, min, max, stdDev, amplitude) for each season
    
    Args:
        collection (ee.ImageCollection): Input image collection with all bands
        percentileDry (int, optional): Percentile threshold for dry season (default: 25)
            Lower values = drier conditions. Typical range: 10-30
        percentileWet (int, optional): Percentile threshold for wet season (default: 75)
            Higher values = wetter conditions. Typical range: 70-90
        percentileBand (str, optional): Band used to determine seasons (default: 'ndvi')
            Common options: 'ndvi' (vegetation), 'ndwi' (water), 'evi2'
        dateStart (str, optional): Start date for mosaic period (default: '2020-01-01')
            Format: 'YYYY-MM-DD'
        dateEnd (str, optional): End date for mosaic period (default: '2020-12-31')
            Format: 'YYYY-MM-DD'
    
    Returns:
        ee.Image: Multi-band mosaic containing:
            - *_median: Overall median for each band
            - *_median_dry: Median of dry season pixels for each band
            - *_median_wet: Median of wet season pixels for each band
            - *_min: Minimum value for each band
            - *_max: Maximum value for each band
            - *_amp: Amplitude (max - min) for each band
            - *_stdDev: Standard deviation for each band
            - {percentileBand}_p{percentileDry}: Dry season threshold image
            - {percentileBand}_p{percentileWet}: Wet season threshold image
    
    Example:
        >>> collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \\
        ...     .filterBounds(roi) \\
        ...     .filterDate('2020-01-01', '2020-12-31')
        >>> mosaic = getMosaic(collection, 
        ...                    percentileDry=25, 
        ...                    percentileWet=75,
        ...                    percentileBand='ndvi')
        >>> # Access specific bands
        >>> ndvi_dry = mosaic.select('ndvi_median_dry')
        >>> amplitude = mosaic.select('ndvi_amp')
    
    Note:
        - Images with percentileBand values ≤ percentileDry threshold are classified as "dry"
        - Images with percentileBand values ≥ percentileWet threshold are classified as "wet"
        - Amplitude bands help identify temporal variability (useful for cropland detection)
    """
    # Extract all band names from the first image in the collection
    bands = ee.Image(collection.first()).bandNames()

    # Create band name suffixes for dry season statistics
    # Example: 'ndvi' becomes 'ndvi_median_dry'
    bandsDry = bands.map(lambda band:
                         ee.String(band).cat('_median_dry')
                         )

    # Create band name suffixes for wet season statistics
    # Example: 'ndvi' becomes 'ndvi_median_wet'
    bandsWet = bands.map(lambda band:
                         ee.String(band).cat('_median_wet')
                         )

    # Create band name suffixes for amplitude statistics
    # Example: 'ndvi' becomes 'ndvi_amp'
    bandsAmp = bands.map(lambda band:
                         ee.String(band).cat('_amp')
                         )

    # ========================================================================
    # DRY SEASON PROCESSING
    # ========================================================================
    
    # Calculate the dry season threshold using the specified percentile
    # This creates a single-band image representing the percentile value
    dry = collection\
        .select([percentileBand])\
        .reduce(ee.Reducer.percentile([percentileDry]))

    # Create dry season collection by masking images where the quality band
    # is less than or equal to the dry threshold
    collectionDry = collection.map(
        lambda image:
            image.mask(image.select([percentileBand]).lte(dry))
    )

    # ========================================================================
    # WET SEASON PROCESSING
    # ========================================================================
    
    # Calculate the wet season threshold using the specified percentile
    wet = collection\
        .select([percentileBand])\
        .reduce(ee.Reducer.percentile([percentileWet]))

    # Create wet season collection by masking images where the quality band
    # is greater than or equal to the wet threshold
    collectionWet = collection.map(
        lambda image:
            image.mask(image.select([percentileBand]).gte(wet))
    )

    # ========================================================================
    # MOSAIC STATISTICS CALCULATION
    # ========================================================================
    
    # Overall median mosaic for the entire time period
    mosaic = collection.filter(
        ee.Filter.date(dateStart, dateEnd)
    ).reduce(ee.Reducer.median())

    # Dry season median mosaic (only pixels below dry threshold)
    mosaicDry = collectionDry.reduce(ee.Reducer.median())\
        .rename(bandsDry)

    # Wet season median mosaic (only pixels above wet threshold)
    mosaicWet = collectionWet.reduce(ee.Reducer.median())\
        .rename(bandsWet)

    # Minimum value mosaic across all images
    mosaicMin = collection.reduce(ee.Reducer.min())

    # Maximum value mosaic across all images
    mosaicMax = collection.reduce(ee.Reducer.max())

    # Amplitude mosaic (difference between max and min)
    # High amplitude often indicates seasonal crops or deciduous vegetation
    mosaicAmp = mosaicMax.subtract(mosaicMin)\
        .rename(bandsAmp)

    # Standard deviation mosaic (temporal variability)
    mosaicStdDev = collection.reduce(ee.Reducer.stdDev())

    # ========================================================================
    # COMBINE ALL BANDS INTO FINAL MOSAIC
    # ========================================================================
    
    mosaic = mosaic\
        .addBands(mosaicDry)\
        .addBands(mosaicWet)\
        .addBands(mosaicMin)\
        .addBands(mosaicMax)\
        .addBands(mosaicAmp)\
        .addBands(mosaicStdDev)\
        .addBands(dry)\
        .addBands(wet)

    return mosaic


def getMosaicAgriculture(
        collection,
        percentiles=[20, 75],
        qualityBand='evi2'):
    """
    Generate an agriculture-optimized mosaic with quality-based compositing.
    
    This function creates mosaics specifically designed for agricultural monitoring
    and crop mapping. It uses a quality mosaic approach where the "best" pixel
    is selected based on a vegetation index value (typically EVI2), which helps
    capture peak vegetation conditions important for crop classification.
    
    The quality mosaic (QMO) selects pixels with the highest values in the quality
    band, which often correspond to peak crop growth or optimal observation conditions.
    
    Args:
        collection (ee.ImageCollection): Input image collection with all bands
        percentiles (list, optional): Two percentile values for temporal analysis
            (default: [20, 75]). Lower value captures drier/earlier conditions,
            higher value captures wetter/later conditions
        qualityBand (str, optional): Band used for quality mosaic selection (default: 'evi2')
            Common options: 'evi2', 'ndvi', 'gcvi' (green vegetation indices)
    
    Returns:
        ee.Image: Multi-band mosaic containing:
            - *_median: Median value for each band across all images
            - *_p{percentile[0]}: Lower percentile value for each band
            - *_p{percentile[1]}: Upper percentile value for each band
            - *_min: Minimum value for each band
            - *_max: Maximum value for each band
            - *_stdDev: Standard deviation for each band
            - *_qmo: Quality mosaic (highest quality pixels) for each band
    
    Example:
        >>> collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \\
        ...     .filterBounds(farmland) \\
        ...     .filterDate('2020-04-01', '2020-09-30')  # Growing season
        >>> mosaic = getMosaicAgriculture(collection,
        ...                               percentiles=[25, 75],
        ...                               qualityBand='evi2')
        >>> # Quality mosaic often shows peak greenness
        >>> ndvi_peak = mosaic.select('ndvi_qmo')
    
    Note:
        - Quality mosaic is particularly useful for crop type classification
        - Percentiles help capture phenological stages (planting, peak growth, harvest)
        - EVI2 is preferred over NDVI for agriculture due to better saturation properties
    """
    # Extract all band names from the first image
    bands = ee.Image(collection.first()).bandNames()
    
    # Calculate specified percentiles for all bands
    # Creates bands like: ndvi_p20, ndvi_p75
    mosaicPercentil = collection\
        .reduce(ee.Reducer.percentile(percentiles))

    # Calculate median mosaic (typical/average conditions)
    mosaicMedian = collection\
        .reduce(ee.Reducer.median())

    # Calculate minimum mosaic (lowest observed values)
    mosaicMin = collection\
        .reduce(ee.Reducer.min())

    # Calculate maximum mosaic (highest observed values)
    mosaicMax = collection\
        .reduce(ee.Reducer.max())

    # Calculate standard deviation mosaic (temporal variability)
    # High stdDev often indicates agricultural areas with distinct growing seasons
    mosaicStdDev = collection\
        .reduce(ee.Reducer.stdDev())

    # Generate quality mosaic: selects pixels with highest quality band values
    # For each pixel location, chooses all bands from the image that had the
    # highest value in the qualityBand (typically EVI2 at peak greenness)
    mosaicQmo = collection\
        .qualityMosaic(qualityBand)
    
    # Create quality mosaic band name suffixes
    # Example: 'ndvi' becomes 'ndvi_qmo'
    bandsQmo = bands.map(lambda band:
                      ee.String(band).cat('_qmo')
                      )
    
    # Rename quality mosaic bands with '_qmo' suffix
    mosaicQmo = mosaicQmo.rename(bandsQmo)

    # Combine all mosaic statistics into a single multi-band image
    mosaic = mosaicMedian\
        .addBands(mosaicPercentil)\
        .addBands(mosaicMin)\
        .addBands(mosaicMax)\
        .addBands(mosaicStdDev)\
        .addBands(mosaicQmo)

    return mosaic


def getMosaicUrban(
        collection,
        percentiles=[1, 99],
        percentilesSlice=[25, 75],
        sliceBand='ndvi'):
    """
    Generate an urban area-optimized mosaic with extreme value analysis.
    
    This function creates mosaics designed for urban and built-up area mapping.
    It uses extreme percentiles (1st and 99th) to capture the full range of
    conditions, which is important for detecting urban features that may have
    very low (asphalt, concrete) or very high (urban vegetation) reflectance values.
    
    The slice percentiles create two separate median composites representing
    low-vegetation (urban/built-up) and high-vegetation (parks, trees) conditions.
    
    Args:
        collection (ee.ImageCollection): Input image collection with all bands
        percentiles (list, optional): Extreme percentile values (default: [1, 99])
            Used to capture minimum and maximum conditions. Typical: [1, 99] or [5, 95]
        percentilesSlice (list, optional): Percentiles for low/high slicing (default: [25, 75])
            Lower percentile identifies urban areas, higher identifies vegetation
        sliceBand (str, optional): Band used for slicing collection (default: 'ndvi')
            'ndvi' separates vegetation from non-vegetation effectively
    
    Returns:
        ee.Image: Multi-band mosaic containing:
            - *_median: Overall median value for each band
            - *_p{percentiles[0]}: Lower extreme percentile (near minimum)
            - *_p{percentiles[1]}: Upper extreme percentile (near maximum)
            - *_median_p{percentilesSlice[0]}: Median of low-vegetation pixels
            - *_median_p{percentilesSlice[1]}: Median of high-vegetation pixels
            - *_min: Absolute minimum value for each band
            - *_max: Absolute maximum value for each band
    
    Example:
        >>> collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \\
        ...     .filterBounds(city) \\
        ...     .filterDate('2020-01-01', '2020-12-31')
        >>> mosaic = getMosaicUrban(collection,
        ...                         percentiles=[1, 99],
        ...                         percentilesSlice=[25, 75],
        ...                         sliceBand='ndvi')
        >>> # Low NDVI percentile captures urban/built-up areas
        >>> urban_composite = mosaic.select('red_median_p25')
        >>> # High NDVI percentile captures urban vegetation
        >>> vegetation_composite = mosaic.select('nir_median_p75')
    
    Note:
        - Extreme percentiles (1, 99) help avoid outliers while capturing range
        - Slice composites are useful for separating built-up from vegetated urban areas
        - This approach works well for impervious surface mapping
        - The median of low-NDVI pixels often represents typical urban surface reflectance
    """
    # Extract all band names from the first image
    bands = ee.Image(collection.first()).bandNames()
    
    # Create band name suffixes for low-vegetation slice
    # Example: 'red' becomes 'red_median_p25' (if percentilesSlice[0]=25)
    bandsSlice1 = bands.map(lambda band:
                            ee.String(band).cat(
                                '_median_p{}'.format(percentilesSlice[0]))
                            )

    # Create band name suffixes for high-vegetation slice
    # Example: 'nir' becomes 'nir_median_p75' (if percentilesSlice[1]=75)
    bandsSlice2 = bands.map(lambda band:
                            ee.String(band).cat(
                                '_median_p{}'.format(percentilesSlice[1]))
                         )

    # Calculate extreme percentiles (near minimum and maximum)
    # Captures the full range of urban surface types
    mosaicPercentil = collection\
        .reduce(ee.Reducer.percentile(percentiles))

    # Calculate slice percentile thresholds on the slice band (typically NDVI)
    # Creates two threshold images: one for low vegetation, one for high vegetation
    percentilSlice = collection\
        .select([sliceBand])\
        .reduce(ee.Reducer.percentile(percentilesSlice))

    # ========================================================================
    # LOW-VEGETATION SLICE (Urban/Built-up areas)
    # ========================================================================
    
    # Create collection of images with low slice band values
    # Masks images to keep only pixels where sliceBand ≤ lower percentile threshold
    # This typically captures urban/built-up areas with low NDVI
    collectionPercentilSlice1 = collection.map(
        lambda image:
            image.mask(image.select([sliceBand]).lte(
                percentilSlice.select([0])))  # Select first percentile threshold
    )

    # ========================================================================
    # HIGH-VEGETATION SLICE (Urban parks/trees)
    # ========================================================================
    
    # Create collection of images with high slice band values
    # Masks images to keep only pixels where sliceBand ≥ upper percentile threshold
    # This typically captures vegetated urban areas (parks, street trees)
    collectionPercentilSlice2 = collection.map(
        lambda image:
            image.mask(image.select([sliceBand]).gte(
                percentilSlice.select([1])))  # Select second percentile threshold
    )

    # Calculate median of low-vegetation pixels
    # Represents typical reflectance of urban surfaces (roads, buildings, etc.)
    mosaicPercentilSlice1 = collectionPercentilSlice1\
        .reduce(ee.Reducer.median())\
        .rename(bandsSlice1)

    # Calculate median of high-vegetation pixels
    # Represents typical reflectance of urban vegetation
    mosaicPercentilSlice2 = collectionPercentilSlice2\
        .reduce(ee.Reducer.median())\
        .rename(bandsSlice2)

    # ========================================================================
    # STANDARD STATISTICS
    # ========================================================================
    
    # Overall median mosaic (all conditions)
    mosaicMedian = collection\
        .reduce(ee.Reducer.median())

    # Minimum value mosaic (darkest/lowest reflectance observed)
    mosaicMin = collection\
        .reduce(ee.Reducer.min())

    # Maximum value mosaic (brightest/highest reflectance observed)
    mosaicMax = collection\
        .reduce(ee.Reducer.max())

    # ========================================================================
    # COMBINE ALL BANDS INTO FINAL MOSAIC
    # ========================================================================
    
    mosaic = mosaicMedian\
        .addBands(mosaicPercentil)\
        .addBands(mosaicPercentilSlice1)\
        .addBands(mosaicPercentilSlice2)\
        .addBands(mosaicMin)\
        .addBands(mosaicMax)

    return mosaic
