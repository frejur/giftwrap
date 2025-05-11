import maya.cmds as cmds
from ... import GiftWrap

""" Helpers to fetch control values """
def _sliderValue(ctrl_name, **kwargs):
    return cmds.floatSliderGrp(kwargs.get(ctrl_name), query=True, value=True )
def _optionValue(ctrl_name, **kwargs):
    return cmds.optionMenu(kwargs.get(ctrl_name), query=True, value=True )
def _intValue(ctrl_name, **kwargs):
    return cmds.intField(kwargs.get(ctrl_name), query=True, value=True )

def runWrap(**kwargs):
    """
    Creates a Wrapper object for each selected node
    """
    paper_thickness = _sliderValue('ctrl_paper_thickness', **kwargs)
    paper_color     = _optionValue('ctrl_paper_color', **kwargs).lower()
    ribbon_size     = _optionValue('ctrl_ribbon_width', **kwargs)[0]
    ribbon_color    = _optionValue('ctrl_ribbon_color', **kwargs).lower()
    animation_start =    _intValue('ctrl_anim_start', **kwargs)
    animation_end   =    _intValue('ctrl_anim_end', **kwargs)

    objects = cmds.ls(selection=True)

    for o in objects[:32]:
        GiftWrap(
            o, 'create',
            ribbon_size, paper_thickness, paper_color,
            ribbon_color, animation_start, animation_end
        )
