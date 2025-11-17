"""
Google Earth Engine Spectral Indices Module
============================================

This module provides functions to calculate various spectral indices from
satellite imagery. These indices enhance specific features like vegetation,
water, urban areas, and bare soil by combining spectral bands mathematically.

Spectral indices are transformations of two or more spectral bands designed
to highlight particular features while minimizing effects like atmospheric
conditions, soil background, and illumination variations.

Categories:
- Vegetation Indices: NDVI, EVI, EVI2, SAVI, PRI, GCVI
- Water Indices: NDWI, MNDWI
- Urban/Built-up Indices: NDBI, UI, BU, EBBI
- Other: CAI (Cellulose Absorption), Hall indices (forest structure)

Dependencies: earthengine-api
"""

import ee


def getNDVI(image):
    """
    Calculate Normalized Difference Vegetation Index (NDVI).
    
    NDVI is the most widely used vegetation index. It exploits the high
    reflectance of vegetation in NIR and low reflectance in red to measure
    vegetation health, density, and greenness.
    
    Formula: NDVI = (NIR - Red) / (NIR + Red)
    
    Args:
        image (ee.Image): Input image with 'nir' and 'red' bands
    
    Returns:
        ee.Image: Image with added 'ndvi' band
            Range after +1 offset: 0 to 2 (original range: -1 to 1)
            Values interpretation (before +1):
                < 0: Water, clouds, snow
                0-0.2: Bare soil, rock
                0.2-0.5: Sparse vegetation, grassland
                0.5-0.8: Dense vegetation, crops
                > 0.8: Very dense vegetation, forests
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> ndvi_image = getNDVI(image)
        >>> ndvi = ndvi_image.select('ndvi')
    
    Note:
        - Result is shifted by +1 to avoid negative values (easier storage)
        - Subtract 1 from band values to get actual NDVI range
        - Saturates at high vegetation density (use EVI for dense vegetation)
    
    Applications:
        - Crop health monitoring
        - Vegetation mapping
        - Drought assessment
        - Biomass estimation
    """
    exp = '( b("nir") - b("red") ) / ( b("nir") + b("red") )'

    ndvi = image.expression(exp)\
        .rename(["ndvi"])\
        .add(1)  # Shift range from [-1,1] to [0,2]

    return image.addBands(srcImg=ndvi, overwrite=True)


def getNDBI(image):
    """
    Calculate Normalized Difference Built-up Index (NDBI).
    
    NDBI highlights urban and built-up areas. Built-up areas have higher
    reflectance in SWIR than NIR, opposite to vegetation.
    
    Formula: NDBI = (SWIR1 - NIR) / (SWIR1 + NIR)
    
    Args:
        image (ee.Image): Input image with 'swir1' and 'nir' bands
    
    Returns:
        ee.Image: Image with added 'ndbi' band
            Range after +1 offset: 0 to 2 (original range: -1 to 1)
            Values interpretation (before +1):
                < 0: Water bodies, dense vegetation
                0-0.1: Low built-up density
                0.1-0.3: Moderate built-up density
                > 0.3: High built-up density (urban cores)
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> ndbi_image = getNDBI(image)
        >>> urban_mask = ndbi_image.select('ndbi').gt(1.3)  # NDBI > 0.3
    
    Note:
        - Higher values indicate built-up surfaces
        - Often used with NDVI for urban-vegetation separation
        - Works best in arid/semi-arid regions
    
    Applications:
        - Urban extent mapping
        - Impervious surface detection
        - Urban growth monitoring
        - Built-up vs vegetation classification
    """
    exp = '( b("swir1") - b("nir") ) / ( b("swir1") + b("nir") )'

    ndbi = image.expression(exp)\
        .rename(["ndbi"])\
        .add(1)  # Shift range from [-1,1] to [0,2]

    return image.addBands(srcImg=ndbi, overwrite=True)


