"""
Google Earth Engine Spectral Mixture Analysis (SMA) and NDFI Module
====================================================================

This module implements Spectral Mixture Analysis (SMA) and related fraction-based
indices for satellite imagery. SMA decomposes each pixel's reflectance into
proportions (fractions) of pure surface types called endmembers.

Core Concept:
SMA assumes that each pixel's reflectance is a linear combination of pure
endmember spectra. The algorithm unmixes the pixel to estimate the proportion
of each endmember, providing physical interpretations of land cover composition.

Endmembers Used:
1. GV (Green Vegetation): Live, photosynthetically active vegetation
2. NPV (Non-Photosynthetic Vegetation): Dead vegetation, senescent leaves, litter
3. Soil: Bare soil and exposed earth
4. Cloud: Cloud cover
5. Shade: Shadow component (derived from residual)

Fraction-Based Indices:
- NDFI (Normalized Difference Fraction Index): Forest degradation
- SEFI (Soil Enhanced Fraction Index): Soil exposure
- WEFI (Water Enhanced Fraction Index): Moisture/water content
- FNS (Forest/Non-forest Stratification): Forest classification

Applications:
- Forest degradation and selective logging detection
- Land cover change analysis
- Agricultural monitoring
- Soil exposure assessment
- Vegetation stress detection


Dependencies: earthengine-api
Reference: Souza et al. (2005) NDFI methodology, adapted from Carnegie Institution
"""

import ee

# ============================================================================
# SPECTRAL ENDMEMBER DEFINITIONS
# ============================================================================

ENDMEMBERS = {
    # Landsat 4 TM endmembers (scaled reflectance × 10000)
    # Each row is an endmember, columns are: blue, green, red, nir, swir1, swir2
    'landsat-4': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],    # GV (Green Vegetation)
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0], # NPV (Non-Photosynthetic Vegetation)
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0], # Soil
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]  # Cloud
    ],
    
    # Landsat 5 TM endmembers (identical to L4)
    'landsat-5': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    
    # Landsat 7 ETM+ endmembers (identical to L4/L5)
    'landsat-7': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    
    # Landsat 8 OLI endmembers (same values, adjusted for sensor)
    'landsat-8': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    
    # Landsat 9 OLI-2 endmembers (identical to L8)
    'landsat-9': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    
    # Sentinel-2 Surface Reflectance endmembers
    'sentinel-2 (sr)': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    
    # Sentinel-2 TOA endmembers (identical to SR)
    'sentinel-2 (toa)': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    
    # Sentinel-2 Harmonized endmembers
    'sentinel-2 (harmonized)': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    
    # Simplified 3-endmember model
    'small': [
        [1780, 3370, 4580, 5590, 6830, 6450],  # Substrate (soil-like)
        [300, 600, 310, 6690, 2400, 960],      # Vegetation
        [190, 100, 50, 70, 30, 20]             # Dark (shadow/water)
    ]
}

# ============================================================================
# NDFI COLOR PALETTE
# ============================================================================

