"""
Google Earth Engine Band Name Standardization Module
=====================================================

This module provides standardized band naming conventions for Landsat and
Sentinel-2 satellite imagery across different collection versions and product types.

The module maps original band names from various satellite products to consistent,
human-readable names. This standardization enables cross-sensor analysis and
simplifies code by using universal names like 'nir' and 'red' instead of
sensor-specific names like 'SR_B4' or 'B8'.

Supported Satellites:
- Landsat 4, 5 TM (Thematic Mapper)
- Landsat 7 ETM+ (Enhanced Thematic Mapper Plus)
- Landsat 8, 9 OLI (Operational Land Imager)
- Sentinel-2 MSI (MultiSpectral Instrument)

Supported Products:
- Surface Reflectance (SR) - Collection 2 and Legacy
- Top-of-Atmosphere (TOA) - Collection 2 and Legacy
- Urban products (with DN bands for EBBI calculation)
- Harmonized products (Sentinel-2 with additional red-edge bands)

Standard Band Names:
- blue, green, red: Visible spectrum
- nir: Near-infrared
- swir1, swir2: Shortwave infrared
- pixel_qa: Quality assessment band
- tir: Thermal infrared
- red_edge_*: Sentinel-2 red-edge bands

Dependencies: earthengine-api
"""

import ee

# Standard Landsat band names (8 bands)
LANDSAT_NEW_NAMES = [
    'blue',      # Blue band (~450-520 nm)
    'green',     # Green band (~520-600 nm)
    'red',       # Red band (~630-690 nm)
    'nir',       # Near-infrared (~760-900 nm)
    'swir1',     # Shortwave infrared 1 (~1550-1750 nm)
    'swir2',     # Shortwave infrared 2 (~2080-2350 nm)
    'pixel_qa',  # Quality assessment/flags
    'tir'        # Thermal infrared (~10400-12500 nm)
]

# Standard Sentinel-2 band names (8 bands)
SENTINEL_NEW_NAMES = [
    'blue',       # Blue band (B2, ~490 nm)
    'green',      # Green band (B3, ~560 nm)
    'red',        # Red band (B4, ~665 nm)
    'red_edge_1', # Red-edge 1 (B5, ~705 nm)
    'nir',        # Near-infrared (B8, ~842 nm)
    'swir1',      # Shortwave infrared 1 (B11, ~1610 nm)
    'swir2',      # Shortwave infrared 2 (B12, ~2190 nm)
    'pixel_qa'    # Quality assessment (QA60)
]