def getUI(image):
    """
    Calculate Urban Index (UI).
    
    UI is similar to NDBI but uses SWIR2 instead of SWIR1. The longer
    wavelength can better discriminate between built-up and bare soil.
    
    Formula: UI = (SWIR2 - NIR) / (SWIR2 + NIR)
    
    Args:
        image (ee.Image): Input image with 'swir2' and 'nir' bands
    
    Returns:
        ee.Image: Image with added 'ui' band
            Range after +1 offset: 0 to 2 (original range: -1 to 1)
            Values interpretation (before +1):
                < 0: Vegetation, water
                0-0.2: Low urban density
                > 0.2: High urban density
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> ui_image = getUI(image)
        >>> urban_areas = ui_image.select('ui').gt(1.2)  # UI > 0.2
    
    Note:
        - Alternative to NDBI using longer wavelength
        - May perform better than NDBI in certain conditions
        - Less affected by soil brightness variations
    
    Applications:
        - Urban area extraction
        - Built-up land mapping
        - Urban planning applications
    """
    exp = '( b("swir2") - b("nir") ) / ( b("swir2") + b("nir") )'

    ui = image.expression(exp)\
        .rename(["ui"])\
        .add(1)  # Shift range from [-1,1] to [0,2]

    return image.addBands(srcImg=ui, overwrite=True)


def getBU(image):
    """
    Calculate Built-Up Index (BU).
    
    BU combines NDBI and NDVI to enhance built-up area detection by
    subtracting vegetation signal from built-up signal. This helps separate
    urban areas from vegetated areas and bare soil.
    
    Formula: BU = NDBI - NDVI
    
    Args:
        image (ee.Image): Input image with 'ndbi' and 'ndvi' bands
            Note: Requires NDBI and NDVI to be calculated first
    
    Returns:
        ee.Image: Image with added 'bu' band
            Range: -2 to 2 (no offset applied)
            Values interpretation:
                < 0: Vegetation-dominated
                0-1: Mixed or bare soil
                > 1: Built-up dominated
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> image = getNDVI(image)
        >>> image = getNDBI(image)
        >>> bu_image = getBU(image)
        >>> urban = bu_image.select('bu').gt(1)
    
    Note:
        - Requires NDBI and NDVI to be calculated beforehand
        - No +1 offset applied (unlike NDVI/NDBI)
        - Positive values indicate urban, negative indicate vegetation
    
    Applications:
        - Urban-vegetation discrimination
        - Built-up area mapping
        - Land cover classification
    """
    exp = 'b("ndbi") - b("ndvi")'

    bu = image.expression(exp)\
        .rename(["bu"])

    return image.addBands(srcImg=bu, overwrite=True)


def getEBBI(image):
    """
    Calculate Enhanced Built-Up and Bareness Index (EBBI).
    
    EBBI combines SWIR1, NIR, and thermal bands to identify built-up and
    bare areas. The thermal component helps discriminate between different
    types of impervious surfaces.
    
    Formula: EBBI = (SWIR1 - NIR) / (10 × √(SWIR1 + TIR))
    
    Args:
        image (ee.Image): Input image with 'swir1_dn', 'nir_dn', and 'tir_dn' bands
            Note: Requires DN (Digital Number) versions of bands
    
    Returns:
        ee.Image: Image with added 'ebbi' band
            Range: Variable (no fixed range)
            Higher values indicate built-up/bare areas
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> ebbi_image = getEBBI(image)
        >>> built_up = ebbi_image.select('ebbi').gt(threshold)
    
    Note:
        - Requires thermal band (not available in Sentinel-2)
        - Uses DN (Digital Number) versions of bands
        - Factor of 10 instead of 0.1 in denominator (DN scaling)
        - More discriminative than simple NDBI
    
    Applications:
        - Built-up area extraction
        - Bare soil mapping
        - Impervious surface detection
        - Urban heat island studies
    """
    # Note: Original formula uses 0.1, but DN version uses 10 (scaling difference)
    # exp = '( b("swir1") - b("nir") ) / ( 0.1 * sqrt(b("swir1") + b("tir")) )'
    exp = '( b("swir1_dn") - b("nir_dn") ) / ( 10 * sqrt(b("swir1_dn") + b("tir_dn")) )'

    ebbi = image.expression(exp)\
        .rename(["ebbi"])

    return image.addBands(srcImg=ebbi, overwrite=True)


