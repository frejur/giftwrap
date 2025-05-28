import maya.cmds as cmds
import maya.OpenMaya as om
from numpy.ma.core import absolute


class ObjectAnchor:
    """
    A locator which serves as an anchor point for moving and rotating the
    object to be wrapped.
    """
    def __init__(self, object, bbox):
        if  not cmds.objExists(object):
            raise ValueError(f'Node "{object}" does not exist')

        c = bbox.getCentroid()
        self.anchor = cmds.spaceLocator()
        cmds.move(c[0], c[1], c[2], self.anchor, absolute=True)
        # cmds.parent(object, self.anchor, absolute=True)
        # cmds.move(c[0], c[1], c[2], self.anchor, absolute=True)


        # cmds.move(0,1,0, self.anchor, r=True, rpv=True)
