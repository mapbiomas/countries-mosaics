import ee

LANDSAT_NEW_NAMES = [
    'blue',
    'green',
    'red',
    'nir',
    'swir1',
    'swir2',
    'pixel_qa',
    'tir'
]

SENTINEL_NEW_NAMES = [
    'blue',
    'green',
    'red',
    'red_edge_1',
    'nir',
    'swir1',
    'swir2',
    'pixel_qa'
]

BAND_NAMES = {
    'l4c2': {
        'bandNames': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'QA_PIXEL', 'ST_B6'],
        'newNames': LANDSAT_NEW_NAMES
    },
    'l5c2': {
        'bandNames': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'QA_PIXEL', 'ST_B6'],
        'newNames': LANDSAT_NEW_NAMES
    },
    'l7c2': {
        'bandNames': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'QA_PIXEL', 'ST_B6'],
        'newNames': LANDSAT_NEW_NAMES
    },
    'l8c2': {
        'bandNames': ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'QA_PIXEL', 'ST_B10'],
        'newNames': LANDSAT_NEW_NAMES
    },
    'l9c2': {
        'bandNames': ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'QA_PIXEL', 'ST_B10'],
        'newNames': LANDSAT_NEW_NAMES
    },

    'l4c2toa': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'QA_PIXEL', 'B6'],
        'newNames': LANDSAT_NEW_NAMES
    },
    'l5c2toa': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'QA_PIXEL', 'B6'],
        'newNames': LANDSAT_NEW_NAMES
    },
    'l7c2toa': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'QA_PIXEL', 'B6_VCID_1'],
        'newNames': LANDSAT_NEW_NAMES
    },
    'l8c2toa': {
        'bandNames': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'QA_PIXEL', 'B10'],
        'newNames': LANDSAT_NEW_NAMES
    },

    'l5': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa', 'B6'],
        'newNames': LANDSAT_NEW_NAMES
    },
    'l7': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa', 'B6'],
        'newNames': LANDSAT_NEW_NAMES
    },
    'l8': {
        'bandNames': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa', 'B11'],
        'newNames': LANDSAT_NEW_NAMES
    },
    'l5toa': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'BQA', 'B6'],
        'newNames': LANDSAT_NEW_NAMES
    },
    'l7toa': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'BQA', 'B6_VCID_1'],
        'newNames': LANDSAT_NEW_NAMES
    },
    'l8toa': {
        'bandNames': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'BQA', 'B11'],
        'newNames': LANDSAT_NEW_NAMES
    },
    'sentinel-2 (toa)': {
        'bandNames': ['B2', 'B3', 'B4', 'B5', 'B8', 'B11', 'B12', 'QA60'],
        'newNames': SENTINEL_NEW_NAMES
    },
    's2': {
        'bandNames': ['B2', 'B3', 'B4', 'B5', 'B8', 'B11', 'B12', 'QA60'],
        'newNames': SENTINEL_NEW_NAMES
    },
    's2_harmonized': {
        'bandNames': [
            'B2',
            'B3',
            'B4',
            'B5',
            'B6',
            'B7',
            'B8',
            'B8A',
            'B11',
            'B12',
            'QA60'
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
            'pixel_qa']
    },
    'l5_urban': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa', 'B6', 'B4_1', 'B5_1', 'B6_1'],
        'newNames': LANDSAT_NEW_NAMES + ['swir1_dn', 'nir_dn', 'tir_dn']
    },
    'l7_urban': {
        'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa', 'B6', 'B4_1', 'B5_1', 'B6_VCID_2'],
        'newNames': LANDSAT_NEW_NAMES + ['swir1_dn', 'nir_dn', 'tir_dn']
    },
    'l8_urban': {
        'bandNames': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa', 'B11', 'B5_1', 'B6_1', 'B11_1'],
        'newNames': LANDSAT_NEW_NAMES + ['swir1_dn', 'nir_dn', 'tir_dn']
    },
}


def getBandNames(key):
    """Create a new list of names for bands

    Parameters:
        key (str): Key indicating the collection name

    Returns:
        dictionary: A dictionry containing the input band names and
            the new band names
    """
    return BAND_NAMES[key]