def getNDWI(image):
    """
    Calculate Normalized Difference Water Index (NDWI).
    
    NDWI enhances water features. Water has high reflectance in NIR but
    absorbs SWIR, while vegetation and soil have opposite characteristics.
    
    Formula: NDWI = (NIR - SWIR1) / (NIR + SWIR1)
    
    Args:
        image (ee.Image): Input image with 'nir' and 'swir1' bands
    
    Returns:
        ee.Image: Image with added 'ndwi' band
            Range after +1 offset: 0 to 2 (original range: -1 to 1)
            Values interpretation (before +1):
                < 0: Non-water (vegetation, soil)
                0-0.2: Mixed or moist surfaces
                0.2-0.5: Moderate water content
                > 0.5: Open water bodies
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> ndwi_image = getNDWI(image)
        >>> water_mask = ndwi_image.select('ndwi').gt(1.2)  # NDWI > 0.2
    
    Note:
        - Different from MNDWI (which uses green instead of NIR)
        - Better for vegetation water content than open water
        - Shift by +1 to avoid negative values
    
    Applications:
        - Water body mapping
        - Irrigation monitoring
        - Flood extent mapping
        - Wetland delineation
        - Plant water stress detection
    """
    exp = 'float(b("nir") - b("swir1"))/(b("nir") + b("swir1"))'

    ndwi = image.expression(exp)\
        .rename(["ndwi"])\
        .add(1)  # Shift range from [-1,1] to [0,2]

    return image.addBands(srcImg=ndwi, overwrite=True)


def getMNDWI(image):
    """
    Calculate Modified Normalized Difference Water Index (MNDWI).
    
    MNDWI is optimized for open water detection. Uses green instead of NIR
    to better separate water from built-up areas, which can appear similar
    to water in standard NDWI.
    
    Formula: MNDWI = (Green - SWIR1) / (Green + SWIR1)
    
    Args:
        image (ee.Image): Input image with 'green' and 'swir1' bands
    
    Returns:
        ee.Image: Image with added 'mndwi' band
            Range after +1 offset: 0 to 2 (original range: -1 to 1)
            Values interpretation (before +1):
                < 0: Non-water features
                0-0.3: Mixed pixels, shadows
                > 0.3: Open water
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> mndwi_image = getMNDWI(image)
        >>> water = mndwi_image.select('mndwi').gt(1.3)  # MNDWI > 0.3
    
    Note:
        - Better than NDWI for open water detection
        - Less confusion with built-up areas
        - Preferred for water body extraction
        - May include shadows (can be filtered with NIR)
    
    Applications:
        - Open water mapping
        - Coastline extraction
        - Lake and reservoir monitoring
        - Flood mapping
        - Water quality assessment
    """
    exp = 'float(b("green") - b("swir1"))/(b("green") + b("swir1"))'

    mndwi = image.expression(exp)\
        .rename(["mndwi"])\
        .add(1)  # Shift range from [-1,1] to [0,2]

    return image.addBands(srcImg=mndwi, overwrite=True)


def getSAVI(image):
    """
    Calculate Soil Adjusted Vegetation Index (SAVI).
    
    SAVI minimizes soil brightness influences on vegetation indices. Uses
    a soil brightness correction factor (L) to adjust for varying soil
    backgrounds, especially useful in arid regions with sparse vegetation.
    
    Formula: SAVI = 1.5 × (NIR - Red) / (0.5 + NIR + Red)
    
    Args:
        image (ee.Image): Input image with 'nir' and 'red' bands
    
    Returns:
        ee.Image: Image with added 'savi' band
            Range after +1 offset: ~0 to 2.5 (original range: ~-1 to 1.5)
            Values interpretation (before +1):
                < 0: Non-vegetated
                0-0.2: Sparse vegetation
                0.2-0.5: Moderate vegetation
                > 0.5: Dense vegetation
    
    Parameters in Formula:
        L = 0.5 (soil brightness correction factor)
            L = 0: Equivalent to NDVI (high vegetation)
            L = 1: Maximum soil adjustment (sparse vegetation)
            L = 0.5: Moderate vegetation conditions (most common)
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> savi_image = getSAVI(image)
        >>> vegetation = savi_image.select('savi').gt(1.2)  # SAVI > 0.2
    
    Note:
        - Better than NDVI in sparse vegetation areas
        - Reduces soil background effects
        - Particularly useful in arid/semi-arid regions
        - Factor 1.5 = (1 + L) where L = 0.5
    
    Applications:
        - Rangeland vegetation monitoring
        - Sparse crop mapping
        - Arid region vegetation studies
        - Early crop growth detection
    """
    exp = '1.5 * (b("nir") - b("red")) / (0.5 + b("nir") + b("red"))'

    savi = image.expression(exp)\
        .rename(["savi"])\
        .add(1)  # Shift to positive range

    return image.addBands(srcImg=savi, overwrite=True)


