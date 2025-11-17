"""
Google Earth Engine Miscellaneous Auxiliary Functions Module
=============================================================

This module provides auxiliary functions for adding terrain and texture
information to satellite imagery. These supplementary bands enhance classification
and analysis by providing topographic context and spatial texture measures.

Functions:
- getSlope(): Adds terrain slope from ALOS DEM
- getEntropyG(): Adds texture measure from green band

These functions are typically applied to mosaics before classification to
incorporate additional information beyond spectral reflectance.

Dependencies: earthengine-api, JAXA ALOS DEM
"""

import ee


def getSlope(image):
    """
    Add terrain slope band derived from ALOS World 3D DEM.
    
    This function calculates slope (terrain gradient) from the JAXA ALOS World 3D
    30m Digital Elevation Model and adds it as a band to the input image. Slope
    information helps improve land cover classification, especially for distinguishing
    terrain-dependent classes like agriculture vs natural vegetation.
    
    The ALOS World 3D (AW3D30) is a global DEM with 30-meter resolution derived
    from ALOS PRISM stereo imagery. It provides consistent elevation data suitable
    for topographic analysis.
    
    Args:
        image (ee.Image): Input satellite image or mosaic
            No specific bands required (slope is independent of spectral data)
    
    Returns:
        ee.Image: Original image with added 'slope' band
            slope: Terrain slope in degrees × 100 (0-9000 range)
                Values are scaled by 100 for integer storage
                Example: 1500 = 15.0° slope
                Range: 0° (flat) to 90° (vertical cliff)
    
    Slope Value Interpretation (scaled × 100):
        0-500 (0-5°): Flat to nearly flat terrain
            Suitable for agriculture, urban development
        500-1000 (5-10°): Gentle slopes
            Agriculture possible with care
        1000-1500 (10-15°): Moderate slopes
            Limited agriculture, erosion concerns
        1500-3000 (15-30°): Steep slopes
            Forest, natural vegetation, erosion risk
        3000+ (30°+): Very steep slopes
            Cliffs, rocky terrain, high erosion risk
    
    Algorithm Steps:
        1. Load ALOS World 3D 30m DEM (AVE band = average elevation)
        2. Calculate slope using ee.Terrain.slope() algorithm
        3. Multiply by 100 to scale degrees to integers
        4. Convert to 16-bit integer (int16) for efficient storage
        5. Add as new 'slope' band to input image
    
    Example Usage:
        Basic usage:
            >>> image = ee.Image('LANDSAT/LC08/C02/T1_L2/...')
            >>> image_with_slope = getSlope(image)
            >>> slope = image_with_slope.select('slope')
            >>> 
            >>> # Divide by 100 to get actual degrees
            >>> slope_degrees = slope.divide(100)
            >>> 
            >>> # Classify terrain
            >>> flat = slope.lt(500)  # < 5 degrees
            >>> steep = slope.gt(1500)  # > 15 degrees
        
        With mosaic processing:
            >>> mosaic = getMosaic(collection, ...)
            >>> mosaic = getSlope(mosaic)
            >>> # Now mosaic has slope for classification
        
        Classification with slope:
            >>> # Use slope to improve forest classification
            >>> ndvi = image.select('ndvi')
            >>> slope_band = image.select('slope')
            >>> 
            >>> # Forest on steep slopes (>15°)
            >>> mountain_forest = ndvi.gt(0.6).And(slope_band.gt(1500))
            >>> 
            >>> # Agriculture on flat areas (<5°)
            >>> agriculture = ndvi.gt(0.4).And(slope_band.lt(500))
    
    DEM Details:
        Name: ALOS World 3D - 30m (AW3D30)
        Provider: Japan Aerospace Exploration Agency (JAXA)
        Asset ID: JAXA/ALOS/AW3D30_V1_1
        Resolution: ~30 meters at equator
        Band used: AVE (average elevation in meters)
        Coverage: Global (land areas)
        Vertical accuracy: ~5 meters RMSE
        Version: 1.1 (released 2016)
    
    Slope Calculation:
        The ee.Terrain.slope() function calculates gradient using:
        - Horn's method (3×3 neighborhood)
        - Result in degrees (0-90°)
        - Formula: arctan(√(dz/dx)² + (dz/dy)²) × 180/π
    
    Data Type Considerations:
        - int16 range: -32,768 to 32,767
        - Scaled slope range: 0 to ~9,000 (0° to 90°)
        - Fits comfortably in int16 with headroom
        - Smaller storage than float32
    
    Applications:
        - Land cover classification enhancement
        - Agricultural suitability mapping
        - Erosion risk assessment
        - Forest stratification
        - Hydrological modeling input
        - Terrain-based feature discrimination
        - Topographic normalization
    
    Notes:
        - Slope is calculated once from DEM (not per-image)
        - Independent of image acquisition date
        - Same slope values used for all images in region
        - 30m DEM resolution matches Landsat spatial resolution
        - May not capture fine-scale terrain in mountainous areas
        - Divide by 100 to convert back to degrees when needed
    
    Performance Considerations:
        - DEM data is cached by GEE (fast access)
        - Slope calculation is computationally efficient
        - Minimal impact on overall processing time
        - Adds ~1 band worth of data to image
    
    See Also:
        - ee.Terrain.slope(): GEE terrain algorithm
        - ee.Terrain.aspect(): For terrain aspect/orientation
        - JAXA AW3D30 documentation: https://www.eorc.jaxa.jp/ALOS/en/aw3d30/
    
    Reference:
        Tadono, T., et al. (2014). "Precise Global DEM Generation by ALOS PRISM."
        ISPRS Annals of Photogrammetry, Remote Sensing and Spatial Information Sciences.
    """
    # Load ALOS World 3D 30m Digital Elevation Model
    # AVE band contains average elevation in meters above sea level
    terrain = ee.Image("JAXA/ALOS/AW3D30_V1_1").select("AVE")

    # Calculate slope in degrees using GEE terrain algorithm
    # Multiply by 100 to scale degrees to integers (e.g., 15.5° → 1550)
    # Convert to 16-bit integer for efficient storage
    slope = ee.Terrain.slope(terrain)\
        .multiply(100)\
        .int16()\
        .rename('slope')

    # Add slope band to input image
    return image.addBands(slope)


