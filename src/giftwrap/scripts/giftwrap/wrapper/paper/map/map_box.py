from .map_help import _generateRowVertexMappings, _generateVertexMappings

_BOX_MAPPINGS = {
    # F1 - I1
    'F1': 0, 'F1u': 1, 'G1': 2, 'H1': 3, 'I1u': 4, 'I1': 5,
    'F1a': 6, 'I1a': 7,
    'F1xs': 8, 'I1xs': 9,
    'F1s': 10, 'F1xd': 11, 'F1d': 12, 'I1d': 13, 'I1xd': 14, 'I1s': 15,
    # F2 - I2
    'F2': 16, 'F2x': 17, 'G2': 18, 'H2': 19, 'I2x': 20, 'I2': 21,
    'G2o': 22, 'H2o': 23,
    'G3o': 24, 'H3o': 25,
    # F3 - I3
    'F3': 26, 'F3x': 27, 'G3': 28, 'H3': 29, 'I3x': 30, 'I3': 31,
    # F4 - I4
    'F4us': 32, 'F4xu': 33, 'F4u': 34, 'I4u': 35, 'I4xu': 36, 'I4us': 37,
    'F4xus': 38, 'I4xus': 39,
    'F4a': 40, 'I4a': 41,
    'F4b': 42, 'I4b': 43,
    'F4xds': 44, 'I4xds': 45,
    'F4ds': 46, 'F4xd': 47, 'F4d': 48, 'I4d': 49, 'I4xd': 50, 'I4ds': 51,
    # F5 - I5
    'F5': 52, 'F5x': 53, 'G5': 54, 'H5': 55, 'I5x': 56, 'I5': 57,
    'G5o': 58, 'H5o': 59,
    'G6o': 60, 'H6o': 61,
    # F6 - I6
    'F6': 62, 'F6x': 63, 'G6': 64, 'H6': 65, 'I6x': 66, 'I6': 67,
    # F7 - I7
    'F7s': 68, 'F7xu': 69, 'F7u': 70, 'I7u': 71, 'I7xu': 72, 'I7s': 73,
    'F7xs': 74, 'I7xs': 75,
    'F7a': 76, 'I7a': 77,
    'F7': 78, 'F7m': 79, 'G7': 80, 'H7': 81, 'I7m': 82, 'I7': 83,
    # F8 - I8
    'F8': 84, 'F8d': 85, 'G8': 86, 'H8': 87, 'I8d': 88, 'I8': 89
}

_BOX_ROW_START_END_IDS = (
    ('F1', 'I1'),    # Row 1
    ('F2', 'I2'),    # Row 2
    ('F3', 'I3'),    # Row 3
    ('F4a', 'I4b'),  # Row 4
    ('F5', 'I5'),    # Row 5
    ('F6', 'I6'),    # Row 6
    ('F7', 'I7'),    # Row 7
    ('F8', 'I8'),    # Row 8
)
_BOX_ROW_VERTICES, _BOX_IN_BETWEEN_ROWS_VERTICES = \
    _generateRowVertexMappings(_BOX_MAPPINGS, _BOX_ROW_START_END_IDS)

_BOX_DIAGONAL_FOLD_IDS = {
    'F2 pad': ['F1xs', 'F1s', 'F1xd', 'F2', 'F2x'],
    'F2':     ['F1s', 'F2'],
    'I2 pad': ['I1xs', 'I1s', 'I1xd', 'I2', 'I2x'],
    'I2':     ['I1s', 'I2'],
    'F3 pad': ['F3', 'F3x', 'F4us', 'F4xu', 'F4xus'],
    'F3':     ['F3', 'F4us'],
    'I3 pad': ['I3', 'I3x', 'I4us', 'I4xu', 'I4xus'],
    'I3':     ['I3', 'I4us'],
    'F5 pad': ['F5', 'F5x', 'F4ds', 'F4xd', 'F4xds'],
    'F5':     ['F5', 'F4ds'],
    'I5 pad': ['I5', 'I5x', 'I4ds', 'I4xd', 'I4xds'],
    'I5':     ['I5', 'I4ds'],
    'F6 pad': ['F6', 'F6x', 'F7s', 'F7xu', 'F7xs'],
    'F6':     ['F6', 'F7xs'],
    'I6 pad': ['I6', 'I6x', 'I7s', 'I7xu', 'I7xs'],
    'I6':     ['I6', 'I7xs'],
}

_BOX_DIAGONAL_FOLD_VERTICES = \
    _generateVertexMappings(_BOX_MAPPINGS, _BOX_DIAGONAL_FOLD_IDS)