# Band name mapping dictionary for all supported satellite products
BAND_NAMES = {
    # ========================================================================
    # LANDSAT COLLECTION 2 SURFACE REFLECTANCE
    # ========================================================================
    
    'l4c2': {
        'bandNames': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'QA_PIXEL', 'ST_B6'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 4 TM Collection 2 Level-2 Surface Reflectance
        # SR_B1-B5,B7: Surface reflectance bands
        # QA_PIXEL: Pixel quality flags
        # ST_B6: Surface temperature from thermal band 6
    },
    'l5c2': {
        'bandNames': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'QA_PIXEL', 'ST_B6'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 5 TM Collection 2 Level-2 Surface Reflectance
        # Identical band structure to Landsat 4
    },
    'l7c2': {
        'bandNames': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'QA_PIXEL', 'ST_B6'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 7 ETM+ Collection 2 Level-2 Surface Reflectance
        # Similar band structure to L4/L5 (note: B6 is thermal, acquired at 60m)
    },
    'l8c2': {
        'bandNames': ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'QA_PIXEL', 'ST_B10'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 8 OLI/TIRS Collection 2 Level-2 Surface Reflectance
        # Note: Band numbers shifted (starts at B2 instead of B1)
        # B1 (coastal aerosol) and B9 (cirrus) excluded
        # ST_B10: Surface temperature from TIRS band 10
    },
    'l9c2': {
        'bandNames': ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'QA_PIXEL', 'ST_B10'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 9 OLI-2/TIRS-2 Collection 2 Level-2 Surface Reflectance
        # Identical band structure to Landsat 8
    },

    # ========================================================================
    # LANDSAT COLLECTION 2 TOP-OF-ATMOSPHERE
    # ========================================================================
    
    'l4c2toa': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'QA_PIXEL', 'B6'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 4 TM Collection 2 Level-1 TOA Reflectance
        # B1-B5,B7: TOA reflectance bands
        # B6: Thermal band (brightness temperature)
    },
    'l5c2toa': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'QA_PIXEL', 'B6'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 5 TM Collection 2 Level-1 TOA Reflectance
        # Identical structure to Landsat 4 TOA
    },
    'l7c2toa': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'QA_PIXEL', 'B6_VCID_1'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 7 ETM+ Collection 2 Level-1 TOA Reflectance
        # B6_VCID_1: Thermal band (low gain)
        # Note: B6_VCID_2 (high gain) not included in standard mapping
    },
    'l8c2toa': {
        'bandNames': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'QA_PIXEL', 'B10'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 8 OLI/TIRS Collection 2 Level-1 TOA Reflectance
        # B10: Thermal infrared band 10
        # B11 (TIRS band 11) excluded due to calibration issues
    },

    # ========================================================================
    # LANDSAT COLLECTION 1 (LEGACY) SURFACE REFLECTANCE
    # ========================================================================
    
    'l5': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa', 'B6'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 5 TM Collection 1 Surface Reflectance (Legacy)
        # Note: pixel_qa instead of QA_PIXEL
    },
    'l7': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa', 'B6'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 7 ETM+ Collection 1 Surface Reflectance (Legacy)
    },
    'l8': {
        'bandNames': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa', 'B11'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 8 OLI/TIRS Collection 1 Surface Reflectance (Legacy)
        # B11: Thermal band 11 (before calibration issues were known)
    },

    # ========================================================================
    # LANDSAT COLLECTION 1 (LEGACY) TOP-OF-ATMOSPHERE
    # ========================================================================
    
    'l5toa': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'BQA', 'B6'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 5 TM Collection 1 TOA Reflectance (Legacy)
        # BQA: Quality band (older naming convention)
    },
    'l7toa': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'BQA', 'B6_VCID_1'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 7 ETM+ Collection 1 TOA Reflectance (Legacy)
    },
    'l8toa': {
        'bandNames': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'BQA', 'B11'],
        'newNames': LANDSAT_NEW_NAMES
        # Landsat 8 OLI/TIRS Collection 1 TOA Reflectance (Legacy)
    },

    # ========================================================================
    # SENTINEL-2
    # ========================================================================
    
    'sentinel-2 (toa)': {
        'bandNames': ['B2', 'B3', 'B4', 'B5', 'B8', 'B11', 'B12', 'QA60'],
        'newNames': SENTINEL_NEW_NAMES
        # Sentinel-2 MSI Level-1C (TOA Reflectance)
        # B2: Blue, B3: Green, B4: Red
        # B5: Red-edge 1 (705nm)
        # B8: NIR (wide band)
        # B11-B12: SWIR bands
        # QA60: Cloud probability from Sen2Cor
    },
    's2': {
        'bandNames': ['B2', 'B3', 'B4', 'B5', 'B8', 'B11', 'B12', 'QA60'],
        'newNames': SENTINEL_NEW_NAMES
        # Sentinel-2 MSI (generic mapping for both L1C and L2A)
        # Note: B5 is first red-edge band at 705nm
    },
    's2_harmonized': {
        'bandNames': [
            'B2',   # Blue
            'B3',   # Green
            'B4',   # Red
            'B5',   # Red-edge 1 (705 nm)
            'B6',   # Red-edge 2 (740 nm)
            'B7',   # Red-edge 3 (783 nm)
            'B8',   # NIR (842 nm, wide)
            'B8A',  # NIR narrow (865 nm)
            'B11',  # SWIR 1 (1610 nm)
            'B12',  # SWIR 2 (2190 nm)
            'QA60'  # Cloud probability
        ],
        'newNames': [
            'blue',
            'green',
            'red',
            'red_edge_1',
            'red_edge_2',
            'red_edge_3',
            'nir',
            'red_edge_4',
            'swir1',
            'swir2',
            'pixel_qa'
        ]
        # Sentinel-2 Harmonized product with all red-edge bands
        # Includes additional bands (B6, B7, B8A) not in basic mapping
        # B8A mapped to red_edge_4 (narrow NIR band)
        # Useful for vegetation analysis requiring red-edge information
    },

    # ========================================================================
    # LANDSAT URBAN PRODUCTS (with Digital Number bands)
    # ========================================================================
    
    'l5_urban': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa', 'B6', 'B4_1', 'B5_1', 'B6_1'],
        'newNames': LANDSAT_NEW_NAMES + ['swir1_dn', 'nir_dn', 'tir_dn']
        # Landsat 5 for urban analysis with additional DN bands
        # Standard 8 bands + 3 Digital Number (DN) bands:
        # B4_1 -> nir_dn: NIR in DN for EBBI calculation
        # B5_1 -> swir1_dn: SWIR1 in DN for EBBI calculation
        # B6_1 -> tir_dn: Thermal in DN for EBBI calculation
        # DN bands needed for Enhanced Built-Up and Bareness Index (EBBI)
    },
    'l7_urban': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa', 'B6', 'B4_1', 'B5_1', 'B6_VCID_2'],
        'newNames': LANDSAT_NEW_NAMES + ['swir1_dn', 'nir_dn', 'tir_dn']
        # Landsat 7 for urban analysis with additional DN bands
        # B6_VCID_2: Thermal high gain in DN
        # Similar structure to l5_urban
    },
    'l8_urban': {
        'bandNames': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa', 'B11', 'B5_1', 'B6_1', 'B11_1'],
        'newNames': LANDSAT_NEW_NAMES + ['swir1_dn', 'nir_dn', 'tir_dn']
        # Landsat 8 for urban analysis with additional DN bands
        # B5_1 -> nir_dn: NIR in DN
        # B6_1 -> swir1_dn: SWIR1 in DN
        # B11_1 -> tir_dn: Thermal in DN
        # Note: Band numbering different from L4/L5/L7 (starts at B2)
    },
}