def getPRI(image):
    """
    Calculate Photochemical Reflectance Index (PRI).
    
    PRI is sensitive to changes in carotenoid pigments (especially xanthophyll),
    which are indicators of photosynthetic light use efficiency and plant stress.
    
    Formula: PRI = (Blue - Green) / (Blue + Green)
    
    Args:
        image (ee.Image): Input image with 'blue' and 'green' bands
    
    Returns:
        ee.Image: Image with added 'pri' band
            Range after +1 offset: 0 to 2 (original range: -1 to 1)
            Values interpretation (before +1):
                -0.2 to 0: Stressed vegetation
                0 to 0.2: Healthy vegetation
                > 0.2: High photosynthetic efficiency
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> pri_image = getPRI(image)
        >>> stressed = pri_image.select('pri').lt(1.0)  # PRI < 0
    
    Note:
        - Sensitive to physiological stress before visible symptoms
        - Related to xanthophyll cycle activity
        - Useful for precision agriculture
        - Can be affected by canopy structure
    
    Applications:
        - Plant stress detection
        - Light use efficiency estimation
        - Precision agriculture
        - Crop health monitoring
        - Ecosystem productivity studies
    """
    exp = 'float(b("blue") - b("green"))/(b("blue") + b("green"))'

    pri = image.expression(exp)\
        .rename(["pri"])\
        .add(1)  # Shift range from [-1,1] to [0,2]

    return image.addBands(srcImg=pri, overwrite=True)


def getCAI(image):
    """
    Calculate Cellulose Absorption Index (CAI).
    
    CAI detects cellulose absorption features by comparing SWIR2 to SWIR1.
    It's sensitive to plant senescence, litter, and dry vegetation where
    cellulose absorption features are prominent.
    
    Formula: CAI = SWIR2 / SWIR1
    
    Args:
        image (ee.Image): Input image with 'swir2' and 'swir1' bands
    
    Returns:
        ee.Image: Image with added 'cai' band
            Range after +1 offset: ~1 to 3 (original range: ~0 to 2)
            Values interpretation (before +1):
                < 1: Green vegetation (low cellulose)
                1-1.2: Senescing vegetation
                > 1.2: Dry vegetation, crop residue
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> cai_image = getCAI(image)
        >>> dry_veg = cai_image.select('cai').gt(2.2)  # CAI > 1.2
    
    Note:
        - Ratio rather than normalized difference
        - Higher values indicate more cellulose absorption
        - Useful for crop residue detection
        - Complementary to greenness indices
    
    Applications:
        - Crop residue mapping
        - Senescent vegetation detection
        - Harvest monitoring
        - Fire fuel assessment
        - Decomposition studies
    """
    exp = 'float( b("swir2") / b("swir1") )'

    cai = image.expression(exp)\
        .rename(["cai"])\
        .add(1)  # Shift to avoid values near zero

    return image.addBands(srcImg=cai, overwrite=True)