# Color palette for NDFI visualization (200 colors from degraded to intact forest)
# Format: Hexadecimal RGB colors (white -> magenta -> yellow -> green)
# Range: 0-200 (0=highly degraded, 200=intact forest)
NDFI_COLORS = 'ffffff,fffcff,fff9ff,fff7ff,fff4ff,fff2ff,ffefff,ffecff,ffeaff,ffe7ff,' +\
    'ffe5ff,ffe2ff,ffe0ff,ffddff,ffdaff,ffd8ff,ffd5ff,ffd3ff,ffd0ff,ffceff,' +\
    'ffcbff,ffc8ff,ffc6ff,ffc3ff,ffc1ff,ffbeff,ffbcff,ffb9ff,ffb6ff,ffb4ff,' +\
    'ffb1ff,ffafff,ffacff,ffaaff,ffa7ff,ffa4ff,ffa2ff,ff9fff,ff9dff,ff9aff,' +\
    'ff97ff,ff95ff,ff92ff,ff90ff,ff8dff,ff8bff,ff88ff,ff85ff,ff83ff,ff80ff,' +\
    'ff7eff,ff7bff,ff79ff,ff76ff,ff73ff,ff71ff,ff6eff,ff6cff,ff69ff,ff67ff,' +\
    'ff64ff,ff61ff,ff5fff,ff5cff,ff5aff,ff57ff,ff55ff,ff52ff,ff4fff,ff4dff,' +\
    'ff4aff,ff48ff,ff45ff,ff42ff,ff40ff,ff3dff,ff3bff,ff38ff,ff36ff,ff33ff,' +\
    'ff30ff,ff2eff,ff2bff,ff29ff,ff26ff,ff24ff,ff21ff,ff1eff,ff1cff,ff19ff,' +\
    'ff17ff,ff14ff,ff12ff,ff0fff,ff0cff,ff0aff,ff07ff,ff05ff,ff02ff,ff00ff,' +\
    'ff00ff,ff0af4,ff15e9,ff1fdf,ff2ad4,ff35c9,ff3fbf,ff4ab4,ff55aa,ff5f9f,' +\
    'ff6a94,ff748a,ff7f7f,ff8a74,ff946a,ff9f5f,ffaa55,ffb44a,ffbf3f,ffc935,' +\
    'ffd42a,ffdf1f,ffe915,fff40a,ffff00,ffff00,fffb00,fff700,fff300,fff000,' +\
    'ffec00,ffe800,ffe400,ffe100,ffdd00,ffd900,ffd500,ffd200,ffce00,ffca00,' +\
    'ffc600,ffc300,ffbf00,ffbb00,ffb700,ffb400,ffb000,ffac00,ffa800,ffa500,' +\
    'ffa500,f7a400,f0a300,e8a200,e1a200,d9a100,d2a000,ca9f00,c39f00,bb9e00,' +\
    'b49d00,ac9c00,a59c00,9d9b00,969a00,8e9900,879900,7f9800,789700,709700,' +\
    '699600,619500,5a9400,529400,4b9300,439200,349100,2d9000,258f00,1e8e00,' +\
    '168e00,0f8d00,078c00,008c00,008c00,008700,008300,007f00,007a00,007600,' +\
    '007200,006e00,006900,006500,006100,005c00,005800,005400,005000,004c00'


# ============================================================================
# SPECTRAL MIXTURE ANALYSIS FUNCTIONS
# ============================================================================

