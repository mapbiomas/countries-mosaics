#!/usr/bin/env python

"""
Google Earth Engine Cloud and Shadow Masking Module
====================================================

This module provides comprehensive cloud and cloud shadow detection algorithms
for satellite imagery (Landsat and Sentinel-2). It implements multiple masking
approaches that can be used individually or combined for robust cloud removal.

Masking Algorithms Implemented:
1. Cloud Flag Mask: Uses QA bands from satellite products
2. Cloud Score Mask: Spectral-based cloud detection algorithm
3. Cloud Shadow Flag Mask: Uses QA bands for shadow detection
4. TDOM (Temporal Dark Outlier Mask): Statistical shadow detection
5. Cloud Shadow Projection: Geometric shadow casting from clouds

The module supports both TOA (Top-of-Atmosphere) and SR (Surface Reflectance)
products from Landsat 4-9 and Sentinel-2.

Dependencies: earthengine-api
Reference: Adapted from Google Earth Engine cloud masking examples
"""

import ee
import math

# Uncomment to initialize Earth Engine (typically done in main script)
# ee.Initialize()


def rescale(image, min=0, max=10000):
    """
    Rescale image values to 0-1 range using linear stretch.
    
    This function performs min-max normalization, converting any numeric range
    to the standard 0-1 range. It's commonly used to normalize spectral values
    for cloud detection thresholds.
    
    Formula: (value - min) / (max - min)
    
    Args:
        image (ee.Image): Input image or band to rescale
        min (float, optional): Minimum value of input range (default: 0)
        max (float, optional): Maximum value of input range (default: 10000)
    
    Returns:
        ee.Image: Rescaled image with values in 0-1 range
            Values below min become 0, values above max become 1
    
    Example:
        >>> # Rescale blue band from typical range 1000-3000 to 0-1
        >>> blue = image.select('blue')
        >>> normalized = rescale(blue, min=1000, max=3000)
        >>> # Value 1000 becomes 0.0, 2000 becomes 0.5, 3000 becomes 1.0
    
    Note:
        Used internally by cloudScoreMask to normalize spectral bands
        for cloud probability calculation
    """
    image = ee.Image(image)

    # Linear normalization formula
    image = image.subtract(min) \
        .divide(ee.Number(max).subtract(min))

    return image


def cloudScoreMask(image, cloudThresh):
    """
    Generate cloud mask using spectral-based cloud score algorithm.
    
    This algorithm detects clouds based on their spectral characteristics:
    - Clouds are bright in blue band
    - Clouds are bright in all visible bands
    - Clouds are bright in all infrared bands
    - Clouds have different NDSI than snow
    
    The algorithm combines multiple spectral tests, taking the minimum score
    at each pixel. Lower scores indicate higher cloud probability.
    
    Args:
        image (ee.Image): Input image with bands: blue, red, green, nir, swir1, swir2
        cloudThresh (int): Cloud score threshold (0-100)
            Lower values = more aggressive cloud masking
            Typical values: 10-20
            Higher values = less aggressive (allows brighter surfaces)
    
    Returns:
        ee.Image: Original image with added 'cloudScoreMask' band
            cloudScoreMask = 1 where score >= threshold (potential cloud)
            cloudScoreMask = 0 where score < threshold (clear)
    
    Algorithm Steps:
        1. Start with perfect score (1.0)
        2. Test blue brightness (clouds bright in blue)
        3. Test visible band sum (clouds bright across visible spectrum)
        4. Test infrared sum (clouds bright in infrared)
        5. Test NDSI (clouds different from snow)
        6. Take minimum score from all tests
        7. Scale to 0-100 and threshold
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> masked = cloudScoreMask(image, cloudThresh=15)
        >>> cloud_mask = masked.select('cloudScoreMask')
    
    Note:
        - Does not use thermal band (Sentinel-2 doesn't have thermal)
        - More conservative than simple brightness threshold
        - Works well combined with QA band masks
    
    Reference:
        Based on Google Earth Engine's Simple Cloud Score algorithm
    """
    image = ee.Image(image)
    
    # Initialize score as perfect (1.0 = clear sky)
    score = ee.Image(1.0)

    # Test 1: Clouds are reasonably bright in the blue band
    # Typical clear sky: 1000, clouds: 3000+
    blue = image.select(['blue'])
    score = score.min(rescale(blue, min=1000, max=3000))

    # Test 2: Clouds are reasonably bright in all visible bands
    # Sum of red + green + blue
    visibleSum = image.expression("b('red') + b('green') + b('blue')")
    score = score.min(rescale(visibleSum, min=2000, max=8000))

    # Test 3: Clouds are reasonably bright in all infrared bands
    # Sum of NIR + SWIR1 + SWIR2
    infraredSum = image.expression("b('nir') + b('swir1') + b('swir2')")
    score = score.min(rescale(infraredSum, min=3000, max=8000))

    # Note: Thermal band test disabled because Sentinel-2 lacks thermal band
    # temperature = image.select('temp')

    # Test 4: Clouds are not snow (NDSI test)
    # Snow has high NDSI (>0.8), clouds have lower NDSI
    ndsi = image.normalizedDifference(['green', 'swir1'])
    score = score.min(rescale(ndsi, min=0.8, max=0.6))

    # Convert score to 0-100 range and apply threshold
    score = score.multiply(100).byte()
    score = score.gte(cloudThresh).rename('cloudScoreMask')

    return image.addBands(score)