def getEVI(image):
    """
    Calculate Enhanced Vegetation Index (EVI).
    
    EVI improves on NDVI by correcting for soil background signals and
    atmospheric conditions. It remains sensitive to high biomass and doesn't
    saturate as quickly as NDVI in dense vegetation.
    
    Formula: EVI = 2.5 × (NIR - Red) / (NIR + 6×Red - 7.5×Blue + 1)
    
    Args:
        image (ee.Image): Input image with 'nir', 'red', and 'blue' bands
    
    Returns:
        ee.Image: Image with added 'evi' band
            Range after +1 offset: ~0 to 2.5 (original range: ~-1 to 1.5)
            Values interpretation (before +1):
                < 0: Non-vegetated
                0-0.2: Sparse vegetation
                0.2-0.5: Moderate vegetation
                0.5-1.0: Dense vegetation
    
    Coefficients:
        G = 2.5: Gain factor
        C1 = 6: Aerosol resistance red coefficient
        C2 = 7.5: Aerosol resistance blue coefficient
        L = 1: Canopy background adjustment
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> evi_image = getEVI(image)
        >>> dense_veg = evi_image.select('evi').gt(1.5)  # EVI > 0.5
    
    Note:
        - Superior to NDVI for high biomass regions
        - Less saturated in dense vegetation
        - Better atmospheric correction
        - Standard product in MODIS
        - More computationally complex than NDVI
    
    Applications:
        - Global vegetation monitoring
        - Forest biomass estimation
        - Crop growth monitoring
        - Land cover classification
        - Phenology studies
    """
    exp = '2.5 * ((b("nir") - b("red")) / (b("nir") + 6 * b("red") - 7.5 * b("blue") + 1))'

    evi = image.expression(exp)\
        .rename(["evi"])\
        .add(1)  # Shift to positive range

    return image.addBands(srcImg=evi, overwrite=True)


def getEVI2(image):
    """
    Calculate Two-Band Enhanced Vegetation Index (EVI2).
    
    EVI2 is a simplified version of EVI that doesn't require the blue band,
    making it applicable to sensors without blue bands. It maintains most
    of EVI's advantages while being more universally applicable.
    
    Formula: EVI2 = 2.5 × (NIR - Red) / (NIR + 2.4×Red + 1)
    
    Args:
        image (ee.Image): Input image with 'nir' and 'red' bands
    
    Returns:
        ee.Image: Image with added 'evi2' band
            Range after +1 offset: ~0 to 2.5 (original range: ~-1 to 1.5)
            Values interpretation (before +1):
                < 0: Non-vegetated
                0-0.2: Sparse vegetation
                0.2-0.5: Moderate vegetation
                > 0.5: Dense vegetation
    
    Advantages over EVI:
        - Only requires NIR and Red bands
        - Applicable to more sensors
        - Similar performance to EVI
        - Computationally simpler
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> evi2_image = getEVI2(image)
        >>> vegetation = evi2_image.select('evi2').gt(1.3)  # EVI2 > 0.3
    
    Note:
        - Coefficient 2.4 approximates the effect of blue band in EVI
        - Highly correlated with EVI (r² > 0.95)
        - Preferred when blue band unavailable or unreliable
        - Good alternative for sensors like AVHRR
    
    Applications:
        - Vegetation monitoring (blue band unavailable)
        - Historical data analysis
        - Cross-sensor vegetation studies
        - Agricultural monitoring
        - Forest health assessment
    """
    exp = '2.5 * (b("nir") - b("red")) / (b("nir") + (2.4 * b("red")) + 1)'

    evi2 = image.expression(exp)\
        .rename(["evi2"])\
        .add(1)  # Shift to positive range

    return image.addBands(srcImg=evi2, overwrite=True)


def getHallCover(image):
    """
    Calculate Hall Forest Cover Index.
    
    Hall Cover estimates forest canopy cover percentage using empirical
    relationships between surface reflectance and canopy cover. The index
    is based on field-calibrated coefficients for forest environments.
    
    Formula: HallCover = exp((-0.017×Red) - (0.007×NIR) - (0.079×SWIR2) + 5.22)
    
    Args:
        image (ee.Image): Input image with 'red', 'nir', and 'swir2' bands
    
    Returns:
        ee.Image: Image with added 'hallcover' band
            Values: Estimated canopy cover percentage (0-100+)
            Interpretation:
                0-20: Sparse forest or non-forest
                20-50: Open forest
                50-80: Moderate forest cover
                > 80: Dense forest canopy
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> cover_image = getHallCover(image)
        >>> dense_forest = cover_image.select('hallcover').gt(70)
    
    Note:
        - Empirically derived for forest environments
        - Exponential transformation of linear combination
        - Coefficients calibrated from field measurements
        - May need recalibration for different forest types
        - No +1 offset applied (unlike vegetation indices)
    
    Applications:
        - Forest canopy cover estimation
        - Forest density mapping
        - Habitat quality assessment
        - Forest degradation monitoring
        - Biomass estimation (indirect)
    
    Reference:
        Hall et al. forest cover estimation methodology
    """
    exp = '( (-b("red") * 0.017) - (b("nir") * 0.007) - (b("swir2") * 0.079) + 5.22 )'

    hallcover = image.expression(exp)\
        .exp()\
        .rename(["hallcover"])

    return image.addBands(hallcover)


