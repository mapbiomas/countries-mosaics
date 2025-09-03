#
import ee


def getNDVI(image):

    exp = '( b("nir") - b("red") ) / ( b("nir") + b("red") )'

    ndvi = image.expression(exp)\
        .rename(["ndvi"])\
        .add(1)

    return image.addBands(srcImg=ndvi, overwrite=True)


def getNDBI(image):

    exp = '( b("swir1") - b("nir") ) / ( b("swir1") + b("nir") )'

    ndbi = image.expression(exp)\
        .rename(["ndbi"])\
        .add(1)

    return image.addBands(srcImg=ndbi, overwrite=True)


def getUI(image):

    exp = '( b("swir2") - b("nir") ) / ( b("swir2") + b("nir") )'

    ui = image.expression(exp)\
        .rename(["ui"])\
        .add(1)

    return image.addBands(srcImg=ui, overwrite=True)


def getBU(image):
    
    exp = 'b("ndbi") - b("ndvi")'

    bu = image.expression(exp)\
        .rename(["bu"])

    return image.addBands(srcImg=bu, overwrite=True)


def getEBBI(image):
    
    # exp = '( b("swir1") - b("nir") ) / ( 0.1 * sqrt(b("swir1") + b("tir")) )'
    exp = '( b("swir1_dn") - b("nir_dn") ) / ( 10 * sqrt(b("swir1_dn") + b("tir_dn")) )'

    ebbi = image.expression(exp)\
        .rename(["ebbi"])

    return image.addBands(srcImg=ebbi, overwrite=True)

def getNDWI(image):

    exp = 'float(b("nir") - b("swir1"))/(b("nir") + b("swir1"))'

    ndwi = image.expression(exp)\
        .rename(["ndwi"])\
        .add(1)

    return image.addBands(srcImg=ndwi, overwrite=True)


def getMNDWI(image):

    exp = 'float(b("green") - b("swir1"))/(b("green") + b("swir1"))'

    mndwi = image.expression(exp)\
        .rename(["mndwi"])\
        .add(1)

    return image.addBands(srcImg=mndwi, overwrite=True)


def getSAVI(image):

    exp = '1.5 * (b("nir") - b("red")) / (0.5 + b("nir") + b("red"))'

    savi = image.expression(exp)\
        .rename(["savi"])\
        .add(1)

    return image.addBands(srcImg=savi, overwrite=True)


def getPRI(image):

    exp = 'float(b("blue") - b("green"))/(b("blue") + b("green"))'

    pri = image.expression(exp)\
        .rename(["pri"])\
        .add(1)

    return image.addBands(srcImg=pri, overwrite=True)


def getCAI(image):

    exp = 'float( b("swir2") / b("swir1") )'

    cai = image.expression(exp)\
        .rename(["cai"])\
        .add(1)

    return image.addBands(srcImg=cai, overwrite=True)


def getEVI(image):

    exp = '2.5 * ((b("nir") - b("red")) / (b("nir") + 6 * b("red") - 7.5 * b("blue") + 1))'

    evi = image.expression(exp)\
        .rename(["evi"])\
        .add(1)

    return image.addBands(srcImg=evi, overwrite=True)


def getEVI2(image):

    exp = '2.5 * (b("nir") - b("red")) / (b("nir") + (2.4 * b("red")) + 1)'

    evi2 = image.expression(exp)\
        .rename(["evi2"])\
        .add(1)

    return image.addBands(srcImg=evi2, overwrite=True)


def getHallCover(image):

    exp = '( (-b("red") * 0.017) - (b("nir") * 0.007) - (b("swir2") * 0.079) + 5.22 )'

    hallcover = image.expression(exp)\
        .exp()\
        .rename(["hallcover"])

    return image.addBands(hallcover)


def getHallHeigth(image):

    exp = '( (-b("red") * 0.039) - (b("nir") * 0.011) - (b("swir1") * 0.026) + 4.13 )'

    hallheigth = image.expression(exp)\
        .exp()\
        .rename(["hallheigth"])

    return image.addBands(hallheigth)


def getGCVI(image):

    exp = 'b("nir") / b("green") - 1'

    gcvi = image.expression(exp)\
        .rename(["gcvi"])\
        .add(1)

    return image.addBands(gcvi)