def tdom(collection,
         zScoreThresh=-1,
         shadowSumThresh=5000,
         dilatePixels=2):
    """
    Apply Temporal Dark Outlier Mask (TDOM) for shadow detection.
    
    TDOM identifies shadows by finding pixels that are statistically darker
    than normal across time. It uses z-score analysis on NIR and SWIR bands
    to detect temporal anomalies that indicate shadows.
    
    The algorithm works by:
    1. Computing mean and standard deviation of NIR+SWIR across time
    2. Calculating z-scores for each image
    3. Flagging pixels with very low z-scores (darker than expected)
    4. Requiring both NIR and SWIR to be dark (reduces false positives)
    
    Args:
        collection (ee.ImageCollection): Input image collection
        zScoreThresh (float, optional): Z-score threshold for shadow detection (default: -1)
            Negative values flag dark outliers. Typical range: -0.5 to -2.0
            More negative = more conservative (only very dark shadows)
            Less negative = more aggressive (includes lighter shadows)
        shadowSumThresh (int, optional): Sum threshold for NIR+SWIR (default: 5000)
            Pixels with NIR+SWIR sum below this are potential shadows
            Lower values = more aggressive shadow detection
        dilatePixels (int, optional): Pixels to dilate shadow mask (default: 2)
            Erosion/buffer applied to shadow mask for cleaner edges
    
    Returns:
        ee.ImageCollection: Collection with added 'tdomMask' band to each image
            tdomMask = 1 where shadow detected
            tdomMask = 0 where clear
    
    Algorithm Details:
        Z-score = (value - mean) / stdDev
        Shadow criteria:
            - Z-score < threshold for BOTH NIR and SWIR
            - NIR + SWIR sum < shadowSumThresh
            - Morphological cleaning (focal_min)
    
    Example:
        >>> collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')...
        >>> masked_collection = tdom(collection, 
        ...                          zScoreThresh=-1.0,
        ...                          shadowSumThresh=5000)
        >>> # Each image now has 'tdomMask' band
    
    Note:
        - Requires multiple images (temporal collection) to compute statistics
        - Works best with 5+ images
        - More effective than single-image shadow detection
        - Complements geometric shadow projection methods
    
    Reference:
        Temporal Dark Outlier Mask (TDOM) algorithm for cloud shadow detection
    """
    # Bands used for shadow detection (infrared bands sensitive to shadows)
    shadowSumBands = ['nir', 'swir1']

    # Compute standard deviation of infrared bands across time
    irStdDev = collection \
        .select(shadowSumBands) \
        .reduce(ee.Reducer.stdDev())

    # Compute mean of infrared bands across time
    irMean = collection \
        .select(shadowSumBands) \
        .mean()

    def _maskDarkOutliers(image):
        """
        Internal function to identify dark outliers in a single image.
        """
        # Calculate z-score: (value - mean) / stdDev
        # Negative z-scores indicate darker than average
        zScore = image.select(shadowSumBands) \
            .subtract(irMean) \
            .divide(irStdDev)

        # Calculate sum of infrared bands
        irSum = image.select(shadowSumBands) \
            .reduce(ee.Reducer.sum())

        # Shadow criteria:
        # 1. Z-score < threshold for both NIR and SWIR (both bands dark)
        # 2. Sum of infrared bands < threshold (absolute darkness test)
        tdomMask = zScore.lt(zScoreThresh) \
            .reduce(ee.Reducer.sum()) \
            .eq(2) \
            .And(irSum.lt(shadowSumThresh))

        # Apply morphological erosion to clean up mask edges
        tdomMask = tdomMask.focal_min(dilatePixels)

        return image.addBands(tdomMask.rename('tdomMask'))

    # Apply shadow detection to each image in collection
    collection = collection.map(_maskDarkOutliers)

    return collection


