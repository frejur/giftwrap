import maya.cmds as cmds
from enum import Enum, auto
import string
import random

from enum import Enum, auto

from .paper import *
from .dummy import *
from .anchor import *
from .ribbon import *
from .ctrl import *

from .wrapper_constants import *
from ..globals.parameters import *
from ..utils.bbox import *
from ..utils.bbox.bbox_helpers import (
    determine_smallest_and_largest_bbox_side,
    BboxFacePair
)

class Underside(Enum):
    LEFT   = auto()
    BOTTOM = auto()
    BACK   = auto()

class Wrapper():
    """
    Wrap object in wrapping paper, create a control handle.
    The animation is driven by the control handle attribute.

    Note: Just ignore this warning when animating the ribbon:
     '(Extrude): invalid path curve'
    """
    def __init__(self, object_name, **kwargs):
        if  not cmds.objExists(object_name):
            raise ValueError(f'Node "{object_name}" does not exist')

        # Link internal member names to parameter enums
        parms = {
            'mode':             Parm.WRAPPER_MODE,
            'paper_thickness':  Parm.PAPER_THICKNESS,
            'use_plane':        Parm.PAPER_USE_PLANE,
            'paper_color':      Parm.PAPER_COLOR,
            'ribbon_width':     Parm.RIBBON_WIDTH,
            'ribbon_thickness': Parm.RIBBON_THICKNESS,
            'ribbon_color':     Parm.RIBBON_COLOR,
            'anim_s':           Parm.ANIM_START_FRAME,
            'anim_e':           Parm.ANIM_END_FRAME,
            'anim_placemt':     Parm.ANIMATE_PLACEMENT,
            'anim_flip':        Parm.ANIMATE_GIFT_FLIP,
            'keep_original':    Parm.KEEP_ORIGINAL,
            'cspace':           Parm.COORDINATE_SPACE,
            'up_axis_mode':     Parm.UP_AXIS,
            'inv_up':           Parm.INVERT_UP_AXIS,
            'auto_place_opt':   Parm.AUTO_PLACE_OBJECT,
            'knot_placemt':     Parm.KNOT_PLACEMENT,
        }

        # Validate and fetch default values using global parameter list
        # -> Store in member variables.
        for name, p_id in parms.items():
            value = None

            p_id_string = p_id.name.lower()
            if (p_id in ATTR and P_Attr.CONTROL_TYPE in ATTR[p_id]):
                value = kwargs.get(p_id_string, _default_value(p_id))

                if (ATTR[p_id][P_Attr.CONTROL_TYPE] in (Ctrl_Type.INT_FIELD,
                                                        Ctrl_Type.FLOAT_SLIDER)
                ):
                    _validate_within_min_max(p_id, value)
            else:
                value = kwargs.get(p_id_string, None)

            setattr(self, name, value)

        # Disable auto placement when dynamic up axis is active
        self.dynamic_up_axis = (
                self.up_axis_mode == OPT[P_Opt.USE_LARGEST_SIDE_UP]
        )
        self.auto_place = (self.dynamic_up_axis == False and
                           self.auto_place_opt != OPT[P_Opt.PLACE_AS_IS])

        # Set paper thickness to zero if using plane
        self.paper_thickness = 0 if self.use_plane else self.paper_thickness

        # Setup ID and object properties
        self.wrap_id = self.idGenerator(size=5)
        self.original_object = object_name
        self.object = (
            cmds.duplicate(object_name,
                           name=f'object_copy_{self.wrap_id}_geo')[0]
            if self.keep_original
            else object_name)

        # Dummy
        self.dummy_world = WrapDummy(self.object, self.wrap_id, BboxSpace.WORLD)
        self.dummy_object = WrapDummy(self.object, self.wrap_id, BboxSpace.OBJECT)
        self.dummy_group = cmds.group(n=f'dummy_{self.wrap_id}_grp',
                                      empty=True)
        cmds.parent([self.dummy_world.objectName(),
                     self.dummy_object.objectName()],
                    self.dummy_group)

        # Coordinate space and bounding box
        if self.cspace == OPT[P_Opt.USE_WORLD_SPACE]:
            self.bbox_space = BboxSpace.WORLD
            self.bounding_box = self.dummy_world.copyBoundingBox()
        else:
            self.bbox_space = BboxSpace.OBJECT
            self.bounding_box = self.dummy_object.copyBoundingBox()

        debug_bb = drawBoundingBox(self.bounding_box, space=BboxSpace.OBJECT)
        cmds.xform(debug_bb, centerPivots=True)
        cmds.move(0, 0, 0, debug_bb, rotatePivotRelative=True)

        self.largest_side_up_axis = None
        self.underside = Underside.BOTTOM
        bb_width, bb_height, bb_depth = self.bounding_box.getDimensions()
        sides = determine_smallest_and_largest_bbox_side(bb_width,
                                                         bb_height,
                                                         bb_depth
        )
        self.turn_plane_90_deg = _should_turn_folding_plane(sides)

        # Calculate ribbon width and thickness
        shortest_edge = min(bb_width, bb_height, bb_depth)
        self.ribbon_width = shortest_edge * (self.ribbon_width / 10)
        self.ribbon_thickness *= max(
                ATTR[Parm.PAPER_THICKNESS][P_Attr.MIN_VALUE],
                self.paper_thickness)

        if (self.dynamic_up_axis or self.auto_place):
            print(f'Largest: {sides.largest}, smallest: {sides.smallest}')
            if sides.largest == BboxFacePair.LEFT_RIGHT:
                self.underside = Underside.LEFT
                cmds.xform(debug_bb, rotation=[0, 0, 90], objectSpace=True)
            elif sides.largest == BboxFacePair.FRONT_BACK:
                self.underside = Underside.BACK
                cmds.xform(debug_bb, rotation=[90, 0, 0], objectSpace=True)

        if self.underside == Underside.BOTTOM:
            self.width = bb_width
            self.height = bb_height
            self.depth = bb_depth
        elif self.underside == Underside.LEFT:
            self.width = bb_height
            self.height = bb_depth
            self.depth = bb_width
        elif self.underside == Underside.BACK:
            self.height = bb_depth
            self.depth = bb_height
        else:
            raise RuntimeError("Invalid underside")

        if self.turn_plane_90_deg:
            temp = self.width
            self.width = self.depth
            self.depth = temp
            cmds.xform(debug_bb, rotation=[0, 90, 0], relative=True)

        self.invert_flap_order = False
        self.paper = Paper(self.width, self.height, self.depth,
                           self.paper_thickness, self.invert_flap_order,
                           self.wrap_id)
        self.paper.setFoldNumber(16)

        uw_xyz_f_l = self.paper.getUnwrappedFrontLeftCorner()
        uw_xyz_b_r = self.paper.getUnwrappedBackRightCorner()
        self.control_handle = Control_handle(uw_xyz_f_l.x, uw_xyz_b_r.z,
                                             uw_xyz_b_r.x, uw_xyz_f_l.z,
                                             self.wrap_id)
        self.ribbon = Ribbon(self.width, self.height, self.depth,
                             self.paper_thickness,
                             self.ribbon_thickness, self.ribbon_width,
                             self.wrap_id)
        self.anchor = ObjectAnchor(self.object, self.bounding_box)

        # self.shaders = None


        # Debug offset
        # cmds.xform(self.paper.getGroup(),
        #            translation=list(self.bounding_box.getCentroid()),
        #            worldSpace=True)

    @staticmethod
    def idGenerator(size=4, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

# ==============================================================================
# Helpers
# ==============================================================================

def _default_value(parameter):
    """Fetch the default value for the given parameter"""
    return ATTR[parameter][P_Attr.DEFAULT_VALUE]

def _validate_within_min_max(parameter_id, parameter_value):
    """
    Checks if the given parameter value is within the valid range contained
    in the global parameter list. Raises an exception if not.

    Args:
        parameter_id: Parm Enum
        parameter_value: The value to check.
    """
    if (parameter_value < ATTR[parameter_id][P_Attr.MIN_VALUE] or
            parameter_value > ATTR[parameter_id][P_Attr.MAX_VALUE]):
        raise ValueError("Value outside of valid range")

def _should_turn_folding_plane(s):
    """
    Checks if the given sides of the object indicate that the folding plane
    should be turned 90 degrees before wrapping, so that the folds end up on the
    smallest side.

    Args:
        s: A named tuple containing the `largest` and `smallest` side of the
           object to be wrapped.

    Returns:
        Boolean
    """
    BBF = BboxFacePair
    return ((s.largest == BBF.TOP_BOTTOM and s.smallest == BBF.FRONT_BACK) or
            (s.largest == BBF.LEFT_RIGHT and s.smallest == BBF.FRONT_BACK) or
            (s.largest == BBF.FRONT_BACK and s.smallest == BBF.TOP_BOTTOM))