def getEntropyG(image):
    """
    Calculate texture entropy from green band using Gray Level Co-occurrence Matrix (GLCM).
    
    This function computes spatial texture using Shannon entropy on the green band.
    Entropy measures the randomness or complexity of pixel values within a neighborhood,
    providing information about spatial heterogeneity. High entropy indicates complex,
    varied textures while low entropy indicates homogeneous surfaces.
    
    Texture is a key characteristic for distinguishing land cover types with similar
    spectral signatures but different spatial patterns (e.g., natural forest vs
    plantation, urban vs bare soil).
    
    Args:
        image (ee.Image): Input image containing 'green_median' band
            Typically a mosaic with median-composited bands
            Band name must be exactly 'green_median'
    
    Returns:
        ee.Image: Original image with added texture band:
            green_median_texture: Entropy measure × 100 (0-1000+ range)
                Values are scaled by 100 for integer precision
                Example: 450 = entropy of 4.50
                Higher values = more complex/heterogeneous texture
                Lower values = more homogeneous texture
    
    Entropy Value Interpretation (scaled × 100):
        0-200 (0-2.0): Very homogeneous
            Water bodies, bare soil, uniform surfaces
        200-400 (2.0-4.0): Low texture complexity
            Grasslands, uniform agriculture, sand
        400-600 (4.0-6.0): Moderate texture
            Mixed agriculture, sparse vegetation
        600-800 (6.0-8.0): High texture complexity
            Forest, urban areas, complex landscapes
        800+ (8.0+): Very high texture
            Dense forest, heterogeneous urban, rocky terrain
    
    Algorithm Details:
        Kernel: Square window, radius 5 pixels (11×11 neighborhood)
            Total area: 121 pixels (~0.1 km² at 30m resolution)
        
        Entropy Calculation:
            1. Convert green band to 32-bit integer
            2. For each pixel, examine 11×11 neighborhood
            3. Calculate probability distribution of pixel values
            4. Compute Shannon entropy: H = -Σ(p(i) × log₂(p(i)))
            5. Scale by 100 for integer storage
        
        Shannon Entropy Formula:
            H = -Σᵢ pᵢ log₂(pᵢ)
            where pᵢ is probability of value i in neighborhood
            Maximum entropy for 8-bit data: log₂(256) = 8.0
    
    Example Usage:
        Basic usage:
            >>> mosaic = getMosaic(collection, ...)
            >>> # Mosaic has 'green_median' band from percentile compositing
            >>> mosaic_with_texture = getEntropyG(mosaic)
            >>> texture = mosaic_with_texture.select('green_median_texture')
            >>> 
            >>> # Divide by 100 to get actual entropy
            >>> entropy_actual = texture.divide(100)
            >>> 
            >>> # High texture areas (complex landscapes)
            >>> complex = texture.gt(600)
            >>> # Low texture areas (homogeneous surfaces)
            >>> homogeneous = texture.lt(300)
        
        Classification with texture:
            >>> # Distinguish forest types by texture
            >>> ndvi = mosaic.select('ndvi')
            >>> texture = mosaic.select('green_median_texture')
            >>> 
            >>> # Natural forest: high NDVI + high texture
            >>> natural_forest = ndvi.gt(0.7).And(texture.gt(650))
            >>> 
            >>> # Plantation: high NDVI + low texture (uniform)
            >>> plantation = ndvi.gt(0.7).And(texture.lt(450))
            >>> 
            >>> # Urban: moderate NDVI + high texture
            >>> urban = ndvi.lt(0.4).And(texture.gt(550))
        
        Multi-scale analysis:
            >>> # Can modify kernel size for different scales
            >>> # (Note: this requires modifying the function)
            >>> # Small kernel (3×3): fine texture
            >>> # Large kernel (15×15): coarse texture
    
    Kernel Size Considerations:
        Radius 5 (11×11 pixels):
            - Neighborhood: ~330m × 330m at 30m resolution
            - Good for: General land cover classification
            - Captures: Medium-scale spatial patterns
            - Trade-off: Balances detail vs computational cost
        
        Alternative sizes (require function modification):
            - Radius 2 (5×5): Fine texture, local variation
            - Radius 10 (21×21): Coarse texture, landscape patterns
    
    Why Green Band?:
        - Sensitive to vegetation structure
        - Less affected by atmospheric scattering than blue
        - Good penetration in vegetation canopy
        - Commonly available across all sensors
        - Used in median composite naming convention
    
    Data Type Considerations:
        - Input converted to int32 for entropy calculation
        - Output implicitly float (entropy is continuous)
        - Scaled by 100 to preserve precision as integer
        - Typical entropy range: 0-8 for 8-bit input
    
    Applications:
        - Forest type classification (natural vs plantation)
        - Urban feature detection
        - Agricultural field boundary delineation
        - Land cover classification enhancement
        - Landscape heterogeneity assessment
        - Habitat complexity mapping
        - Change detection (texture changes)
    
    Performance Considerations:
        - Computationally expensive (neighborhood operations)
        - Larger kernels = more computation time
        - Calculate once per mosaic (not per image)
        - Use with classification algorithms that benefit from texture
    
    Limitations:
        - Sensitive to radiometric resolution
        - May be affected by noise in original data
        - Edge effects near image boundaries
        - Fixed kernel size may not suit all applications
        - Requires 'green_median' band specifically named
    
    Notes:
        - Texture band name hardcoded to 'green_median_texture'
        - Assumes input has 'green_median' from mosaic process
        - Entropy is scale-dependent (kernel size matters)
        - Often used with other texture measures (variance, contrast)
        - Complements spectral information in classifications
    
    Alternative Texture Measures:
        Could be extended to calculate:
        - Variance: Measure of local dispersion
        - Contrast: Difference between highest and lowest values
        - Correlation: Linear dependency of neighboring pixels
        - Homogeneity: Closeness of value distribution
    
    See Also:
        - ee.Image.entropy(): GEE entropy calculation
        - ee.Kernel.square(): Kernel shape definition
        - GLCM texture measures literature
    
    Reference:
        Haralick, R.M., et al. (1973). "Textural Features for Image Classification."
        IEEE Transactions on Systems, Man, and Cybernetics, SMC-3(6), 610-621.
    """
    # Define square kernel with radius 5 (creates 11×11 pixel neighborhood)
    # Total area: 121 pixels at 30m resolution ≈ 0.1 km²
    square = ee.Kernel.square(radius=5)

    # Calculate entropy texture from green median band
    # Steps:
    # 1. Select green_median band (from mosaic percentile compositing)
    # 2. Convert to 32-bit integer (required for entropy calculation)
    # 3. Calculate Shannon entropy within 11×11 neighborhood
    # 4. Multiply by 100 to scale entropy values (e.g., 4.5 → 450)
    # 5. Rename band to indicate it's a texture measure
    entropyG = image.select('green_median')\
        .int32()\
        .entropy(square)\
        .multiply(100)\
        .rename("green_median_texture")

    # Add texture band to input image
    return image.addBands(entropyG)
