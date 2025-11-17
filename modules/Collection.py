#!/usr/bin/env python

"""
Google Earth Engine Image Collection Management Module
=======================================================

This module provides utilities for creating and preprocessing satellite image
collections in Google Earth Engine, with a focus on Landsat and Sentinel-2 data.
It handles metadata normalization, scale factor application, and collection filtering.

Key Features:
- Normalizes metadata properties across Landsat and Sentinel-2 satellites
- Applies correct scale factors for Landsat Collection 2 (Surface Reflectance and TOA)
- Provides flexible collection filtering (date, cloud cover, geometry, blacklist)
- Standardizes property names for cross-sensor compatibility

Dependencies: earthengine-api
"""

# Import earthengine API
import ee
from datetime import date

# Initialize Earth Engine (uncomment if running standalone)
# ee.Initialize()


def setProperties(image):
    """
    Normalize metadata properties across Landsat and Sentinel-2 satellites.
    
    This function standardizes property names that vary between satellite platforms,
    making it easier to work with mixed collections. It handles different naming
    conventions for cloud cover, acquisition date, satellite identifier, and solar
    geometry parameters.
    
    The function uses conditional logic (ee.Algorithms.If) to check for the existence
    of properties and select the appropriate one based on the satellite type.
    
    Args:
        image (ee.Image): Input satellite image with original metadata properties
    
    Returns:
        ee.Image: Image with standardized properties:
            - cloud_cover: Cloud coverage percentage (0-100)
            - satellite_name: Satellite identifier (e.g., 'LANDSAT_8', 'Sentinel-2A')
            - sun_azimuth_angle: Solar azimuth angle in degrees (0-360)
            - sun_elevation_angle: Solar elevation angle in degrees (0-90)
            - date: Acquisition date in 'YYYY-MM-DD' format
    
    Property Mapping:
        Cloud Cover:
            - Landsat: 'CLOUD_COVER'
            - Sentinel-2: 'CLOUDY_PIXEL_PERCENTAGE'
        
        Date:
            - Landsat: 'DATE_ACQUIRED'
            - Sentinel-2: 'SENSING_TIME' or 'GENERATION_TIME'
        
        Satellite:
            - Landsat: 'SPACECRAFT_ID' or 'SATELLITE'
            - Sentinel-2: 'SPACECRAFT_NAME'
        
        Solar Azimuth:
            - Landsat: 'SUN_AZIMUTH'
            - Sentinel-2: 'SOLAR_AZIMUTH_ANGLE' or 'MEAN_SOLAR_AZIMUTH_ANGLE'
        
        Solar Elevation:
            - Landsat: 'SUN_ELEVATION'
            - Sentinel-2: 90 - 'SOLAR_ZENITH_ANGLE' or 90 - 'MEAN_SOLAR_ZENITH_ANGLE'
    
    Note:
        - Solar elevation is calculated from zenith angle for Sentinel-2: elevation = 90° - zenith
        - The function prioritizes Landsat property names first, then falls back to Sentinel-2
        - Original properties are preserved; new standardized properties are added
    
    Example:
        >>> landsat_image = ee.Image('LANDSAT/LC08/C02/T1_L2/LC08_226080_20200101')
        >>> normalized = setProperties(landsat_image)
        >>> cloud_pct = normalized.get('cloud_cover')  # Works for both Landsat and Sentinel-2
    """
    # Determine cloud cover property (Sentinel-2 uses different property name)
    cloudCover = ee.Algorithms.If(image.get('SPACECRAFT_NAME'),  # If Sentinel-2
                                  image.get('CLOUDY_PIXEL_PERCENTAGE'),
                                  image.get('CLOUD_COVER'))  # Else Landsat

    # Determine acquisition date property (varies by satellite and product)
    date = ee.Algorithms.If(image.get('DATE_ACQUIRED'),  # Landsat format
                            image.get('DATE_ACQUIRED'),
                            ee.Algorithms.If(image.get('SENSING_TIME'),  # Sentinel-2 format
                                             image.get('SENSING_TIME'),
                                             image.get('GENERATION_TIME')))  # Alternative format

    # Determine satellite identifier property
    satellite = ee.Algorithms.If(image.get('SPACECRAFT_ID'),  # Landsat (e.g., 'LANDSAT_8')
                                 image.get('SPACECRAFT_ID'),
                                 ee.Algorithms.If(image.get('SATELLITE'),  # Alternative Landsat
                                                  image.get('SATELLITE'),
                                                  image.get('SPACECRAFT_NAME')))  # Sentinel-2

    # Determine solar azimuth angle property (sun position in horizontal plane)
    azimuth = ee.Algorithms.If(image.get('SUN_AZIMUTH'),  # Landsat
                               image.get('SUN_AZIMUTH'),
                               ee.Algorithms.If(image.get('SOLAR_AZIMUTH_ANGLE'),  # Sentinel-2
                                                image.get('SOLAR_AZIMUTH_ANGLE'),
                                                image.get('MEAN_SOLAR_AZIMUTH_ANGLE')))  # Alternative

    # Determine solar elevation angle property (sun height above horizon)
    # Sentinel-2 provides zenith angle (angle from vertical), so convert: elevation = 90° - zenith
    elevation = ee.Algorithms.If(image.get('SUN_ELEVATION'),  # Landsat (direct)
                                 image.get('SUN_ELEVATION'),
                                 ee.Algorithms.If(image.get('SOLAR_ZENITH_ANGLE'),  # Sentinel-2
                                                  ee.Number(90).subtract(
                                                      image.get('SOLAR_ZENITH_ANGLE')),
                                                  ee.Number(90).subtract(image.get('MEAN_SOLAR_ZENITH_ANGLE'))))

    # Add standardized properties to the image
    return image \
        .set('cloud_cover', cloudCover) \
        .set('satellite_name', satellite) \
        .set('sun_azimuth_angle', azimuth) \
        .set('sun_elevation_angle', elevation) \
        .set('date', ee.Date(date).format('Y-MM-dd'))