def getBandNames(key):
    """
    Retrieve standardized band name mapping for a satellite product.
    
    This function returns a dictionary containing the original band names from
    a satellite product and their corresponding standardized names. This enables
    consistent band referencing across different satellites and product versions.
    
    Args:
        key (str): Product identifier key
            
            Supported keys:
            
            Landsat Collection 2:
                - 'l4c2', 'l5c2', 'l7c2', 'l8c2', 'l9c2': Surface Reflectance
                - 'l4c2toa', 'l5c2toa', 'l7c2toa', 'l8c2toa': TOA Reflectance
            
            Landsat Collection 1 (Legacy):
                - 'l5', 'l7', 'l8': Surface Reflectance
                - 'l5toa', 'l7toa', 'l8toa': TOA Reflectance
            
            Sentinel-2:
                - 's2': Standard mapping (7 optical + QA)
                - 's2_harmonized': Full mapping with red-edge bands
                - 'sentinel-2 (toa)': TOA product
            
            Urban Products:
                - 'l5_urban', 'l7_urban', 'l8_urban': With DN bands for EBBI
    
    Returns:
        dict: Dictionary with two keys:
            - 'bandNames' (list): Original band names from satellite product
            - 'newNames' (list): Corresponding standardized names
            
            Lists are parallel (same length, index correspondence)
    
    Raises:
        KeyError: If the provided key is not in BAND_NAMES dictionary
    
    Example Usage:
        Basic band renaming:
            >>> bands = getBandNames('l8c2')
            >>> print(bands)
            {
                'bandNames': ['SR_B2', 'SR_B3', 'SR_B4', ...],
                'newNames': ['blue', 'green', 'red', ...]
            }
            
            >>> # Use with GEE image
            >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
            >>> bands = getBandNames('l8c2')
            >>> renamed = image.select(bands['bandNames'], bands['newNames'])
            >>> # Now can use: renamed.select('nir') instead of 'SR_B5'
        
        Cross-sensor processing:
            >>> # Process Landsat 8 and Sentinel-2 with same code
            >>> l8_bands = getBandNames('l8c2')
            >>> s2_bands = getBandNames('s2')
            >>> 
            >>> l8_image = ee.Image('LANDSAT/LC08/...').select(
            ...     l8_bands['bandNames'], l8_bands['newNames'])
            >>> s2_image = ee.Image('COPERNICUS/S2_SR/...').select(
            ...     s2_bands['bandNames'], s2_bands['newNames'])
            >>> 
            >>> # Both images now have standardized names
            >>> l8_ndvi = l8_image.normalizedDifference(['nir', 'red'])
            >>> s2_ndvi = s2_image.normalizedDifference(['nir', 'red'])
        
        Urban analysis with DN bands:
            >>> bands = getBandNames('l8_urban')
            >>> print(bands['newNames'])
            ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 
             'pixel_qa', 'tir', 'swir1_dn', 'nir_dn', 'tir_dn']
            >>> # Now have both reflectance and DN versions for EBBI
    
    Best Practices:
        1. Always use this function when working with multiple satellite products
        2. Store the key as metadata in processed images for traceability
        3. For Collection 2, prefer 'c2' variants over legacy collections
        4. Use 's2_harmonized' when red-edge information is needed
        5. Use urban variants when calculating EBBI or similar DN-based indices
    
    Notes:
        - All Landsat products map to 8 standard bands (except urban: 11 bands)
        - Sentinel-2 basic mapping has 8 bands (no thermal)
        - Sentinel-2 harmonized has 11 bands (with red-edge)
        - Urban products include 3 additional DN bands for EBBI calculation
        - Band order in lists is preserved from satellite products
        - Thermal bands: L4/L5/L7 use B6, L8/L9 use B10/B11
    
    Band Wavelength Reference:
        - blue: ~450-520 nm (coastal/blue)
        - green: ~520-600 nm
        - red: ~630-690 nm
        - nir: ~760-900 nm (near-infrared)
        - swir1: ~1550-1750 nm (shortwave infrared)
        - swir2: ~2080-2350 nm
        - tir: ~10400-12500 nm (thermal infrared)
        - red_edge: ~700-790 nm (Sentinel-2 only)
    
    See Also:
        - Collection.getCollection(): Uses this function for band renaming
        - Landsat Collection 2 documentation: https://www.usgs.gov/landsat-missions/
        - Sentinel-2 band info: https://sentinels.copernicus.eu/
    """
    return BAND_NAMES[key]
