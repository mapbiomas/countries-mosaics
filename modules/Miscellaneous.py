import ee
#
#
#
def getSlope(image):

    terrain = ee.Image("JAXA/ALOS/AW3D30_V1_1").select("AVE")

    slope = ee.Terrain.slope(terrain)\
        .multiply(100)\
        .int16()\
        .rename('slope')

    return image.addBands(slope)

#
#
#
def getEntropyG(image):

    """Calculate textG
    
    Parameters:
        image (ee.Image): image containing the Green band:
        
    Returns:
        ee.Image:  image with textG band
    """
    square = ee.Kernel.square(radius=5)

    entropyG = image.select('green_median')\
        .int32()\
        .entropy(square)\
        .multiply(100)\
        .rename("green_median_texture")

    return image.addBands(entropyG)