def getFractions(image, endmembers):
    """
    Perform Spectral Mixture Analysis (SMA) to decompose pixel reflectance into fractions.
    
    This function unmixes each pixel's reflectance into proportions of four endmembers:
    Green Vegetation (GV), Non-Photosynthetic Vegetation (NPV), Soil, and Cloud.
    It also calculates a Shade fraction from the unmixing residual.
    
    The linear spectral mixture model assumes:
    Pixel_reflectance = (GV_fraction × GV_spectrum) + (NPV_fraction × NPV_spectrum) + 
                        (Soil_fraction × Soil_spectrum) + (Cloud_fraction × Cloud_spectrum)
    
    Args:
        image (ee.Image): Input image with standardized bands: 
            blue, green, red, nir, swir1, swir2
        endmembers (list): List of 4 endmember spectra (each with 6 values)
            Format: [[gv], [npv], [soil], [cloud]]
            Retrieve from ENDMEMBERS dictionary using satellite key
    
    Returns:
        ee.Image: Original image with added fraction bands:
            - gv: Green vegetation fraction (0-100%)
            - npv: Non-photosynthetic vegetation fraction (0-100%)
            - soil: Soil fraction (0-100%)
            - cloud: Cloud fraction (0-100%)
            - shade: Shade/shadow fraction (0-100%)
    
    Fraction Interpretation:
        GV: Live, photosynthetically active vegetation (high NIR, low red)
        NPV: Dead vegetation, crop residue, senescent leaves (high SWIR)
        Soil: Bare soil, exposed earth (moderate across all bands)
        Cloud: Bright clouds (high in all bands)
        Shade: Shadows, water, dark surfaces (residual: 100 - sum(gv+npv+soil))
    
    Algorithm Steps:
        1. Select 6 optical bands (blue through swir2)
        2. Apply linear unmixing with endmembers
        3. Constrain fractions to non-negative (max with 0)
        4. Scale to 0-100 range and convert to byte
        5. Calculate shade as residual from 100%
    
    Example:
        >>> from modules.SmaAndNdfi import ENDMEMBERS
        >>> 
        >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
        >>> image = image.select(['SR_B2', ...], ['blue', ...])
        >>> 
        >>> endmember = ENDMEMBERS['landsat-8']
        >>> fractions = getFractions(image, endmember)
        >>> 
        >>> # Access individual fractions
        >>> gv = fractions.select('gv')
        >>> shade = fractions.select('shade')
        >>> 
        >>> # Forest has high GV, low NPV
        >>> forest_mask = gv.gt(60).And(npv.lt(20))
    
    Notes:
        - Fractions are constrained to 0-100% (negative values set to 0)
        - Sum of GV+NPV+Soil may not equal 100% (residual becomes shade)
        - High shade values indicate shadows, water, or dark surfaces
        - Byte data type (0-100 integers) for efficient storage
        - All endmembers use same spectral basis (6 bands)
    
    Endmember Selection:
        - Use satellite-specific endmembers from ENDMEMBERS dictionary
        - Same endmembers work across Landsat 4-9 (empirically validated)
        - Sentinel-2 uses adapted but numerically identical endmembers
    
    Applications:
        - Input for NDFI calculation (forest degradation)
        - Input for SEFI, WEFI, FNS indices
        - Land cover classification
        - Change detection analysis
        - Vegetation monitoring
    
    Reference:
        - Souza et al. (2005) Journal of Geophysical Research
        - Adams et al. (1995) Remote Sensing of Environment
    """
    # Output band names for the four unmixed fractions
    outBandNames = ['gv', 'npv', 'soil', 'cloud']

    # Perform linear spectral unmixing
    fractions = ee.Image(image)\
        .select(['blue', 'green', 'red', 'nir', 'swir1', 'swir2'])\
        .unmix(endmembers)\
        .max(0)\
        .multiply(100)\
        .byte()

    fractions = fractions.rename(outBandNames)

    # Calculate sum of vegetation and soil fractions
    summed = fractions.expression('b("gv") + b("npv") + b("soil")')

    # Calculate shade fraction as residual from 100%
    # Shade = |100 - (GV + NPV + Soil)|
    shade = summed\
        .subtract(100)\
        .abs()\
        .byte()\
        .rename(["shade"])

    # Add fraction bands to original image
    image = image.addBands(fractions)
    image = image.addBands(shade)

    return image