def cloudProject(image,
                 cloudBand=None,
                 shadowSumThresh=5000,
                 cloudHeights=[],
                 dilatePixels=2):
    """
    Project cloud shadows geometrically based on solar geometry and cloud height.
    
    This algorithm casts shadows from detected clouds using:
    - Solar azimuth angle (sun direction)
    - Solar elevation angle (sun height)
    - Assumed cloud heights
    
    For each cloud pixel, it calculates where the shadow should fall based on
    sun position and projects the cloud mask to that location.
    
    Args:
        image (ee.Image): Input image with cloud mask and TDOM mask
        cloudBand (str): Name of band containing cloud mask
        shadowSumThresh (int, optional): Threshold for dark pixels (default: 5000)
            Sum of NIR+SWIR1+SWIR2 below this indicates potential shadow
        cloudHeights (list): List of cloud heights in meters
            Example: [200, 500, 1000, 2000, 5000]
            Multiple heights help capture shadows from clouds at various altitudes
        dilatePixels (int, optional): Pixels to dilate shadow mask (default: 2)
            Buffer applied to projected shadow for better coverage
    
    Returns:
        ee.Image: Original image with added 'cloudShadowTdomMask' band
            cloudShadowTdomMask = 1 where projected shadow detected
            cloudShadowTdomMask = 0 where clear
    
    Algorithm Steps:
        1. Get cloud mask and TDOM mask from image
        2. Identify dark pixels (potential shadow locations)
        3. Extract solar geometry from image metadata
        4. For each cloud height:
           a. Calculate shadow distance using trigonometry
           b. Calculate x,y offset based on azimuth
           c. Shift cloud mask to shadow location
        5. Combine all shadow projections (maximum)
        6. Refine using dark pixel mask and TDOM
    
    Geometry Calculations:
        Shadow distance = tan(zenith) × cloud_height
        x_offset = cos(azimuth) × distance
        y_offset = sin(azimuth) × distance
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> # Image must have 'cloudFlagMask' and 'tdomMask' bands
        >>> shadowed = cloudProject(image,
        ...                         cloudBand='cloudFlagMask',
        ...                         cloudHeights=[200, 500, 1000, 2000],
        ...                         shadowSumThresh=5000)
    
    Note:
        - Requires image metadata: sun_azimuth_angle, sun_elevation_angle
        - Multiple cloud heights account for uncertainty in cloud altitude
        - Works best when combined with TDOM for validation
        - Geometric projection more accurate than spectral-only methods
    
    Reference:
        Cloud shadow projection using solar geometry
    """
    # Get cloud mask band (detected clouds)
    cloud = image.select([cloudBand])

    # Get TDOM mask (temporal dark outlier mask)
    tdomMask = image.select(['tdomMask'])

    # Identify dark pixels (potential shadow locations)
    # Sum of NIR + SWIR1 + SWIR2 < threshold
    darkPixels = image.select(['nir', 'swir1', 'swir2']) \
        .reduce(ee.Reducer.sum()) \
        .lt(shadowSumThresh)

    # Get pixel size for projection calculations
    nominalScale = cloud.projection().nominalScale()

    # Extract solar geometry from image metadata
    meanAzimuth = image.get('sun_azimuth_angle')
    meanElevation = image.get('sun_elevation_angle')

    # Convert azimuth to radians and adjust for coordinate system
    # Add π/2 to convert from north-clockwise to east-counterclockwise
    azR = ee.Number(meanAzimuth) \
        .multiply(math.pi) \
        .divide(180.0) \
        .add(ee.Number(0.5).multiply(math.pi))

    # Convert elevation to zenith angle in radians
    # Zenith = 90° - elevation
    zenR = ee.Number(0.5) \
        .multiply(math.pi) \
        .subtract(ee.Number(meanElevation).multiply(math.pi).divide(180.0))

    def _findShadow(cloudHeight):
        """
        Internal function to project shadow for a specific cloud height.
        
        Args:
            cloudHeight (float): Cloud height in meters
        
        Returns:
            ee.Image: Projected cloud mask at shadow location
        """
        cloudHeight = ee.Number(cloudHeight)

        # Calculate shadow distance using trigonometry
        # distance = tan(zenith) × height
        shadowCastedDistance = zenR.tan() \
            .multiply(cloudHeight)

        # Calculate x offset (east-west) in pixels
        # x = cos(azimuth) × distance / pixel_size
        x = azR.cos().multiply(shadowCastedDistance) \
            .divide(nominalScale).round()

        # Calculate y offset (north-south) in pixels
        # y = sin(azimuth) × distance / pixel_size
        y = azR.sin().multiply(shadowCastedDistance) \
            .divide(nominalScale).round()

        # Shift cloud mask by calculated offset
        return cloud.changeProj(cloud.projection(), 
                               cloud.projection().translate(x, y))

    # Project shadows for all specified cloud heights
    shadows = ee.List(cloudHeights).map(_findShadow)

    # Combine all shadow projections (take maximum to include all)
    shadow = ee.ImageCollection.fromImages(shadows).max().unmask()
    
    # Dilate shadow mask to ensure coverage
    shadow = shadow.focal_max(dilatePixels)
    
    # Refine shadow mask using additional criteria:
    # 1. Must be dark pixel (darkPixels)
    # 2. Must not be TDOM anomaly (not shadow from TDOM perspective)
    # 3. Must not be cloud itself
    shadow = shadow.And(darkPixels).And(tdomMask.Not().And(cloud.Not()))

    shadowMask = shadow.rename(['cloudShadowTdomMask'])

    return image.addBands(shadowMask)


