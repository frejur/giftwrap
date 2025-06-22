import copy
import maya.cmds as cmds

from ...utils.bbox import *

_DUMMY_PREFIX = 'dummy'

class WrapDummy():
    def __init__(self,
                 obj,
                 wrapper_id,
                 bb_space=BboxSpace.WORLD,
                 curves_color=(1, 1, 1)):
        """
        Used to represent the bounds of the original object.
        Args:
            obj:           Name of the object to wrap
            wrapper_id:    ID of the wrapper
            space:         Coordinate space
            curves_color:  Tuple (r, g, b), the color of the curves used to draw
                           the bounding box.

        Notes:
            The `obj` parameter will be validated by the Bounding Box classes.
        """

        if (bb_space == BboxSpace.WORLD):
            self.bbox  = BoundingBox(obj)
        elif (bb_space == BboxSpace.OBJECT):
            self.bbox = ObjectSpaceBoundingBox(obj)
        else:
            raise Exception( 'Invalid coordinate space parameter')

        self.curves = drawBoundingBox(
            self.bbox,
            color=curves_color,
            space=BboxSpace.WORLD
        )
        self.curves = cmds.rename(
            self.curves,
            f'{_DUMMY_PREFIX}_{bb_space.name.lower()}_{wrapper_id}_grp'
        )

    def toggleVisibility(self, show=None):
        if show is None:
            a = f'{self.curves}.visibility'
            cmds.setAttr(a, not cmds.getAttr(a))
        elif show:
            cmds.showHidden(self.curves)
        elif show == False:
            cmds.hide(self.curves)
        else:
            raise ValueError("Invalid show argument")

    def objectName(self):
        return self.curves

    def copyBoundingBox(self):
        return copy.deepcopy(self.bbox)