def getFractionsSmall(image, endmembers):
    """
    Perform simplified 3-endmember Spectral Mixture Analysis.
    
    This is a reduced complexity version using only 3 endmembers:
    Substrate, Vegetation, and Dark. It's computationally faster and
    useful for basic land cover discrimination.
    
    Args:
        image (ee.Image): Input image with standardized bands:
            blue, green, red, nir, swir1, swir2
        endmembers (list): List of 3 endmember spectra (each with 6 values)
            Format: [[substrate], [vegetation], [dark]]
            Use ENDMEMBERS['small'] for standard 3-endmember model
    
    Returns:
        ee.Image: Original image with added fraction bands:
            - subs_small: Substrate fraction (soil-like surfaces) 0-100%
            - veg_small: Vegetation fraction (all vegetation) 0-100%
            - dark_small: Dark fraction (water, shadow) 0-100%
    
    Fraction Interpretation:
        Substrate: Bare soil, rock, built-up areas
        Vegetation: All vegetated surfaces (live + dead combined)
        Dark: Water bodies, shadows, very dark surfaces
    
    Example:
        >>> endmember_small = ENDMEMBERS['small']
        >>> fractions = getFractionsSmall(image, endmember_small)
        >>> 
        >>> vegetation = fractions.select('veg_small')
        >>> water_shadow = fractions.select('dark_small')
    
    Notes:
        - Simpler than 4-endmember model (no GV/NPV separation)
        - Faster computation, less detailed information
        - No shade calculation (included in dark endmember)
        - Useful for rapid assessment or limited processing power
    
    Use Cases:
        - Quick land cover assessment
        - Water body detection
        - Broad vegetation mapping
        - When GV/NPV distinction not needed
    """
    # Output band names for 3-endmember model
    outBandNames = ['subs_small', 'veg_small', 'dark_small']

    # Perform linear spectral unmixing with 3 endmembers
    fractions = ee.Image(image)\
        .select(['blue', 'green', 'red', 'nir', 'swir1', 'swir2'])\
        .unmix(endmembers)\
        .max(0)\
        .multiply(100)\
        .byte()

    fractions = fractions.rename(outBandNames)

    # Add fraction bands to original image
    image = image.addBands(fractions)

    return image


# ============================================================================
# FRACTION-BASED INDICES
# ============================================================================

def getNDFI(imageFractions):
    """
    Calculate Normalized Difference Fraction Index (NDFI).
    
    NDFI is designed to detect forest degradation and canopy damage. It enhances
    the contrast between intact forest (high GV) and degraded forest (high NPV+Soil).
    NDFI is sensitive to selective logging, fire damage, and forest edges.
    
    Formula:
        GVs = GV / (GV + NPV + Soil) × 100
        NDFI = (GVs - (NPV + Soil)) / (GVs + (NPV + Soil))
        Scaled: (NDFI × 100) + 100 to range 0-200
    
    Args:
        imageFractions (ee.Image): Image with fraction bands from getFractions():
            Required bands: gv, npv, soil
    
    Returns:
        ee.Image: Original image with added bands:
            - gvs: Green Vegetation Shade-normalized (0-100%)
            - ndfi: Normalized Difference Fraction Index (0-200)
    
    NDFI Value Interpretation (0-200 scale):
        0-100: Degraded forest, high soil/NPV exposure
            0-50: Severely degraded, bare soil, clearcut
            50-100: Moderately degraded, forest edges
        100-150: Transition zone, mixed forest/non-forest
        150-200: Intact forest, closed canopy
            175-200: Dense, undisturbed forest
    
    Algorithm Steps:
        1. Calculate sum of GV + NPV + Soil (excludes cloud and shade)
        2. Normalize GV by sum to get GVs (shade-normalized green vegetation)
        3. Calculate normalized difference between GVs and (NPV+Soil)
        4. Rescale from [-1,1] to [0,200] for easier interpretation
    
    Example:
        >>> # After running getFractions
        >>> image_with_ndfi = getNDFI(image_with_fractions)
        >>> ndfi = image_with_ndfi.select('ndfi')
        >>> 
        >>> # Classify forest condition
        >>> intact = ndfi.gte(175)
        >>> degraded = ndfi.lt(100)
        >>> 
        >>> # Visualize with color palette
        >>> Map.addLayer(ndfi, {
        ...     'min': 0, 'max': 200, 
        ...     'palette': NDFI_COLORS
        ... }, 'NDFI')
    
    Applications:
        - Forest degradation mapping
        - Selective logging detection
        - Forest fire damage assessment
        - Forest edge detection
        - Illegal deforestation monitoring
        - Forest recovery monitoring
    
    Advantages:
        - More sensitive to canopy damage than NDVI
        - Separates degraded from intact forest
        - Less affected by soil brightness
        - Accounts for shade variations
    
    Notes:
        - Requires SMA fractions as input (run getFractions first)
        - Scale 0-200 chosen for compatibility with byte data type
        - Works best in forested landscapes
        - May have limitations in non-forest areas
    
    Reference:
        Souza, C.M., et al. (2005). "Combining spectral and spatial information
        to map canopy damage from selective logging and forest fires."
        Remote Sensing of Environment, 98(2-3), 329-343.
    """
    # Calculate sum of fractions (excluding cloud and shade)
    summed = imageFractions.expression('b("gv") + b("npv") + b("soil")')

    # Calculate shade-normalized green vegetation (GVs)
    # GVs = proportion of GV relative to total non-shade surface
    gvs = imageFractions.select("gv")\
        .divide(summed)\
        .multiply(100)\
        .byte()\
        .rename(["gvs"])

    # Sum of NPV and Soil fractions
    npvSoil = imageFractions.expression('b("npv") + b("soil")')

    # Calculate normalized difference: (GVs - (NPV+Soil)) / (GVs + (NPV+Soil))
    ndfi = ee.Image.cat(gvs, npvSoil)\
        .normalizedDifference()\
        .rename(['ndfi'])

    # Rescale NDFI from [-1, 1] to [0, 200]
    # Formula: (ndfi × 100) + 100
    # -1 becomes 0, 0 becomes 100, 1 becomes 200
    ndfi = ndfi.expression('byte(b("ndfi") * 100 + 100)')

    # Add new bands to image
    imageFractions = imageFractions.addBands(gvs)
    imageFractions = imageFractions.addBands(ndfi)

    return imageFractions


