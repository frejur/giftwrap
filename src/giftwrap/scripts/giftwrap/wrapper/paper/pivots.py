from ...utils.custom_types.vec import Vec

def calculateFoldingPivots(folding_pattern):
    """
    Calculates the positional values for the pivots that control the folding
    plane clusters.

    Args:
        The folding pattern - Containing a list of Fold Points
                              and their positions.

    Returns:
        A dictionary with the format { Pivot-ID : Vec, }

    Notes:
        Pivot IDs are named based on the quadrant and the fold ordinal, e.g.
            1U = 1st fold, upper quadrant
    """

    # Helper function to average two positions
    def avgPos(pos1, pos2):
        return Vec(
            (pos1.x + pos2.x) / 2, (pos1.y + pos2.y) / 2, (pos1.z + pos2.z) / 2
        )

    # Helper function to copy a position
    def cpPos(pos):
        return Vec(pos.x, pos.y, pos.z)

    temp_I3_H3 = (folding_pattern.point('I3').x -
                  folding_pattern.point('H3').x) / 2
    temp_1U = avgPos(folding_pattern.point('I3'), folding_pattern.point('F3'))
    temp_2U = cpPos(temp_1U)
    temp_2U.y += (folding_pattern.point('F2').z -
                  folding_pattern.point('F3').z) * -1
    temp_2B = cpPos(temp_2U)
    temp_2B.z *= -1
    temp_3UR = cpPos(folding_pattern.point('H3'))
    temp_3UR.x += temp_I3_H3
    temp_3UR.z += temp_I3_H3
    temp_3BR = cpPos(folding_pattern.point('H5'))
    temp_3BR.x += temp_I3_H3
    temp_3BR.z -= temp_I3_H3
    temp_3UL = cpPos(folding_pattern.point('G3'))
    temp_3UL.x -= temp_I3_H3
    temp_3UL.z += temp_I3_H3
    temp_3BL = cpPos(folding_pattern.point('G5'))
    temp_3BL.x -= temp_I3_H3
    temp_3BL.z -= temp_I3_H3
    temp_4UR = cpPos(temp_3UR)
    temp_4UR.y = temp_2U.y
    temp_4BR = cpPos(temp_3BR)
    temp_4BR.y = temp_2U.y
    temp_4UL = cpPos(temp_3UL)
    temp_4UL.y = temp_2U.y
    temp_4BL = cpPos(temp_3BL)
    temp_4BL.y = temp_2U.y
    temp_5R = cpPos(folding_pattern.point('H4'))
    temp_5R.y = temp_2U.y
    temp_5L = cpPos(folding_pattern.point('G4'))
    temp_5L.y = temp_2U.y
    temp_6R = cpPos(folding_pattern.point('H4'))
    temp_6R.x = folding_pattern.point('I4u').x
    temp_6L = cpPos(folding_pattern.point('G4'))
    temp_6L.x = folding_pattern.point('F4u').x
    wrap_pivots = {'1U': temp_1U,
                   '1B': avgPos(folding_pattern.point('I5'),
                                folding_pattern.point('F5')),
                   '2U': temp_2U, '2B': temp_2B,
                   '3UR': temp_3UR, '3BR': temp_3BR, '3UL': temp_3UL,
                   '3BL': temp_3BL,
                   '4UR': temp_4UR, '4BR': temp_4BR, '4UL': temp_4UL,
                   '4BL': temp_4BL,
                   '5R': temp_5R, '5L': temp_5L,
                   '6R': temp_6R, '6L': temp_6L,}

    return wrap_pivots
