from .map_help import _generateRowVertexMappings

_BOX_OVERLAP_MAPPINGS = {
    # F1 - I1
    'F1': 0, 'F1c': 1, 'F1u': 2, 'G1': 3, 'H1': 4, 'I1u': 5, 'I1c': 6, 'I1': 7,
    'F1xs': 8, 'I1xs': 9,
    'F1a': 10, 'I1a': 11,
    'F1xm': 12, 'I1xm': 13,
    'F1b': 14, 'I1b': 15,
    'F1s': 16, 'F1xd': 17, 'F1d': 18, 'I1d': 19, 'I1xd': 20, 'I1s': 21,
    # F2 - I2
    'F2': 22, 'F2x': 23, 'G2': 24, 'H2': 25, 'I2x': 26, 'I2': 27,
    'G2o': 28, 'H2o': 29,
    # F3 - I3
    'G3o': 30, 'H3o': 31,
    'F3': 32, 'F3x': 33, 'G3': 34, 'H3': 35, 'I3x': 36, 'I3': 37,
    # F4 - I4
    'F4us': 38, 'F4xu': 39, 'F4u': 40, 'I4u': 41, 'I4xu': 42, 'I4us': 43,
    'F4b': 44, 'I4b': 45,
    'F4xus': 46, 'F4y': 47, 'I4y': 48, 'I4xus': 49,
    'F4x': 50, 'FG4': 51, 'HI4': 52, 'I4x': 53,
    'F4xds': 54, 'F4z': 55, 'I4z': 56, 'I4xds': 57,
    'F4a': 58, 'I4a': 59,
    'F4ds': 60, 'F4xd': 61, 'F4d': 62, 'I4d': 63, 'I4xd': 64, 'I4ds': 65,
    # F5 - I5
    'F5': 66, 'F5x': 67, 'G5': 68, 'H5': 69, 'I5x': 70, 'I5': 71,
    'G5o': 72, 'H5o': 73,
    # F6 - I6
    'G6o': 74, 'H6o': 75,
    'F6': 76, 'F6x': 77, 'G6': 78, 'H6': 79, 'I6x': 80, 'I6': 81,
    # F7 - I7
    'F7s': 82, 'F7xu': 83, 'F7u': 84, 'I7u': 85, 'I7xu': 86, 'I7s': 87,
    'F7b': 88, 'I7b': 89,
    'F7xm': 90, 'I7xm': 91,
    'F7': 92, 'F7xd': 93, 'F7a': 94, 'F7d': 95,
    'G7': 96, 'H7': 97,
    'I7d': 98, 'I7a': 99, 'I7xd': 100, 'I7': 101,
}

_BOX_OVERLAP_ROW_START_END_ID = (
    ('F1', 'I1'),     # Row 1
    ('F2', 'I2'),     # Row 2
    ('F3', 'I3'),     # Row 3
    ('F4x', 'I4x'),   # Row 4
    ('F5', 'I5'),     # Row 5
    ('F6', 'I6'),     # Row 6
    ('F7', 'I7'),     # Row 7
)

_BOX_OVERLAP_ROW_VERTICES, _BOX_OVERLAP_IN_BETWEEN_ROWS_VERTICES = \
    _generateRowVertexMappings(_BOX_OVERLAP_MAPPINGS,
                               _BOX_OVERLAP_ROW_START_END_ID)
