import maya.cmds as cmds
from ... import GiftWrap
from ...wrapper import *
from ...globals.parameters import *

""" Helper to fetch control values """
def _controlValue(ctrl_name, ctrl_type):
    if (ctrl_type == None):
        raise ValueError("Parameter attribute has no control type")
    if (ctrl_type == Ctrl_Type.OPTION_MENU):
        return cmds.optionMenu(ctrl_name, query=True, value=True)
    if (ctrl_type == Ctrl_Type.CHECKBOX):
        return cmds.checkBox(ctrl_name, query=True, value=True)
    if (ctrl_type == Ctrl_Type.FLOAT_SLIDER):
        return cmds.floatSlider(ctrl_name, query=True, value=True)
    if (ctrl_type == Ctrl_Type.INT_FIELD):
        return cmds.intField(ctrl_name, query=True, value=True)

def runWrap(**kwargs):
    """
    Creates a Wrapper object for each selected node
    """

    new_kwargs = {}
    for (key_string, value) in kwargs.items():
        try:
            key_enum = Parm[key_string.upper()]
        except KeyError:
            continue

        if key_enum in ATTR and P_Attr.CONTROL_TYPE in ATTR[key_enum]:
            value = _controlValue(value, ATTR[key_enum][P_Attr.CONTROL_TYPE])

        new_kwargs[key_string] = value

    new_kwargs[Parm.RIBBON_WIDTH.name.lower()] = 'L' # TODO: Implement proper ribbon width

    objects = cmds.ls(selection=True)

    for o in objects:
        GiftWrap(o, **new_kwargs)

# DEBUG BEGIN ==================================================================

def runWrapDebug(**kwargs):
    """
    Creates a Wrapper object for each selected node
    """

    new_kwargs = {}
    for (key_string, value) in kwargs.items():
        try:
            key_enum = Parm[key_string.upper()]
        except KeyError:
            continue

        if key_enum in ATTR and P_Attr.CONTROL_TYPE in ATTR[key_enum]:
            value = _controlValue(value, ATTR[key_enum][P_Attr.CONTROL_TYPE])

        new_kwargs[key_string] = value

    objects = cmds.ls(selection=True)

    for o in objects:
        Wrapper( o, **new_kwargs )

# DEBUG BREAK ==================================================================