def cloudFlagMaskToaLX(image):
    """
    Extract cloud mask from Landsat TOA QA band.
    
    Reads bit 3 from the pixel_qa band which indicates cloud presence
    in Landsat Top-of-Atmosphere products.
    
    Args:
        image (ee.Image): Landsat TOA image with 'pixel_qa' band
    
    Returns:
        ee.Image: Cloud mask (1 = cloud, 0 = clear)
    
    QA Bit Mapping:
        Bit 3: Cloud (1 = yes, 0 = no)
    """
    qaBand = ee.Image(image.select(['pixel_qa']))

    # Extract bit 3 using bitwise AND with 2^3 = 8
    cloudMask = qaBand.bitwiseAnd(int(math.pow(2, 3))) \
        .rename('cloudFlagMask')

    return ee.Image(cloudMask)


def cloudFlagMaskToaS2(image):
    """
    Extract cloud mask from Sentinel-2 TOA QA band.
    
    Reads bits 10 and 11 from the pixel_qa band which indicate cloud presence
    in Sentinel-2 Top-of-Atmosphere products.
    
    Args:
        image (ee.Image): Sentinel-2 TOA image with 'pixel_qa' band
    
    Returns:
        ee.Image: Cloud mask (1 = cloud, 0 = clear)
    
    QA Bit Mapping:
        Bit 10: Thin cirrus (1 = yes, 0 = no)
        Bit 11: Cloud (1 = yes, 0 = no)
    """
    qaBand = ee.Image(image.select(['pixel_qa']))

    # Extract bits 10 and 11 using bitwise operations
    # Cloud present if either bit is set
    cloudMask = qaBand.bitwiseAnd(int(math.pow(2, 10))).neq(0) \
        .Or(qaBand.bitwiseAnd(int(math.pow(2, 11))).neq(0)) \
        .rename('cloudFlagMask')

    return ee.Image(cloudMask)


