import maya.cmds as cmds
from dataclasses import dataclass

from .wrap import *
from .utils import (
    Scoped_layout,
    _create_horizontal_separator
)
from .. import layout_constants as const

@dataclass
class UISections:
    paper_and_ribbon: Paper_and_ribbon_controls = None
    anim_and_wrap: Animation_and_wrap_controls = None
    tweaks: Fine_tuning_controls = None

def create(main_parent):
    """
    Creates the layout and controls for the Wrap Gift section of the UI.
    """
    with Scoped_layout(
        cmds.frameLayout(
            l='New wrapper',
            width=const.WIN_W,
            collapsable=True,
            collapse=False,
            parent=main_parent
        )
    ) as wrap_frame:
        with Scoped_layout(
                cmds.columnLayout(rs=const.ROW_SP)
        ) as wrap_column:
            ctrl_paper_rib = Paper_and_ribbon_controls()
            _create_horizontal_separator(const.WIN_W_NO_MARGIN)
            ctrl_anim_wrap = Animation_and_wrap_controls()
            _create_horizontal_separator(const.WIN_W_NO_MARGIN)
            ctrl_tweak = Fine_tuning_controls()

    return UISections(
        paper_and_ribbon=ctrl_paper_rib,
        anim_and_wrap=ctrl_anim_wrap,
        tweaks=ctrl_tweak
    )