def applyScaleFactors(image):
    """
    Apply Landsat Collection 2 Surface Reflectance scale factors.
    
    Landsat Collection 2 Level-2 products store surface reflectance as scaled integers
    to reduce file size. This function converts them to actual reflectance values and
    then rescales to a 0-10000 integer range for consistency with processing pipelines.
    
    Scale Factor Application:
        Optical Bands (SR_B*):
            - Original values: Integer (typically 7273-43636)
            - Formula: (DN × 0.0000275) + (-0.2)
            - Result: Reflectance (typically -0.2 to 1.0)
            - Final: × 10000 for integer storage (0-10000 range)
        
        Thermal Bands (ST_B*):
            - Original values: Integer
            - Formula: (DN × 0.00341802) + 149.0
            - Result: Temperature in Kelvin
            - Final: × 10 for integer storage
    
    Args:
        image (ee.Image): Landsat Collection 2 Level-2 image with scaled bands
    
    Returns:
        ee.Image: Image with scale factors applied, reflectance in 0-10000 range
    
    Bands Affected:
        - Optical: All SR_B.* bands (Blue, Green, Red, NIR, SWIR1, SWIR2)
        - Thermal: All ST_B.* bands (Thermal infrared)
    
    Note:
        - The final multiplication by 10000 converts reflectance (0-1) to integers (0-10000)
        - This 10000 scaling is standard in MapBiomas workflows for efficient storage
        - Original bands are replaced (overwrite=True)
        - All image properties are preserved
    
    Reference:
        - Landsat Collection 2 Level-2 Science Product Guide
        - https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/LC08_226080_20200101')
        >>> scaled = applyScaleFactors(image)
        >>> # Blue band now has reflectance × 10000 (e.g., 500 = 0.05 reflectance)
    """
    # Apply scale factors to optical/multispectral bands
    # SR_B.* matches all surface reflectance bands (SR_B1, SR_B2, etc.)
    opticalBands = image.select('SR_B.')\
        .multiply(0.0000275)\
        .add(-0.2)\
        .multiply(10000)
    
    # Apply scale factors to thermal bands
    # ST_B.* matches all surface temperature bands
    thermalBands = image.select('ST_B.*')\
        .multiply(0.00341802)\
        .add(149.0)\
        .multiply(10)

    # Replace original bands with scaled versions
    image = image.addBands(opticalBands, None, True)  # overwrite=True
    image = image.addBands(thermalBands, None, True)
    image = ee.Image(image)

    # Note: Commented code below was for explicit property copying
    # Properties are automatically preserved by addBands
    # image = ee.Image(image.copyProperties(image))
    # image = ee.Image(image.copyProperties(image, ['system:time_start']))
    # image = ee.Image(image.copyProperties(image, ['system:index']))
    # image = ee.Image(image.copyProperties(image, ['system:footprint']))

    return image