def cloudFlagMaskToa(image):
    """
    Extract cloud mask from TOA products (Landsat or Sentinel-2).
    
    Automatically detects satellite type and applies appropriate QA bit extraction.
    
    Args:
        image (ee.Image): TOA image with 'satellite_name' property and 'pixel_qa' band
    
    Returns:
        ee.Image: Cloud mask (1 = cloud, 0 = clear)
    """
    # Detect if Sentinel-2 by checking satellite name
    isSentinel = ee.String(image.get('satellite_name')) \
        .slice(0, 10).compareTo('Sentinel-2').Not()

    # Apply appropriate mask function based on satellite
    cloudMask = ee.Algorithms.If(
        isSentinel,
        cloudFlagMaskToaS2(image),
        cloudFlagMaskToaLX(image))

    return ee.Image(cloudMask)


def cloudFlagMaskSr(image):
    """
    Extract cloud mask from Surface Reflectance QA band.
    
    Reads bit 3 from the pixel_qa band which indicates cloud presence
    in Surface Reflectance products (both Landsat and Sentinel-2).
    
    Args:
        image (ee.Image): SR image with 'pixel_qa' band
    
    Returns:
        ee.Image: Cloud mask (1 = cloud, 0 = clear)
    
    QA Bit Mapping:
        Bit 3: Cloud (1 = yes, 0 = no)
    """
    qaBand = ee.Image(image.select(['pixel_qa']))

    # Extract bit 3 using bitwise AND with 2^3 = 8
    cloudMask = qaBand.bitwiseAnd(int(math.pow(2, 3))) \
        .neq(0) \
        .rename('cloudFlagMask')

    return ee.Image(cloudMask)


def cloudFlagMask(image):
    """
    Extract cloud mask from QA band (TOA or SR products).
    
    Automatically detects product type (TOA vs SR) and applies appropriate
    QA bit extraction method.
    
    Args:
        image (ee.Image): Image with 'reflectance' property and 'pixel_qa' band
    
    Returns:
        ee.Image: Original image with added 'cloudFlagMask' band
            cloudFlagMask = 1 where cloud detected
            cloudFlagMask = 0 where clear
    """
    image = ee.Image(image)

    # Detect if TOA product by checking reflectance property
    isToa = ee.String(image.get('reflectance')).compareTo('TOA').Not()

    # Apply appropriate mask function based on product type
    cloudMask = ee.Algorithms.If(
        isToa,
        cloudFlagMaskToa(image),
        cloudFlagMaskSr(image))

    return image.addBands(ee.Image(cloudMask))


def cloudShadowFlagMaskToaLX(image):
    """
    Extract cloud shadow mask from Landsat TOA QA band.
    
    Reads bit 4 from the pixel_qa band which indicates cloud shadow presence
    in Landsat Top-of-Atmosphere products.
    
    Args:
        image (ee.Image): Landsat TOA image with 'pixel_qa' band
    
    Returns:
        ee.Image: Shadow mask (1 = shadow, 0 = clear)
    
    QA Bit Mapping:
        Bit 4: Cloud shadow (1 = yes, 0 = no)
    """
    qaBand = ee.Image(image.select(['pixel_qa']))

    # Extract bit 4 using bitwise AND with 2^4 = 16
    cloudShadowMask = qaBand.bitwiseAnd(int(math.pow(2, 4))).neq(0)\
        .rename('cloudShadowFlagMask')

    return ee.Image(cloudShadowMask)


def cloudShadowFlagMaskSrLX(image):
    """
    Extract cloud shadow mask from Landsat SR QA band.
    
    Reads bit 4 from the pixel_qa band which indicates cloud shadow presence
    in Landsat Surface Reflectance products.
    
    Args:
        image (ee.Image): Landsat SR image with 'pixel_qa' band
    
    Returns:
        ee.Image: Shadow mask (1 = shadow, 0 = clear)
    
    QA Bit Mapping:
        Bit 4: Cloud shadow (1 = yes, 0 = no)
    """
    qaBand = ee.Image(image.select(['pixel_qa']))

    # Extract bit 4 using bitwise AND with 2^4 = 16
    cloudShadowMask = qaBand.bitwiseAnd(int(math.pow(2, 4))) \
        .neq(0) \
        .rename('cloudShadowFlagMask')

    return ee.Image(cloudShadowMask)


