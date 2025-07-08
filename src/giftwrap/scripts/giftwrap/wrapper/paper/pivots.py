from ...utils.custom_types.vec import Vec
from dataclasses import dataclass
from ...utils.custom_types.vec import Vec

@dataclass
class Pivot:
    position: Vec
    rotation: Vec

    def __init__(self, position, rotation=Vec(0, 0, 0)):
        self.position = position
        self.rotation = rotation

# Helper function to average two positions
def _avgPos(pos1, pos2):
    return Vec(
        (pos1.x + pos2.x) / 2, (pos1.y + pos2.y) / 2, (pos1.z + pos2.z) / 2
    )

def calculateFoldingPivots(folding_pattern):
    """
    Calculates the positional values for the pivots that control the folding
    plane clusters.

    Args:
        The folding pattern - Containing a list of Fold Points
                              and their positions.

    Returns:
        A dictionary with named Pivot objects:
            { Fold-ID : Pivot(Position, Rotation) }

    Notes:
        Fold IDs are named based on the fold's ordinal number and the outer
        corner(s) of the surface being folded, e.g.
            1_F1_I1 = 1st fold, corners F1 and I1
    """

    half_B = folding_pattern.getSideLength('B') / 2
    D = folding_pattern.getSideLength('D')
    thk = folding_pattern.getPaperThickness()

    temp_pts_2 = {'F1_I1': ('F3', 'I3'),
                  'F8_I8': ('F5', 'I5')}
    temp_pos_2 = {}
    for name, (pt_a, pt_b) in temp_pts_2.items():
        temp_pos_2[name] = _avgPos(folding_pattern.point(pt_a),
                                  folding_pattern.point(pt_b))
        temp_pos_2[name].y += D

    temp_offsets_3 = {'F3': ( half_B, 0,  half_B),
                      'F2': ( half_B, D, -half_B),
                      'I3': (-half_B, 0,  half_B),
                      'I2': (-half_B, D, -half_B),
                      'F5': ( half_B, 0, -half_B),
                      'F6': ( half_B, D,  half_B),
                      'I5': (-half_B, 0, -half_B),
                      'I6': (-half_B, D,  half_B)}
    temp_pos_3 = {}
    for name, (x_offs, y_offs, z_offs) in temp_offsets_3.items():
        pos = folding_pattern.point(name)
        temp_pos_3[name] = Vec(pos.x + x_offs, pos.y + y_offs, pos.z + z_offs)

    temp_pts_4 = {'F3': (('F1', 'G1'), thk),
                  'F2': (('F1', 'G1'), D - thk),
                  'I3': (('F1', 'G1'), thk),
                  'I2': (('F1', 'G1'), D - thk),
                  'F5': (('F1', 'G1'), thk),
                  'F6': (('F1', 'G1'), D - thk),
                  'I5': (('F1', 'G1'), thk),
                  'I6': (('F1', 'G1'), D - thk)}
    temp_pos_4 = {}
    for name, ((pt_a, pt_b), y_offs) in temp_pts_4.items():
        temp_pos_4[name] = _avgPos(folding_pattern.point(pt_a),
                                  folding_pattern.point(pt_b))
        temp_pos_4[name].y += y_offs

    wrap_pivots = {'1_F1_I1': Pivot(_avgPos(folding_pattern.point('F3'),
                                           folding_pattern.point('I3'))),
                   '1_F8_I8': Pivot(_avgPos(folding_pattern.point('F5'),
                                           folding_pattern.point('I5'))),
                   '2_F1_I1': Pivot(temp_pos_2['F1_I1']),
                   '2_F8_I8': Pivot(temp_pos_2['F8_I8']),
                   '3_F8_I8': Pivot(Vec(0, D + thk, 0)),
                   '3_F3':    Pivot(temp_pos_3['F3'], Vec(0,   45,  0)),
                   '3_F2':    Pivot(temp_pos_3['F2'], Vec(0,   225, 0)),
                   '3_F5':    Pivot(temp_pos_3['F5'], Vec(0,   45,  180)),
                   '3_F6':    Pivot(temp_pos_3['F6'], Vec(180, 225, 180)),
                   '3_I3':    Pivot(temp_pos_3['I3'], Vec(0,   -45, 0)),
                   '3_I2':    Pivot(temp_pos_3['I2'], Vec(0,   135, 0)),
                   '3_I5':    Pivot(temp_pos_3['I5'], Vec(180, 225, 0)),
                   '3_I6':    Pivot(temp_pos_3['I6'], Vec(0,   45, 0)),
                   '4_F3':    Pivot(temp_pos_4['F3'], Vec(0,   45,  0)),
                   '4_F2':    Pivot(temp_pos_4['F2'], Vec(0,   225, 0)),
                   '4_F5':    Pivot(temp_pos_4['F5'], Vec(0,   45,  180)),
                   '4_F6':    Pivot(temp_pos_4['F6'], Vec(180, 225, 180)),
                   '4_I3':    Pivot(temp_pos_4['I3'], Vec(0,   -45, 0)),
                   '4_I2':    Pivot(temp_pos_4['I2'], Vec(0,   135, 0)),
                   '4_I5':    Pivot(temp_pos_4['I5'], Vec(180, 225, 0)),
                   '4_I6':    Pivot(temp_pos_4['I6'], Vec(0,   45, 0))}

    return wrap_pivots