def applyScaleFactorsTOA(image):
    """
    Apply Landsat Collection 2 Top-of-Atmosphere (TOA) scale factors.
    
    Landsat Collection 2 Level-1 TOA reflectance products store reflectance values
    that need to be scaled. This function simply multiplies by 10000 to convert
    from 0-1 range to 0-10000 integer range for consistency with processing pipelines.
    
    Scale Factor Application:
        TOA Bands (B*):
            - Original values: Float (0.0 to 1.0+)
            - Formula: DN × 10000
            - Result: Integer (0 to 10000+)
    
    Args:
        image (ee.Image): Landsat Collection 2 Level-1 TOA image
    
    Returns:
        ee.Image: Image with TOA reflectance scaled to 0-10000 range
    
    Bands Affected:
        - All B.* bands (B1, B2, B3, etc.) representing TOA reflectance
    
    Note:
        - TOA reflectance does not include atmospheric correction
        - The 10000 scaling matches the Surface Reflectance product format
        - This allows TOA and SR products to be processed with the same pipeline
        - Original bands are replaced (overwrite=True)
    
    Difference from Surface Reflectance:
        - TOA: At-satellite reflectance (includes atmospheric effects)
        - SR: Surface reflectance (atmospherically corrected)
        - TOA is useful when atmospheric correction quality is poor
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_TOA/LC08_226080_20200101')
        >>> scaled = applyScaleFactorsTOA(image)
        >>> # Reflectance now in 0-10000 range
    """
    # Apply scale factor to all optical bands
    # B.* matches all TOA reflectance bands (B1, B2, B3, etc.)
    opticalBands = image.select('B.*')\
        .multiply(10000)  # Convert 0-1 range to 0-10000 integer range

    # Replace original bands with scaled versions
    image = image.addBands(opticalBands, None, True)  # overwrite=True
    image = ee.Image(image)

    # Note: Commented code below was for explicit property copying
    # Properties are automatically preserved by addBands
    # image = ee.Image(image.copyProperties(image))
    # image = ee.Image(image.copyProperties(image, ['system:time_start']))
    # image = ee.Image(image.copyProperties(image, ['system:index']))
    # image = ee.Image(image.copyProperties(image, ['system:footprint']))

    return image