def cloudShadowFlagMask(image):
    """
    Extract cloud shadow mask from QA band (works for TOA/SR and Landsat/Sentinel-2).
    
    Automatically detects satellite type and product type to apply appropriate
    QA bit extraction. Note: Sentinel-2 QA bands do not contain shadow information,
    so a dummy mask is returned for Sentinel-2 images.
    
    Args:
        image (ee.Image): Image with 'satellite_name' and 'reflectance' properties
    
    Returns:
        ee.Image: Original image with added 'cloudShadowFlagMask' band
            cloudShadowFlagMask = 1 where shadow detected
            cloudShadowFlagMask = 0 where clear
            For Sentinel-2: returns 0 everywhere (no QA shadow info)
    """
    # Detect if Sentinel-2
    isSentinel = ee.String(image.get('satellite_name')) \
        .slice(0, 10).compareTo('Sentinel-2').Not()

    # Detect if TOA product
    isToa = ee.String(image.get('reflectance')).compareTo('TOA').Not()

    # Apply appropriate mask based on satellite and product type
    cloudShadowMask = ee.Algorithms.If(
        isSentinel,
        # Sentinel-2 QA doesn't have shadow flags, return dummy mask
        ee.Image(0).mask(image.select(0)).rename('cloudShadowFlagMask'),
        ee.Algorithms.If(
            isToa,
            cloudShadowFlagMaskToaLX(image),
            cloudShadowFlagMaskSrLX(image)))

    return image.addBands(ee.Image(cloudShadowMask))