def getHallHeigth(image):
    """
    Calculate Hall Forest Height Index.
    
    Hall Height estimates forest canopy height using empirical relationships
    between surface reflectance and forest structure. Similar to Hall Cover
    but focuses on vertical structure rather than horizontal coverage.
    
    Formula: HallHeight = exp((-0.039×Red) - (0.011×NIR) - (0.026×SWIR1) + 4.13)
    
    Args:
        image (ee.Image): Input image with 'red', 'nir', and 'swir1' bands
    
    Returns:
        ee.Image: Image with added 'hallheigth' band
            Values: Estimated canopy height in meters
            Interpretation:
                < 5: Low vegetation or shrubland
                5-15: Young forest or short trees
                15-30: Mature forest
                > 30: Old-growth or tall forest
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> height_image = getHallHeigth(image)
        >>> tall_forest = height_image.select('hallheigth').gt(20)
    
    Note:
        - Note the typo in band name: 'hallheigth' (should be 'hallheight')
        - Empirically derived for forest environments
        - Exponential transformation of linear combination
        - Indirect height estimation (not LiDAR precision)
        - May require local calibration
        - Complementary to Hall Cover index
    
    Applications:
        - Forest structure assessment
        - Biomass estimation
        - Carbon stock estimation
        - Forest age classification
        - Habitat suitability modeling
    
    Reference:
        Hall et al. forest height estimation methodology
    """
    exp = '( (-b("red") * 0.039) - (b("nir") * 0.011) - (b("swir1") * 0.026) + 4.13 )'

    hallheigth = image.expression(exp)\
        .exp()\
        .rename(["hallheigth"])

    return image.addBands(hallheigth)


def getGCVI(image):
    """
    Calculate Green Chlorophyll Vegetation Index (GCVI).
    
    GCVI is sensitive to chlorophyll content and emphasizes green vegetation.
    The ratio of NIR to green is particularly responsive to chlorophyll
    concentration and is less affected by leaf structure than NDVI.
    
    Formula: GCVI = (NIR / Green) - 1
    
    Args:
        image (ee.Image): Input image with 'nir' and 'green' bands
    
    Returns:
        ee.Image: Image with added 'gcvi' band
            Range after +1 offset: ~0 to 20+ (original range: ~-1 to 19+)
            Values interpretation (before +1):
                < 0: Non-vegetated or stressed
                0-3: Sparse or senescing vegetation
                3-8: Healthy vegetation
                > 8: Very dense, healthy vegetation
    
    Example:
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> gcvi_image = getGCVI(image)
        >>> healthy_veg = gcvi_image.select('gcvi').gt(4)  # GCVI > 3
    
    Note:
        - Simple ratio index
        - Highly sensitive to chlorophyll content
        - Can have very high values for dense vegetation
        - Less saturated than NDVI in some conditions
        - Offset by +1 to avoid negative values
    
    Applications:
        - Chlorophyll content estimation
        - Crop nitrogen assessment
        - Vegetation health monitoring
        - Precision agriculture
        - Photosynthesis estimation
    
    Alternative Names:
        - Also known as GRVI (Green Ratio Vegetation Index)
    """
    exp = 'b("nir") / b("green") - 1'

    gcvi = image.expression(exp)\
        .rename(["gcvi"])\
        .add(1)  # Shift to positive range

    return image.addBands(gcvi)