def getCollection(collectionId,
                  collectionType='SR',
                  dateStart='1970-01-01',
                  dateEnd=None,
                  cloudCover=100,
                  trashList=None,
                  geometry=None,
                  scaleFactor=True):
    """
    Create a filtered and preprocessed satellite image collection.
    
    This is the main function for retrieving satellite imagery from Google Earth Engine
    with standardized preprocessing. It handles collection filtering, metadata normalization,
    and scale factor application in a single convenient interface.
    
    The function supports both Landsat and Sentinel-2 collections and can work with
    either Surface Reflectance (SR) or Top-of-Atmosphere (TOA) products.
    
    Args:
        collectionId (str): Earth Engine collection ID
            Examples:
                - 'LANDSAT/LC08/C02/T1_L2' (Landsat 8 Surface Reflectance)
                - 'LANDSAT/LC08/C02/T1_TOA' (Landsat 8 TOA)
                - 'COPERNICUS/S2_SR' (Sentinel-2 Surface Reflectance)
        
        collectionType (str, optional): Type of reflectance product (default: 'SR')
            - 'SR': Surface Reflectance (atmospherically corrected)
            - 'TOA': Top-of-Atmosphere reflectance (not corrected)
        
        dateStart (str, optional): Start date for collection (default: '1970-01-01')
            Format: 'YYYY-MM-DD'
        
        dateEnd (str, optional): End date for collection (default: None)
            Format: 'YYYY-MM-DD'
            If None, uses today's date
        
        cloudCover (float, optional): Maximum cloud cover percentage (default: 100)
            Range: 0-100. Lower values = less cloudy images
            Examples: 20 (very clear), 50 (moderate), 80 (liberal)
        
        trashList (list, optional): List of image IDs to exclude (default: None)
            Format: ['LANDSAT/.../LC08_226080_20200101', ...]
            Useful for excluding known bad images
        
        geometry (ee.Geometry, optional): Region of interest (default: None)
            If provided, only images intersecting this geometry are returned
            Examples: ee.Geometry.Point(), ee.Geometry.Polygon(), feature.geometry()
        
        scaleFactor (bool, optional): Whether to apply scale factors (default: True)
            If True, applies appropriate scale factors based on collectionType
            Set to False if working with already-scaled data
    
    Returns:
        ee.ImageCollection: Filtered and preprocessed image collection with:
            - Standardized metadata properties (cloud_cover, satellite_name, etc.)
            - Applied scale factors (if scaleFactor=True)
            - Filtered by date, cloud cover, geometry, and blacklist
            - 'reflectance' property set to collectionType value
    
    Processing Steps:
        1. Load collection by ID
        2. Filter by date range
        3. Normalize metadata properties (setProperties)
        4. Set reflectance type property
        5. Apply scale factors (if enabled)
        6. Filter by geometry (if provided)
        7. Exclude blacklisted images (if provided)
        8. Filter by cloud cover threshold
    
    Example - Basic Usage:
        >>> # Get Landsat 8 images for 2020 with <30% clouds
        >>> collection = getCollection(
        ...     collectionId='LANDSAT/LC08/C02/T1_L2',
        ...     dateStart='2020-01-01',
        ...     dateEnd='2020-12-31',
        ...     cloudCover=30
        ... )
    
    Example - With Geometry:
        >>> # Get images for a specific region
        >>> roi = ee.Geometry.Rectangle([-60, -30, -50, -20])
        >>> collection = getCollection(
        ...     collectionId='LANDSAT/LC08/C02/T1_L2',
        ...     dateStart='2020-01-01',
        ...     dateEnd='2020-12-31',
        ...     cloudCover=50,
        ...     geometry=roi
        ... )
    
    Example - With Blacklist:
        >>> # Exclude specific bad images
        >>> bad_images = ['LC08_226080_20200515', 'LC08_226080_20200601']
        >>> collection = getCollection(
        ...     collectionId='LANDSAT/LC08/C02/T1_L2',
        ...     dateStart='2020-01-01',
        ...     dateEnd='2020-12-31',
        ...     cloudCover=30,
        ...     trashList=bad_images
        ... )
    
    Example - TOA Reflectance:
        >>> # Get TOA instead of Surface Reflectance
        >>> collection = getCollection(
        ...     collectionId='LANDSAT/LC08/C02/T1_TOA',
        ...     collectionType='TOA',
        ...     dateStart='2020-01-01',
        ...     dateEnd='2020-12-31',
        ...     cloudCover=30
        ... )
    
    Note:
        - Cloud cover filtering happens last to work with normalized 'cloud_cover' property
        - Geometry filtering is applied before blacklist filtering for efficiency
        - Scale factors are applied after metadata normalization
        - The 'reflectance' property can be used to track SR vs TOA in mixed workflows
    
    See Also:
        - setProperties(): For metadata normalization details
        - applyScaleFactors(): For SR scale factor details
        - applyScaleFactorsTOA(): For TOA scale factor details
    """
    # Set end date to today if not specified
    if dateEnd == None:
        dateEnd = str(date.today())

    # Initialize collection with date filter and metadata normalization
    collection = ee.ImageCollection(collectionId)\
        .filter(ee.Filter.date(dateStart, dateEnd))\
        .map(setProperties) \
        .map(
            lambda image: image.set('reflectance', collectionType)
        )
    
    # Apply appropriate scale factors based on collection type
    if scaleFactor:
        if collectionType == 'TOA':
            collection = collection.map(applyScaleFactorsTOA)
        else:  # Surface Reflectance (SR)
            collection = collection.map(applyScaleFactors)
    
    # Filter by geometry (spatial extent) if provided
    # This reduces the collection to only images intersecting the ROI
    if geometry != None:
        collection = collection.filterBounds(geometry)
    
    # Exclude blacklisted images if provided
    # Uses inverted filter: keep images NOT in the trash list
    if trashList != None:
        collection = collection.filter(
            ee.Filter.inList('system:index', trashList).Not()
        )

    # Filter by maximum cloud cover threshold
    # Uses normalized 'cloud_cover' property from setProperties()
    collection = collection.filterMetadata(
        'cloud_cover', 'less_than', cloudCover)
    
    return collection
