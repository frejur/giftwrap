import maya.cmds as cmds

from ...utils import (
    Scoped_layout,
    _create_horizontal_separator
)
from ....layout_constants import *
from .....globals.parameters import *

def create_orientation_and_placement_section(self):
    with Scoped_layout(
            cmds.frameLayout(
                l='  Orientation and Placement',
                w=COL_TWEAK_R,
                collapsable=True,
                collapse=True,
                bgc=ORIENT_TITLE_BG
            )
    ) as col_orientation_and_placement:
        with Scoped_layout(
                cmds.columnLayout(
                    rs=ROW_SP,
                    bgc=ORIENT_BG
                )
        ) as col_orientation:
            # ==================================================================
            # Orientation Row
            with Scoped_layout(
                    cmds.rowLayout(
                        numberOfColumns=5,
                        columnWidth5=COLS_ORI_UP
                    )
            ) as row_orientation:
                # ==============================================================
                # Coordinate space

                cmds.text(
                    l='{}:'.format(
                        ATTR[Parm.COORDINATE_SPACE][P_Attr.CONTROL_LABEL]
                    ),
                    align='right'
                )

                self.coordinate_space = (
                    cmds.optionMenu(bgc=ORIENT_MENU_BG)
                )
                for i in ATTR[Parm.COORDINATE_SPACE][P_Attr.OPTIONS]:
                    cmds.menuItem(l=OPT[i])
                cmds.optionMenu(
                    self.coordinate_space,
                    e=True,
                    sl=ATTR[Parm.COORDINATE_SPACE][P_Attr.DEFAULT_VALUE]
                )

                largest_side_label = 'Largest side'
                cmds.text(
                    l='      {}:'.format(
                        ATTR[Parm.UP_AXIS][P_Attr.CONTROL_LABEL]
                    ),
                    align='right'
                )

                # ==============================================================
                # Up-axis

                self.up_axis = (
                    cmds.optionMenu(bgc=ORIENT_MENU_BG)
                )
                for i in ATTR[Parm.UP_AXIS][P_Attr.OPTIONS]:
                    cmds.menuItem(l=OPT[i])
                cmds.optionMenu(
                    self.up_axis,
                    e=True,
                    sl=ATTR[Parm.UP_AXIS][P_Attr.DEFAULT_VALUE]
                )
                print(f'default value:{ATTR[Parm.UP_AXIS][P_Attr.DEFAULT_VALUE]}')

                self.invert_up = cmds.checkBox(
                    l=ATTR[Parm.INVERT_UP_AXIS][P_Attr.CONTROL_LABEL],
                    value=ATTR[Parm.INVERT_UP_AXIS][P_Attr.DEFAULT_VALUE]
                )

            _create_horizontal_separator(COL_TWEAK_R)

            # ==================================================================
            # Placement row
            with Scoped_layout(
                    cmds.rowLayout(
                        numberOfColumns=4,
                        columnWidth4=COLS_PLACE,
                        bgc=ORIENT_BG
                    )
            ) as row_placement:
                # ==============================================================
                # Object placement
                self.object_placement_label = cmds.text(
                    l='{}:'.format(
                        ATTR[Parm.AUTO_PLACE_OBJECT][P_Attr.CONTROL_LABEL]
                    ),
                    align='right'
                )

                self.object_placement_menu = cmds.optionMenu(
                    bgc=ORIENT_MENU_BG,
                    w=COL_PLACE_2
                )
                for i in ATTR[Parm.AUTO_PLACE_OBJECT][P_Attr.OPTIONS]:
                    cmds.menuItem(l=OPT[i])
                cmds.optionMenu(
                    self.object_placement_menu,
                    e=True,
                    sl=ATTR[Parm.AUTO_PLACE_OBJECT][P_Attr.DEFAULT_VALUE]
                )

                # ==============================================================
                # Ribbon Placement
                cmds.text(
                    l='   {}: '.format(
                        ATTR[Parm.KNOT_PLACEMENT][P_Attr.CONTROL_LABEL]
                    ),
                    align='right'
                )

                self.knot_placement = cmds.optionMenu(
                    bgc=ORIENT_MENU_BG,
                    w=COL_PLACE_4
                )
                for i in ATTR[Parm.KNOT_PLACEMENT][P_Attr.OPTIONS]:
                    cmds.menuItem(l=OPT[i])
                cmds.optionMenu(
                    self.knot_placement,
                    e=True,
                    sl=ATTR[Parm.KNOT_PLACEMENT][P_Attr.DEFAULT_VALUE]
                )