def getMasks(collection,
             cloudThresh=10,
             zScoreThresh=-1,
             shadowSumThresh=5000,
             dilatePixels=2,
             cloudFlag=True,
             cloudScore=True,
             cloudShadowFlag=True,
             cloudShadowTdom=True,
             cloudHeights=[],
             cloudBand=None):
    """
    Generate comprehensive cloud and shadow masks for image collection.
    
    This is the main function that orchestrates multiple cloud and shadow detection
    algorithms. It can apply various masking methods individually or in combination
    to create robust cloud/shadow masks.
    
    The function supports four independent masking approaches:
    1. Cloud Flag Mask: QA band-based cloud detection
    2. Cloud Score Mask: Spectral-based cloud detection
    3. Cloud Shadow Flag Mask: QA band-based shadow detection
    4. Cloud Shadow TDOM: Temporal and geometric shadow detection
    
    Args:
        collection (ee.ImageCollection): Input image collection with required bands:
            - Spectral: blue, green, red, nir, swir1, swir2
            - QA: pixel_qa (if using flag masks)
            - Metadata: sun_azimuth_angle, sun_elevation_angle (for projection)
        
        cloudThresh (int, optional): Cloud score threshold 0-100 (default: 10)
            Lower = more aggressive cloud removal
            Higher = less aggressive
            Only used if cloudScore=True
        
        zScoreThresh (float, optional): Z-score threshold for TDOM (default: -1)
            More negative = more conservative shadow detection
            Only used if cloudShadowTdom=True
        
        shadowSumThresh (int, optional): Darkness threshold for shadows (default: 5000)
            Lower = more aggressive shadow detection
            Sum of infrared bands below this indicates potential shadow
        
        dilatePixels (int, optional): Buffer size for cloud/shadow masks (default: 2)
            Number of pixels to dilate masks
            Larger values = more conservative (more masking)
        
        cloudFlag (bool, optional): Enable QA-based cloud masking (default: True)
            Uses pixel_qa band cloud flags
        
        cloudScore (bool, optional): Enable spectral cloud detection (default: True)
            Uses brightness-based algorithm
        
        cloudShadowFlag (bool, optional): Enable QA-based shadow masking (default: True)
            Uses pixel_qa band shadow flags
        
        cloudShadowTdom (bool, optional): Enable TDOM shadow detection (default: True)
            Uses temporal statistics and geometric projection
        
        cloudHeights (list, optional): Cloud heights in meters (default: [])
            Example: [200, 500, 1000, 2000, 5000]
            Only used if cloudShadowTdom=True
            Multiple heights improve shadow detection accuracy
        
        cloudBand (str, optional): Name of cloud mask band for projection (default: None)
            Typically 'cloudFlagMask' or 'cloudScoreMask'
            Only used if cloudShadowTdom=True
    
    Returns:
        ee.ImageCollection: Collection with added mask bands to each image:
            - cloudFlagMask: QA-based cloud mask (if cloudFlag=True)
            - cloudScoreMask: Spectral cloud mask (if cloudScore=True)
            - cloudShadowFlagMask: QA-based shadow mask (if cloudShadowFlag=True)
            - tdomMask: Temporal dark outlier mask (if cloudShadowTdom=True)
            - cloudShadowTdomMask: Geometric shadow projection (if cloudShadowTdom=True)
    
    Usage Examples:
        Example 1 - All masks enabled (default):
            >>> collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')...
            >>> masked = getMasks(collection,
            ...                   cloudThresh=10,
            ...                   cloudHeights=[200, 700, 1200, 2000],
            ...                   cloudBand='cloudFlagMask')
        
        Example 2 - Only QA-based masks:
            >>> masked = getMasks(collection,
            ...                   cloudFlag=True,
            ...                   cloudScore=False,
            ...                   cloudShadowFlag=True,
            ...                   cloudShadowTdom=False)
        
        Example 3 - Only spectral and TDOM:
            >>> masked = getMasks(collection,
            ...                   cloudFlag=False,
            ...                   cloudScore=True,
            ...                   cloudShadowFlag=False,
            ...                   cloudShadowTdom=True,
            ...                   cloudHeights=[500, 1000, 2000])
    
    Processing Workflow:
        1. Apply cloud detection (Flag and/or Score)
        2. Apply shadow detection (Flag and/or TDOM)
        3. If TDOM enabled, apply geometric shadow projection
        4. Return collection with all mask bands attached
    
    Notes:
        - Combining multiple methods improves accuracy
        - QA masks are fast but may miss some clouds
        - Spectral methods catch more clouds but have false positives
        - TDOM requires temporal collection (5+ images recommended)
        - Geometric projection requires accurate solar geometry metadata
        - All mask bands are added to images (not applied yet)
        - Use .mask() or .updateMask() to actually apply masks
    
    Best Practices:
        - Use cloudFlag + cloudScore for robust cloud detection
        - Use cloudShadowTdom for best shadow detection
        - Set cloudBand='cloudFlagMask' when using TDOM
        - Include multiple cloudHeights (200-5000m range)
        - Adjust thresholds based on study area and season
    
    Reference:
        Based on MapBiomas cloud masking methodology combining multiple algorithms
    """

    # Apply cloud detection algorithms based on flags
    collection = ee.Algorithms.If(
        cloudFlag,
        ee.Algorithms.If(
            cloudScore,
            collection.map(cloudFlagMask).map(
                lambda collection: cloudScoreMask(collection, cloudThresh)
            ),
            collection.map(cloudFlagMask)),
        collection.map(
            lambda collection: cloudScoreMask(collection, cloudThresh)
        )
    )

    collection = ee.ImageCollection(collection)

    collection = ee.Algorithms.If(
        cloudShadowFlag,
        ee.Algorithms.If(
            cloudShadowTdom,
            tdom(collection.map(cloudShadowFlagMask),
                 zScoreThresh=zScoreThresh,
                 shadowSumThresh=shadowSumThresh,
                 dilatePixels=dilatePixels),
            collection.map(cloudShadowFlagMask)),
        tdom(collection,
             zScoreThresh=zScoreThresh,
             shadowSumThresh=shadowSumThresh,
             dilatePixels=dilatePixels))

    collection = ee.ImageCollection(collection)

    def _getShadowMask(image):

        image = cloudProject(image,
                             shadowSumThresh=shadowSumThresh,
                             dilatePixels=dilatePixels,
                             cloudHeights=cloudHeights,
                             cloudBand=cloudBand)

        return image

    if cloudShadowTdom:
        collection = collection.map(_getShadowMask)

    return collection
