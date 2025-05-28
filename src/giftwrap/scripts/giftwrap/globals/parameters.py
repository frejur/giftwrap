"""
Parameter names and values.
"""

from enum import Enum, auto

# ==============================================================================
# Enums
# ==============================================================================

class Parm(Enum):
    WRAPPER_MODE      = auto()
    WRAPPER_ID        = auto()
    OBJECT_NAME       = auto()
    PAPER_THICKNESS   = auto()
    PAPER_USE_PLANE   = auto()
    PAPER_COLOR       = auto()
    RIBBON_THICKNESS  = auto()
    RIBBON_WIDTH      = auto()
    RIBBON_COLOR      = auto()
    ANIM_START_FRAME  = auto()
    ANIM_END_FRAME    = auto()
    ANIMATE_PLACEMENT = auto()
    ANIMATE_GIFT_FLIP = auto()
    WRAP_BUTTON       = auto()
    KEEP_ORIGINAL     = auto()
    COORDINATE_SPACE  = auto()
    UP_AXIS           = auto()
    INVERT_UP_AXIS    = auto()
    AUTO_PLACE_OBJECT = auto()
    KNOT_PLACEMENT    = auto()

class P_Opt(Enum):
    CREATE_WRAPPER          = auto()
    EDIT_WRAPPER            = auto()
    USE_WORLD_SPACE         = auto()
    USE_OBJECT_SPACE        = auto()
    USE_X_UP                = auto()
    USE_Y_UP                = auto()
    USE_Z_UP                = auto()
    USE_LARGEST_SIDE_UP     = auto()
    PLACE_LARGEST_SIDE_DOWN = auto()
    PLACE_AS_IS             = auto()
    TIE_KNOT_AT_TOP         = auto()
    TIE_KNOT_AT_BOTTOM      = auto()
    COLOR_RANDOM            = auto()
    COLOR_RED               = auto()
    COLOR_GREEN             = auto()
    COLOR_BLUE              = auto()
    COLOR_YELLOW            = auto()
    COLOR_BLACK             = auto()
    COLOR_WHITE             = auto()

class P_Attr(Enum):
    MIN_VALUE     = auto()
    MAX_VALUE     = auto()
    DEFAULT_VALUE = auto()
    DESCRIPTION   = auto()
    CONTROL_LABEL = auto()
    COLUMN_LABEL  = auto()
    MIN_LENGTH    = auto()
    MAX_LENGTH    = auto()
    CONTROL_TYPE  = auto()
    OPTIONS       = auto()

class Ctrl_Type(Enum):
    CHECKBOX     = auto()
    INT_SLIDER   = auto()
    INT_FIELD    = auto()
    FLOAT_SLIDER = auto()
    OPTION_MENU  = auto()
    TEXT_INPUT   = auto()

# ==============================================================================
# Notes
# ==============================================================================

LEGACY_COLORS_NOTE = ('NOTE: The colors are a legacy option.\n'
                      'A set of very basic shaders with different colors\n'
                      'are set up and assigned to the different meshes.\n'
                      'This color information will NOT be exported.')

# ==============================================================================
# Parameter Attributes
# ==============================================================================

