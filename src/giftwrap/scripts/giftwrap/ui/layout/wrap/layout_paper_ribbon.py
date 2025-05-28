import maya.cmds as cmds

from ..utils import (
    Scoped_layout,
    _create_vertical_separator
)
from ...layout_constants import *
from ....globals.parameters import *

class Paper_and_ribbon_controls:
    """
    Creates the controls for adjusting the appearance of the Paper and Ribbon.
    A three-column layout, with a vertical separator in the middle.
    """
    def __init__(self):
        self.paper_thickness  = None
        self.use_plane        = None
        self.ribbon_width     = None
        self.ribbon_thickness = None

        with Scoped_layout(
                cmds.rowLayout(
                    numberOfColumns=3,
                    columnWidth3=COLS_1_SEP_1,
                    adjustableColumn=2,
                )
        ) as paper_and_ribbon_root:
            self.create_paper_controls()
            _create_vertical_separator(SEP_PAPER_RIBBON_H)
            self.create_ribbon_controls()

    def create_paper_controls(self):
        """ Controls for adjusting the properties of the paper mesh """
        with Scoped_layout(
                cmds.columnLayout(rs=ROW_SP)
        ) as wrap_col_paper:
            cmds.text(l=' Paper', font=FNT_SM)

            with Scoped_layout(
                    cmds.rowLayout(
                        numberOfColumns=2,
                        columnWidth2=COLS_PAPER_RIBBON,
                        adj=2
                    )
            ) as wrap_row_paper_w:
                cmds.text(
                    l=f' {ATTR[Parm.PAPER_THICKNESS][P_Attr.CONTROL_LABEL]}:  ',
                    align='right',
                    w=COL_PAPER_RIBBON_L
                )
                self.paper_thickness = cmds.floatSlider(
                    minValue=ATTR[Parm.PAPER_THICKNESS][P_Attr.MIN_VALUE],
                    maxValue=ATTR[Parm.PAPER_THICKNESS][P_Attr.MAX_VALUE],
                    value=ATTR[Parm.PAPER_THICKNESS][P_Attr.DEFAULT_VALUE],
                )

            with Scoped_layout(
                    cmds.rowLayout(
                        numberOfColumns=2,
                        columnWidth2=COLS_PAPER_RIBBON,
                        adj=1
                    )
            ) as wrap_row_paper_tgl:
                cmds.text(l='', w=COL_PAPER_RIBBON_L)  # Empty column
                self.use_plane = cmds.checkBox(
                    l='Plane Only',
                )

    def create_ribbon_controls(self):
        """ Controls for adjusting the properties of the ribbon mesh """
        with Scoped_layout(
                cmds.columnLayout(rs=ROW_SP)
        ) as wrap_col_ribbon:

            cmds.text(l=' Ribbon', font=FNT_SM)

            with Scoped_layout(
                    cmds.rowLayout(
                        numberOfColumns=2,
                        # columnWidth2=COLS_PAPER_RIBBON
                        cw=(1, COL_PAPER_RIBBON_L),
                        adj=1
            )
            ) as wrap_row_ribbon_thk:

                cmds.text(
                    l=f'{ATTR[Parm.RIBBON_THICKNESS][P_Attr.CONTROL_LABEL]}:  ',
                    align='right',
                    w=COL_PAPER_RIBBON_L
                )
                self.ribbon_thickness = cmds.floatSlider(
                    minValue=ATTR[Parm.RIBBON_THICKNESS][P_Attr.MIN_VALUE],
                    maxValue=ATTR[Parm.RIBBON_THICKNESS][P_Attr.MAX_VALUE],
                    value=ATTR[Parm.RIBBON_THICKNESS][P_Attr.DEFAULT_VALUE],
                )

            with Scoped_layout(cmds.rowLayout(
                    numberOfColumns=2,
                    columnWidth2=COLS_PAPER_RIBBON)
            ) as wrap_row_ribbon_w:

                cmds.text(
                    l=f'{ATTR[Parm.RIBBON_WIDTH][P_Attr.CONTROL_LABEL]}:  ',
                    align='right',
                    w=COL_PAPER_RIBBON_L
                )
                self.ribbon_width = cmds.floatSlider(
                    minValue=ATTR[Parm.RIBBON_WIDTH][P_Attr.MIN_VALUE],
                    maxValue=ATTR[Parm.RIBBON_WIDTH][P_Attr.MAX_VALUE],
                    value=ATTR[Parm.RIBBON_WIDTH][P_Attr.DEFAULT_VALUE],
                )