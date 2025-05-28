import maya.cmds as cmds
from ..layout_constants import *

class Scoped_layout:
    """
    Temporarily sets the current parent to a specified Maya UI element,
    allowing child controls to be added within its context. Upon exit,
    the parent is restored to its previous value.

    Args:
        parent_command: The return value from a Maya UI creation command.

    Example:
        ```python
        with Scoped_layout(cmds.columnLayout(adjustableColumn=True)) as layout:
            cmds.button(label="Button 1")
            cmds.button(label="Button 2")
        # Parent is automatically restored after the block
        ```
    """
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
        h=separator_height,
        style='out',
        horizontal=False,
    )

def _create_horizontal_separator(separator_width):
    cmds.separator(
        w=separator_width,
        h=H_SEP_H,
        style='in'
    )