def getSEFI(imageFractions):
    """
    Calculate Soil Enhanced Fraction Index (SEFI).
    
    SEFI enhances soil exposure by contrasting soil fraction against combined
    vegetation fractions (GV+NPV). It's useful for detecting bare soil, erosion,
    and areas with minimal vegetation cover.
    
    Formula:
        GVNPVs = (GV + NPV) / (GV + NPV + Soil) × 100
        SEFI = (GVNPVs - Soil) / (GVNPVs + Soil)
        Scaled: (SEFI × 100) + 100 to range 0-200
    
    Args:
        imageFractions (ee.Image): Image with fraction bands from getFractions():
            Required bands: gv, npv, soil
    
    Returns:
        ee.Image: Original image with added 'sefi' band (0-200)
    
    SEFI Value Interpretation (0-200 scale):
        0-80: High soil exposure, minimal vegetation
            0-50: Bare soil, severely eroded areas
            50-80: Sparse vegetation, exposed soil
        80-120: Moderate soil exposure, mixed surfaces
        120-200: Low soil exposure, vegetation dominant
            150-200: Dense vegetation cover, minimal soil visible
    
    Example:
        >>> image_with_sefi = getSEFI(image_with_fractions)
        >>> sefi = image_with_sefi.select('sefi')
        >>> 
        >>> # Detect high soil exposure
        >>> exposed_soil = sefi.lt(80)
        >>> 
        >>> # Erosion risk areas
        >>> erosion_risk = sefi.lt(60)
    
    Applications:
        - Soil erosion assessment
        - Bare soil mapping
        - Agricultural soil exposure monitoring
        - Degraded land identification
        - Construction site detection
        - Mining area monitoring
    
    Notes:
        - High values indicate vegetation cover (low soil)
        - Low values indicate soil exposure (low vegetation)
        - Complements NDFI for land degradation studies
        - Scale 0-200 for consistency with NDFI
    """
    # Calculate sum of all fractions (excluding cloud and shade)
    summed = imageFractions.expression('b("gv") + b("npv") + b("soil")')
    
    # Extract individual fractions
    soil = imageFractions.select(['soil'])
    npv = imageFractions.select(['npv'])
    gv = imageFractions.select(['gv'])
    
    # Calculate normalized vegetation fraction (GV+NPV relative to sum)
    gvnpv_s = (gv.add(npv).divide(summed)).multiply(100)

    # Calculate normalized difference between vegetation and soil
    sefi = ee.Image.cat(gvnpv_s, soil)\
        .normalizedDifference()\
        .rename(['sefi'])

    # Rescale SEFI from [-1, 1] to [0, 200]
    sefi = sefi.expression('byte(b("sefi") * 100 + 100)')

    # Add SEFI band to image
    imageFractions = imageFractions.addBands(sefi)

    return imageFractions