ATTR = {
    Parm.WRAPPER_MODE: {
        P_Attr.DEFAULT_VALUE: P_Opt.CREATE_WRAPPER,
    },
    Parm.WRAPPER_ID: {
        P_Attr.DESCRIPTION:  'Wrapper ID',
        P_Attr.COLUMN_LABEL: 'ID'
    },
    Parm.OBJECT_NAME: {
        P_Attr.DESCRIPTION:  'Name of original object',
        P_Attr.COLUMN_LABEL: 'Object',
    },
    Parm.PAPER_THICKNESS: {
        P_Attr.DESCRIPTION:   'Paper thickness',
        P_Attr.CONTROL_LABEL: 'Thickness',
        P_Attr.COLUMN_LABEL:  'P. weight',
        P_Attr.MIN_VALUE:     0.005,
        P_Attr.MAX_VALUE:     0.05,
        P_Attr.DEFAULT_VALUE: 0.02,
        P_Attr.CONTROL_TYPE:  Ctrl_Type.FLOAT_SLIDER
    },
    Parm.PAPER_USE_PLANE: {
        P_Attr.DESCRIPTION:   'Use a simple plane for the Paper mesh',
        P_Attr.CONTROL_LABEL: 'Plane Only',
        P_Attr.COLUMN_LABEL:  'Use plane',
        P_Attr.DEFAULT_VALUE: False,
        P_Attr.CONTROL_TYPE:  Ctrl_Type.CHECKBOX
    },
    Parm.RIBBON_THICKNESS: {
        P_Attr.DESCRIPTION:   'Ribbon thickness',
        P_Attr.CONTROL_LABEL: 'Thickness',
        P_Attr.COLUMN_LABEL:  'R. thickness',
        P_Attr.MIN_VALUE:     0.1,
        P_Attr.MAX_VALUE:     2.0,
        P_Attr.DEFAULT_VALUE: 1.0,
        P_Attr.CONTROL_TYPE:  Ctrl_Type.FLOAT_SLIDER
    },
    Parm.RIBBON_WIDTH: {
        P_Attr.DESCRIPTION:   'Ribbon width',
        P_Attr.CONTROL_LABEL: 'Width',
        P_Attr.COLUMN_LABEL:  'R. width',
        P_Attr.MIN_VALUE:     2.5,
        P_Attr.MAX_VALUE:     5.0,
        P_Attr.DEFAULT_VALUE: 4.0,
        P_Attr.CONTROL_TYPE:  Ctrl_Type.FLOAT_SLIDER
    },
    Parm.ANIM_START_FRAME: {
        P_Attr.DESCRIPTION: 'Animation start frame',
        P_Attr.COLUMN_LABEL: 'Start',
        P_Attr.MIN_VALUE: -2048,
        P_Attr.MAX_VALUE: 2048,
        P_Attr.DEFAULT_VALUE: 1,
        P_Attr.CONTROL_TYPE: Ctrl_Type.INT_FIELD,
    },
    Parm.ANIM_END_FRAME: {
        P_Attr.DESCRIPTION: 'Animation end frame',
        P_Attr.COLUMN_LABEL: 'End',
        P_Attr.MIN_VALUE: -2048,
        P_Attr.MAX_VALUE: 2048,
        P_Attr.DEFAULT_VALUE: 100,
        P_Attr.CONTROL_TYPE: Ctrl_Type.INT_FIELD,
    },
    Parm.ANIMATE_PLACEMENT: {
        P_Attr.DESCRIPTION:   'If the object is reoriented and placed with\n'
                              'its largest side facing down, this motion will\n'
                              'be included in the animation.',
        P_Attr.CONTROL_LABEL: 'Animate placement',
        P_Attr.COLUMN_LABEL:  'Anim. Placemt',
        P_Attr.DEFAULT_VALUE: True,
        P_Attr.CONTROL_TYPE:  Ctrl_Type.CHECKBOX
    },
    Parm.ANIMATE_GIFT_FLIP: {
        P_Attr.DESCRIPTION:   'Flips the gift around before tying the ribbon\n'
                              'and includes this motion in the animation.',
        P_Attr.CONTROL_LABEL: 'Animate gift flip',
        P_Attr.COLUMN_LABEL:  'Anim. Flip',
        P_Attr.DEFAULT_VALUE: True,
        P_Attr.CONTROL_TYPE:  Ctrl_Type.CHECKBOX
    },
    Parm.WRAP_BUTTON: {
        P_Attr.DESCRIPTION:   'Wraps the selected object(s)',
        P_Attr.CONTROL_LABEL: 'Wrap'
    },
    Parm.KEEP_ORIGINAL: {
        P_Attr.DESCRIPTION:   'Duplicates and keeps a copy of the original\n'
                              'object(s) before wrapping',
        P_Attr.CONTROL_LABEL: 'Keep original',
        P_Attr.DEFAULT_VALUE: True
    },
    Parm.COORDINATE_SPACE: {
        P_Attr.DESCRIPTION:   'Choose to align the wrapper to the object\'s\n'
                              'rotational pivot or to world space',
        P_Attr.CONTROL_LABEL: 'Space',
        P_Attr.COLUMN_LABEL:  'Space',
        P_Attr.DEFAULT_VALUE: 2, # NOTE: 1-indexed
        P_Attr.CONTROL_TYPE:  Ctrl_Type.OPTION_MENU,
        P_Attr.OPTIONS:       (P_Opt.USE_WORLD_SPACE, P_Opt.USE_OBJECT_SPACE)
    },
    Parm.UP_AXIS: {
        P_Attr.DESCRIPTION:   'Up/down axis. X, Y, Z or dynamically determine\n'
                              'and use the axis that has the largest side\n'
                              'of the object\'s bounding box facing up/down.',
        P_Attr.CONTROL_LABEL: 'Up',
        P_Attr.COLUMN_LABEL:  'Up',
        P_Attr.DEFAULT_VALUE: 2,  # NOTE: 1-indexed
        P_Attr.CONTROL_TYPE:  Ctrl_Type.OPTION_MENU,
        P_Attr.OPTIONS:       (P_Opt.USE_X_UP,
                               P_Opt.USE_Y_UP,
                               P_Opt.USE_Z_UP,
                               P_Opt.USE_LARGEST_SIDE_UP)
    },
    Parm.INVERT_UP_AXIS: {
        P_Attr.DESCRIPTION:   'Invert the Up Axis',
        P_Attr.CONTROL_LABEL: 'Invert',
        P_Attr.COLUMN_LABEL:  'Inv. Up',
        P_Attr.CONTROL_TYPE:  Ctrl_Type.CHECKBOX,
        P_Attr.DEFAULT_VALUE: False
    },
    Parm.AUTO_PLACE_OBJECT: {
        P_Attr.DESCRIPTION:   'Automatically reorient the object with its\n'
                              'largest side facing down before wrapping,\n'
                              'or maintain the current object placement.',
        P_Attr.CONTROL_LABEL: 'Place obj',
        P_Attr.COLUMN_LABEL:  'Obj placemt',
        P_Attr.DEFAULT_VALUE: 1,  # NOTE: 1-indexed
        P_Attr.CONTROL_TYPE: Ctrl_Type.OPTION_MENU,
        P_Attr.OPTIONS: (P_Opt.PLACE_LARGEST_SIDE_DOWN, P_Opt.PLACE_AS_IS)
    },
    Parm.KNOT_PLACEMENT: {
        P_Attr.DESCRIPTION: 'Choose on which side of the gift to tie the knot',
        P_Attr.CONTROL_LABEL: 'Knot',
        P_Attr.COLUMN_LABEL: 'Knot',
        P_Attr.DEFAULT_VALUE: 1,  # NOTE: 1-indexed
        P_Attr.CONTROL_TYPE: Ctrl_Type.OPTION_MENU,
        P_Attr.OPTIONS: (P_Opt.TIE_KNOT_AT_TOP, P_Opt.TIE_KNOT_AT_BOTTOM)
    },
    Parm.PAPER_COLOR: {
        P_Attr.DESCRIPTION: 'The color of the paper mesh.\n' +
                            LEGACY_COLORS_NOTE,
        P_Attr.CONTROL_LABEL: 'Paper Color',
        P_Attr.COLUMN_LABEL: 'P. Color',
        P_Attr.DEFAULT_VALUE: 1,  # NOTE: 1-indexed
        P_Attr.CONTROL_TYPE: Ctrl_Type.OPTION_MENU,
        P_Attr.OPTIONS: (P_Opt.COLOR_RANDOM,
                         P_Opt.COLOR_RED,
                         P_Opt.COLOR_GREEN,
                         P_Opt.COLOR_BLUE,
                         P_Opt.COLOR_YELLOW,
                         P_Opt.COLOR_BLACK,
                         P_Opt.COLOR_WHITE)
    },
    Parm.RIBBON_COLOR: {
        P_Attr.DESCRIPTION: 'The color of the ribbon surface.\n' +
                            LEGACY_COLORS_NOTE,
        P_Attr.CONTROL_LABEL: 'Ribbon Color',
        P_Attr.COLUMN_LABEL: 'R. Color',
        P_Attr.DEFAULT_VALUE: 1,  # NOTE: 1-indexed
        P_Attr.CONTROL_TYPE: Ctrl_Type.OPTION_MENU,
        P_Attr.OPTIONS: (P_Opt.COLOR_RANDOM,
                         P_Opt.COLOR_RED,
                         P_Opt.COLOR_GREEN,
                         P_Opt.COLOR_BLUE,
                         P_Opt.COLOR_YELLOW)
    },
}

# ==============================================================================
# Option menu options
# ==============================================================================

OPT = {
    P_Opt.USE_WORLD_SPACE         : 'World',
    P_Opt.USE_OBJECT_SPACE        : 'Object',
    P_Opt.USE_X_UP                : 'X',
    P_Opt.USE_Y_UP                : 'Y',
    P_Opt.USE_Z_UP                : 'Z',
    P_Opt.USE_LARGEST_SIDE_UP     : 'Largest side',
    P_Opt.PLACE_LARGEST_SIDE_DOWN : 'Largest side down',
    P_Opt.PLACE_AS_IS             : 'As is',
    P_Opt.TIE_KNOT_AT_TOP         : 'Top',
    P_Opt.TIE_KNOT_AT_BOTTOM      : 'Bottom',
    P_Opt.COLOR_RANDOM            : 'Random',
    P_Opt.COLOR_RED               : 'Red',
    P_Opt.COLOR_GREEN             : 'Green',
    P_Opt.COLOR_BLUE              : 'Blue',
    P_Opt.COLOR_YELLOW            : 'Yellow',
    P_Opt.COLOR_BLACK             : 'Black',
    P_Opt.COLOR_WHITE             : 'White',
}
