import maya.cmds as cmds
from .. import _const

class _Layout:
    def __init__(self, parent_command):
        self.parent = parent_command

    def __enter__(self):
        cmds.setParent(self.parent)
        return self.parent

    def __exit__(self, *args):
        cmds.setParent(self.parent)
        cmds.setParent('..')

def _create_vertical_separator(separator_height):
    cmds.separator(
        w=_const.V_SEP_W,
        h=separator_height,
        style='out',
        horizontal=False
    )

def _create_horizontal_separator(separator_width):
    cmds.separator(
        w=separator_width,
        h=_const.H_SEP_H,
        style='in'
    )

