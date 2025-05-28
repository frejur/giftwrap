import maya.cmds as cmds

from ...utils import (
    Scoped_layout
)
from ....layout_constants import *
from .....globals.parameters import *

def create_color_section(self):
    """
    Creates the controls for adjusting colors.
    A basic four-column layout with labels and dropdowns.
    """
    with Scoped_layout(
            cmds.frameLayout(
                l='  Colors (Legacy)',
                w=COL_TWEAK_R,
                collapsable=True,
                collapse=True,
                bgc=COLORS_TITLE_BG
            )
    ) as frame_colors:
        with Scoped_layout(
                cmds.columnLayout(
                    rs=ROW_SP,
                    bgc=COLORS_BG
                )
        ) as col_colors:
            with Scoped_layout(
                    cmds.rowLayout(
                        numberOfColumns=4,
                        columnWidth4=COLS_COLORS
                    )
            ) as row_colors:
                # ==============================================================
                # Paper Color
                cmds.text(
                    l='{}:'.format(
                        ATTR[Parm.PAPER_COLOR][P_Attr.CONTROL_LABEL]
                    ),
                    ann=ATTR[Parm.PAPER_COLOR][P_Attr.DESCRIPTION],
                    align='right'
                )

                self.paper_color = cmds.optionMenu(
                    bgc=ORIENT_MENU_BG,
                    w=COL_COLORS_2,
                    ann=ATTR[Parm.PAPER_COLOR][P_Attr.DESCRIPTION]
                )
                for i in ATTR[Parm.PAPER_COLOR][P_Attr.OPTIONS]:
                    cmds.menuItem(l=OPT[i])
                cmds.optionMenu(
                    self.paper_color,
                    e=True,
                    sl=ATTR[Parm.PAPER_COLOR][P_Attr.DEFAULT_VALUE]
                )

                # ==============================================================
                # Ribbon Color
                cmds.text(
                    l='{}:'.format(
                        ATTR[Parm.RIBBON_COLOR][P_Attr.CONTROL_LABEL]
                    ),
                    ann=ATTR[Parm.RIBBON_COLOR][P_Attr.DESCRIPTION],
                    align='right'
                )

                self.ribbon_color = cmds.optionMenu(
                    bgc=ORIENT_MENU_BG,
                    w=COL_COLORS_4,
                    ann=ATTR[Parm.RIBBON_COLOR][P_Attr.DESCRIPTION]
                )
                for i in ATTR[Parm.RIBBON_COLOR][P_Attr.OPTIONS]:
                    cmds.menuItem(l=OPT[i])
                cmds.optionMenu(
                    self.ribbon_color,
                    e=True,
                    sl=ATTR[Parm.RIBBON_COLOR][P_Attr.DEFAULT_VALUE]
                )
