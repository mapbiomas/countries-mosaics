#
import ee

ENDMEMBERS = {
    'landsat-4': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    'landsat-5': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    'landsat-7': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    'landsat-8': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    'landsat-9': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    'sentinel-2 (sr)': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    'sentinel-2 (toa)': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    'sentinel-2 (harmonized)': [
        [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0],
        [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0],
        [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0],
        [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0]
    ],
    'small': [
        [1780, 3370, 4580, 5590, 6830, 6450],  # substrate
        [300, 600, 310, 6690, 2400, 960],  # vegetation
        [190, 100, 50, 70, 30, 20]  # dark
    ]
}

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


def getFractions(image, endmembers):

    outBandNames = ['gv', 'npv', 'soil', 'cloud']

    fractions = ee.Image(image)\
        .select(['blue', 'green', 'red', 'nir', 'swir1', 'swir2'])\
        .unmix(endmembers)\
        .max(0)\
        .multiply(100)\
        .byte()

    fractions = fractions.rename(outBandNames)

    summed = fractions.expression('b("gv") + b("npv") + b("soil")')

    shade = summed\
        .subtract(100)\
        .abs()\
        .byte()\
        .rename(["shade"])

    image = image.addBands(fractions)
    image = image.addBands(shade)

    return image


def getFractionsSmall(image, endmembers):

    outBandNames = ['subs_small', 'veg_small', 'dark_small']

    fractions = ee.Image(image)\
        .select(['blue', 'green', 'red', 'nir', 'swir1', 'swir2'])\
        .unmix(endmembers)\
        .max(0)\
        .multiply(100)\
        .byte()

    fractions = fractions.rename(outBandNames)

    image = image.addBands(fractions)

    return image

def getNDFI(imageFractions):

    summed = imageFractions.expression('b("gv") + b("npv") + b("soil")')

    gvs = imageFractions.select("gv")\
        .divide(summed)\
        .multiply(100)\
        .byte()\
        .rename(["gvs"])

    npvSoil = imageFractions.expression('b("npv") + b("soil")')

    ndfi = ee.Image.cat(gvs, npvSoil)\
        .normalizedDifference()\
        .rename(['ndfi'])

    # rescale NDFI from 0 to 200
    ndfi = ndfi.expression('byte(b("ndfi") * 100 + 100)')

    imageFractions = imageFractions.addBands(gvs)
    imageFractions = imageFractions.addBands(ndfi)

    return imageFractions


def getSEFI(imageFractions):

    summed = imageFractions.expression('b("gv") + b("npv") + b("soil")')
    soil = imageFractions.select(['soil'])
    npv = imageFractions.select(['npv'])
    gv = imageFractions.select(['gv'])
    gvnpv_s = (gv.add(npv).divide(summed)).multiply(100)

    # calculate SEFI
    sefi = ee.Image.cat(gvnpv_s, soil)\
        .normalizedDifference()\
        .rename(['sefi'])

    # rescale SEFI from 0 to 200
    sefi = sefi.expression('byte(b("sefi") * 100 + 100)')

    imageFractions = imageFractions.addBands(sefi)

    return imageFractions


def getWEFI(imageFractions):

    summed = imageFractions.expression('b("gv") + b("npv") + b("soil")')
    soil = imageFractions.select(['soil'])
    npv = imageFractions.select(['npv'])
    gv = imageFractions.select(['gv'])
    shd = summed.subtract(100).abs().byte()
    gvnpv = gv.add(npv)
    soilshade = soil.add(shd)

    # calculate WEFI
    wefi = ee.Image.cat(gvnpv, soilshade)\
        .normalizedDifference()\
        .rename(['wefi'])

    # rescale WEFI from 0 to 200
    wefi = wefi.expression('byte(b("wefi") * 100 + 100)')

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
