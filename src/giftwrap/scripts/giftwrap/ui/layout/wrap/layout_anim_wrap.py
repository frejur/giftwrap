import maya.cmds as cmds

from ..utils import (
    Scoped_layout,
    _create_vertical_separator
)
from ...layout_constants import *
from ....globals.parameters import *

class Animation_and_wrap_controls:
    """
    Creates the controls for adjusting Animation, and the Wrap button panel.
    A three-column layout, with a vertical separator in the middle.
    """

    def __init__(self):
        self.start_frame       = None
        self.end_frame         = None
        self.animate_placement = None
        self.animate_gift_flip = None
        self.wrap_button       = None
        self.keep_original     = None

        with Scoped_layout(
                cmds.rowLayout(
                    numberOfColumns=3,
                    columnWidth3=COLS_1_SEP_1,
                    adjustableColumn=2,
                )
        ) as anim_and_wrap_root:
            self.create_animation_controls()
            _create_vertical_separator(SEP_PAPER_RIBBON_H)
            self.create_wrap_panel_controls()

    def create_animation_controls(self):
        with Scoped_layout(
                cmds.columnLayout(rs=ROW_SP)
        ) as wrap_col_anim:
            cmds.text(l=' Animation', font=FNT_SM)

            with Scoped_layout(
                    cmds.rowLayout(
                        numberOfColumns=4,
                        columnWidth4=COLS_ANIM,
                        adj=3,
                    )
            ) as wrap_row_anim:
                cmds.text(
                    l='Range:',
                    align='right',
                    w=COL_ANIM_L,
                )
                self.start_frame = cmds.intField(
                    minValue=ATTR[Parm.ANIM_START_FRAME][P_Attr.MIN_VALUE],
                    value=ATTR[Parm.ANIM_START_FRAME][P_Attr.DEFAULT_VALUE],
                    maxValue=ATTR[Parm.ANIM_START_FRAME][P_Attr.MAX_VALUE],
                    w=COL_ANIM_M
                )
                cmds.text(
                    l=':',
                )
                self.end_frame = cmds.intField(
                    minValue=ATTR[Parm.ANIM_END_FRAME][P_Attr.MIN_VALUE],
                    value=ATTR[Parm.ANIM_END_FRAME][P_Attr.DEFAULT_VALUE],
                    maxValue=ATTR[Parm.ANIM_END_FRAME][P_Attr.MAX_VALUE],
                    w=COL_ANIM_R
                )

            with Scoped_layout(
                    cmds.rowLayout(
                        numberOfColumns=2,
                        columnWidth2=COLS_ANIM_TGL,
                        adj=2,
                    )
            ) as row_anim_tgl_placement:
                cmds.text(l='', w=COL_ANIM_TGL_L) # Empty column
                self.animate_placement = cmds.checkBox(
                    l=ATTR[Parm.ANIMATE_PLACEMENT][P_Attr.CONTROL_LABEL],
                    value=ATTR[Parm.ANIMATE_PLACEMENT][P_Attr.DEFAULT_VALUE],
                    w=COL_ANIM_TGL_R,
                )

            with Scoped_layout(
                    cmds.rowLayout(
                        numberOfColumns=2,
                        columnWidth2=COLS_ANIM_TGL,
                        adj=2,
                    )
            ) as row_anim_tgl_flip:
                cmds.text(l='', w=COL_ANIM_TGL_L) # Empty column
                self.animate_gift_flip = cmds.checkBox(
                    l=ATTR[Parm.ANIMATE_GIFT_FLIP][P_Attr.CONTROL_LABEL],
                    value=ATTR[Parm.ANIMATE_GIFT_FLIP][P_Attr.DEFAULT_VALUE],
                    w=COL_ANIM_TGL_R
                )

    def create_wrap_panel_controls(self):
        with Scoped_layout(
                cmds.columnLayout(
                    rs=ROW_SP,
                    columnAlign='center'
                )
        ) as col_root:
            with Scoped_layout(
                    cmds.rowLayout(
                        numberOfColumns=3,
                        columnWidth3=COLS_WRAP,
                        adj=1,
                    )
            ) as row_wrap_button:
                with Scoped_layout(cmds.columnLayout()) as _: 0 # Empty column
                self.wrap_button = cmds.button(
                    l=ATTR[Parm.WRAP_BUTTON][P_Attr.CONTROL_LABEL],
                    w=COL_WRAP_M,
                    h=BTN_WRAP_H,
                )
                with Scoped_layout(cmds.columnLayout()) as _: 0 # Empty column

            with Scoped_layout(
                    cmds.rowLayout(
                        numberOfColumns=2,
                        columnWidth2=COLS_KEEP,
                        adj=2,
                    )
            ) as row_keep_original:
                with Scoped_layout(cmds.columnLayout()) as _: 0 # Empty column
                self.keep_original = cmds.checkBox(
                    l=ATTR[Parm.KEEP_ORIGINAL][P_Attr.CONTROL_LABEL],
                    value=ATTR[Parm.KEEP_ORIGINAL][P_Attr.DEFAULT_VALUE]
                )