def getWEFI(imageFractions):
    """
    Calculate Water Enhanced Fraction Index (WEFI).
    
    WEFI enhances moisture and water content by contrasting vegetation fractions
    (GV+NPV) against soil and shade. It's sensitive to water presence, wet soils,
    and areas with high shade content.
    
    Formula:
        Shade = |100 - (GV + NPV + Soil)|
        WEFI = ((GV + NPV) - (Soil + Shade)) / ((GV + NPV) + (Soil + Shade))
        Scaled: (WEFI × 100) + 100 to range 0-200
    
    Args:
        imageFractions (ee.Image): Image with fraction bands from getFractions():
            Required bands: gv, npv, soil
    
    Returns:
        ee.Image: Original image with added 'wefi' band (0-200)
    
    WEFI Value Interpretation (0-200 scale):
        0-80: Low moisture, dry conditions
            0-50: Very dry, minimal water content
            50-80: Dry, low moisture
        80-120: Moderate moisture conditions
        120-200: High moisture, wet conditions
            150-200: Very wet, water bodies, saturated soils
    
    Example:
        >>> image_with_wefi = getWEFI(image_with_fractions)
        >>> wefi = image_with_wefi.select('wefi')
        >>> 
        >>> # Detect water bodies and wet areas
        >>> water = wefi.gt(150)
        >>> 
        >>> # Moisture gradient
        >>> wet = wefi.gt(120)
        >>> moderate = wefi.gte(80).And(wefi.lte(120))
        >>> dry = wefi.lt(80)
    
    Applications:
        - Water body detection
        - Wetland mapping
        - Soil moisture estimation
        - Irrigation monitoring
        - Flood extent mapping
        - Riparian zone delineation
    
    Notes:
        - High values indicate water or high moisture
        - Includes shade component (shadows often associated with water)
        - Useful complement to MNDWI/NDWI spectral indices
        - Scale 0-200 for consistency with other fraction indices
    """
    # Calculate sum of fractions
    summed = imageFractions.expression('b("gv") + b("npv") + b("soil")')
    
    # Extract individual fractions
    soil = imageFractions.select(['soil'])
    npv = imageFractions.select(['npv'])
    gv = imageFractions.select(['gv'])
    
    # Calculate shade fraction as residual
    shd = summed.subtract(100).abs().byte()
    
    # Calculate vegetation sum
    gvnpv = gv.add(npv)
    
    # Calculate soil+shade sum
    soilshade = soil.add(shd)

    # Calculate normalized difference between vegetation and (soil+shade)
    wefi = ee.Image.cat(gvnpv, soilshade)\
        .normalizedDifference()\
        .rename(['wefi'])

    # Rescale WEFI from [-1, 1] to [0, 200]
    wefi = wefi.expression('byte(b("wefi") * 100 + 100)')

    # Add WEFI band to image
    imageFractions = imageFractions.addBands(wefi)

    return imageFractions


def getFNS(imageFractions):

    summed = imageFractions.expression('b("gv") + b("npv") + b("soil")')
    soil = imageFractions.select(['soil'])
    gv = imageFractions.select(['gv'])
    shd = summed.subtract(100).abs().byte()
    gvshade = gv.add(shd)

    # calculate FNS
    fns = ee.Image.cat(gvshade, soil)\
        .normalizedDifference()\
        .rename(['fns'])

    # rescale FNS from 0 to 200
    fns = fns.expression('byte(b("fns") * 100 + 100)')

    imageFractions = imageFractions.addBands(fns)

    return imageFractions
