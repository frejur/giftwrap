import maya.cmds as cmds

from .utils import (_Layout,
                    _create_horizontal_separator,
                    _create_vertical_separator)
from .. import _const
from ..actions import action_run
from ...wrapper._parms import *

def create(main_parent):
    """
    Creates the layout and controls for the Wrap Gift section of the UI.
    """
    ctrl_paper_rib = None
    ctrl_anim_wrap = None
    ctrl_fine_tune = None

    with _Layout(
        cmds.frameLayout(
            l='Wrap Gift',
            width=_const.WIN_W,
            collapsable=True,
            collapse=False,
            parent=main_parent
        )
    ) as wrap_frame:
        with _Layout(
                cmds.columnLayout(rs=_const.ROW_SP)
        ) as wrap_column:
            ctrl_paper_rib = _Paper_and_ribbon_controls()
            _create_horizontal_separator(_const.WIN_W)
            ctrl_anim_wrap = _Animation_and_wrap_controls()
            _create_horizontal_separator(_const.WIN_W)
            ctrl_fine_tune = _Fine_tuning_controls()

class _Paper_and_ribbon_controls:
    """
    Creates the controls for adjusting the appearance of the Paper and Ribbon.
    A three-column layout, with a vertical separator in the middle.
    """
    def __init__(self):
        self.paper_weight     = None
        self.use_plane        = None
        self.ribbon_width     = None
        self.ribbon_thickness = None

        with _Layout(
            cmds.rowLayout(
                numberOfColumns=3, columnWidth3=_const.COLS_1_SEP_1
            )
        ) as paper_and_ribbon_root:
            self.create_paper_controls()
            _create_vertical_separator(_const.SEP_PAPER_RIBBON_H)
            self.create_ribbon_controls()


    def create_paper_controls(self):
        """ Controls for adjusting the properties of the paper mesh """
        with _Layout(
            cmds.columnLayout( rs=_const.ROW_SP)
        ) as wrap_col_paper:
            cmds.text(l=' Paper', font=_const.FNT_SM)

            with _Layout(
                cmds.rowLayout(
                    numberOfColumns=2,
                    columnWidth2=_const.COLS_PAPER_RIBBON
                )
            ) as wrap_row_paper_w:
                cmds.text(
                    l=f' {ATTR[Parm.PAPER_WEIGHT][P_Attr.CONTROL_LABEL]}:  ',
                    align='right',
                    w=_const.COL_PAPER_RIBBON_L
                )
                self.paper_weight = cmds.floatSliderGrp(
                    minValue=ATTR[Parm.PAPER_WEIGHT][P_Attr.MIN_VALUE],
                    maxValue=ATTR[Parm.PAPER_WEIGHT][P_Attr.MAX_VALUE],
                    value=ATTR[Parm.PAPER_WEIGHT][P_Attr.DEFAULT_VALUE],
                    w=_const.COL_PAPER_RIBBON_R
                )

            with _Layout(
                cmds.rowLayout(
                    numberOfColumns=2,
                    columnWidth2=_const.COLS_PAPER_RIBBON,
                )
            ) as wrap_row_paper_tgl:
                cmds.text(l='', w=_const.COL_PAPER_RIBBON_L)  # Empty column
                wrap_tgl_plane = cmds.checkBox(
                    l='Plane Only',
                    w=_const.COL_PAPER_RIBBON_R
                )

    def create_ribbon_controls(self):
        """ Controls for adjusting the properties of the ribbon mesh """
        with _Layout(
            cmds.columnLayout( rs=_const.COL_SP )
        ) as wrap_col_ribbon:

            cmds.text(l=' Ribbon', font=_const.FNT_SM)

            with _Layout(
               cmds.rowLayout(
                   numberOfColumns=2,
                   columnWidth2=_const.COLS_PAPER_RIBBON
               )
            ) as wrap_row_ribbon_thk:

               cmds.text(
                   l=f'{ATTR[Parm.RIBBON_THICKNESS][P_Attr.CONTROL_LABEL]}:  ',
                   align='right',
                   w=_const.COL_PAPER_RIBBON_L
               )
               wrap_sld_rib_thk = cmds.floatSlider(
                   minValue=ATTR[Parm.RIBBON_THICKNESS][P_Attr.MIN_VALUE],
                   maxValue=ATTR[Parm.RIBBON_THICKNESS][P_Attr.MAX_VALUE],
                   value=ATTR[Parm.RIBBON_THICKNESS][P_Attr.DEFAULT_VALUE],
                   w=_const.COL_PAPER_RIBBON_R
               )

            with _Layout(cmds.rowLayout(
                numberOfColumns=2,
                columnWidth2=_const.COLS_PAPER_RIBBON)
            ) as wrap_row_ribbon_w:

                cmds.text(
                    l=f'{ATTR[Parm.RIBBON_WIDTH][P_Attr.CONTROL_LABEL]}:  ',
                    align='right',
                    w=_const.COL_PAPER_RIBBON_L
                )
                self.ribbon_width = cmds.floatSlider(
                    minValue=ATTR[Parm.RIBBON_WIDTH][P_Attr.MIN_VALUE],
                    maxValue=ATTR[Parm.RIBBON_WIDTH][P_Attr.MAX_VALUE],
                    value=ATTR[Parm.RIBBON_WIDTH][P_Attr.DEFAULT_VALUE],
                    w=_const.COL_PAPER_RIBBON_R
                )

class _Animation_and_wrap_controls:
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

        with _Layout(
            cmds.rowLayout(
                numberOfColumns=3,
                columnWidth3=_const.COLS_1_SEP_1,
            )
        ) as anim_and_wrap_root:
            self.create_animation_controls()
            _create_vertical_separator(_const.SEP_PAPER_RIBBON_H)
            self.create_wrap_panel_controls()

    def create_animation_controls(self):
        with _Layout(
            cmds.columnLayout(rs=_const.COL_SP)
        ) as wrap_col_anim:
            cmds.text(
                l=' Animation',
                font=_const.FNT_SM
            )

            with _Layout(
                cmds.rowLayout(
                    numberOfColumns=4,
                    columnWidth4=_const.COLS_ANIM
                )
            ) as wrap_row_anim:
                cmds.text(
                    l='Range:',
                    w=_const.COL_ANIM_L,
                    align='right'
                )
                self.start_frame = cmds.intField(
                    minValue=ATTR[Parm.ANIM_START_FRAME][P_Attr.MIN_VALUE],
                    value=ATTR[Parm.ANIM_START_FRAME][P_Attr.DEFAULT_VALUE],
                    maxValue=ATTR[Parm.ANIM_START_FRAME][P_Attr.MAX_VALUE],
                    w=_const.COL_ANIM_M
                )
                cmds.text(
                    l=':',
                    w=_const.COL_ANIM_GAP
                )
                self.end_frame = cmds.intField(
                    minValue=ATTR[Parm.ANIM_END_FRAME][P_Attr.MIN_VALUE],
                    value=ATTR[Parm.ANIM_END_FRAME][P_Attr.DEFAULT_VALUE],
                    maxValue=ATTR[Parm.ANIM_END_FRAME][P_Attr.MAX_VALUE],
                    w=_const.COL_ANIM_R
                )

            with _Layout(
                cmds.rowLayout(
                    numberOfColumns=2,
                    columnWidth2=_const.COLS_ANIM_TGL
                )
            ) as row_anim_tgl_placement:
                cmds.text(l='', w=_const.COL_ANIM_TGL_L) # Empty column
                self.animate_placement = cmds.checkBox(
                    l=ATTR[Parm.ANIMATE_PLACEMENT][P_Attr.CONTROL_LABEL],
                    value=ATTR[Parm.ANIMATE_PLACEMENT][P_Attr.DEFAULT_VALUE],
                    w=_const.COL_ANIM_TGL_R
                )

            with _Layout(
                cmds.rowLayout(
                    numberOfColumns=2,
                    columnWidth2=_const.COLS_ANIM_TGL
                )
            ) as row_anim_tgl_flip:
                cmds.text(l='', w=_const.COL_ANIM_TGL_L) # Empty column
                self.animate_gift_flip = cmds.checkBox(
                    l=ATTR[Parm.ANIMATE_GIFT_FLIP][P_Attr.CONTROL_LABEL],
                    value=ATTR[Parm.ANIMATE_GIFT_FLIP][P_Attr.DEFAULT_VALUE],
                    w=_const.COL_ANIM_TGL_R
                )

    def create_wrap_panel_controls(self):
        with _Layout(
            cmds.columnLayout(
                rs=_const.COL_SP,
                columnAlign='center'
            )
        ) as col_root:
            with _Layout(
                cmds.rowLayout(
                    numberOfColumns=3,
                    columnWidth3=_const.COLS_WRAP
                )
            ) as row_wrap_button:
                cmds.text(l='', w=_const.COL_WRAP_L) # Empty
                self.wrap_button = cmds.button(
                    l=ATTR[Parm.WRAP_BUTTON][P_Attr.CONTROL_LABEL],
                    w=_const.COL_WRAP_M,
                    h=_const.BTN_WRAP_H,
                    align='center'
                )
                cmds.text(l='', w=_const.COL_WRAP_R) # Empty

            with _Layout(
                cmds.rowLayout(
                    numberOfColumns=2,
                    columnWidth2=_const.COLS_KEEP
                )
            ) as row_keep_original:
                cmds.text(l='', w=_const.COL_WRAP_L) # Empty
                self.keep_original = cmds.checkBox(
                    l=ATTR[Parm.KEEP_ORIGINAL][P_Attr.CONTROL_LABEL],
                    w=(_const.COL_WRAP_M + _const.COL_WRAP_R),
                    value=ATTR[Parm.KEEP_ORIGINAL][P_Attr.DEFAULT_VALUE]
                )

class _Fine_tuning_controls:
    """
    Creates the controls for tweaking attributes for Animation and Color.
    A 2-column layout, with the first one being empty to serve as padding.
    The layout contains collapsible layout for the different sections to be
    tweaked.
    """
    def __init__(self):
        self.coordinate_space = None
        self.up_axis          = None
        self.invert_up        = None
        self.object_placement = None
        self.knot_placement   = None

        cmds.text(l=' Fine tuning', font=_const.FNT_SM)

        with _Layout(
            cmds.rowLayout(
                numberOfColumns=2,
                columnWidth2=_const.COLS_FINE_TUNE
            )
        ) as row_orientation_and_placement:
            cmds.text('') # Left padding / indent
            self.create_orientation_and_placement_section()

        with _Layout(
            cmds.rowLayout(
                numberOfColumns=2,
                columnWidth2=_const.COLS_FINE_TUNE
            )
        ) as row_colors:
            cmds.text('') # Left padding / indent
            self.create_color_section()

    def create_orientation_and_placement_section(self):
        with _Layout(
            cmds.frameLayout(
                l='  Orientation and Placement',
                w=_const.COL_FINE_TUNE_R,
                collapsable=True,
                collapse=True,
                bgc=_const.ORIENT_TITLE_BG
            )
        ) as col_orientation_and_placement:
            with _Layout(
                cmds.columnLayout(
                    rs=_const.COL_SP,
                    bgc=_const.ORIENT_BG
                )
            ) as col_orientation:
                with _Layout(
                    cmds.rowLayout(
                        numberOfColumns=5,
                        columnWidth5=_const.COLS_ORI_UP
                    )
                ) as row_orientation:
                    cmds.text(
                        l='{}:'.format(
                            ATTR[Parm.COORDINATE_SPACE] [P_Attr.CONTROL_LABEL]
                        ),
                        align='right'
                    )

                    self.coordinate_space = (
                        cmds.optionMenu(bgc=_const.ORIENT_MENU_BG)
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

                    self.up_axis = (
                        cmds.optionMenu(bgc=_const.ORIENT_MENU_BG)
                    )
                    for i in ATTR[Parm.UP_AXIS][P_Attr.OPTIONS]:
                        cmds.menuItem(l=OPT[i])
                    cmds.optionMenu(
                        self.up_axis,
                        e=True,
                        sl=ATTR[Parm.UP_AXIS][P_Attr.DEFAULT_VALUE]
                    )

                    self.invert_up = cmds.checkBox(
                        l=ATTR[Parm.INVERT_UP_AXIS][P_Attr.CONTROL_LABEL],
                        value=ATTR[Parm.INVERT_UP_AXIS][P_Attr.DEFAULT_VALUE]
                    )

                _create_horizontal_separator(_const.COL_FINE_TUNE_R)

                with _Layout(
                    cmds.rowLayout(
                        numberOfColumns=4,
                        columnWidth4=_const.COLS_PLACE,
                        bgc=_const.ORIENT_BG
                )
                ) as row_placement:
                    cmds.text(
                        l='{}:'.format(
                            ATTR[Parm.AUTO_PLACE_OBJECT][P_Attr.CONTROL_LABEL]
                        ),
                        align='right'
                    )

                    self.object_placement = cmds.optionMenu(
                        bgc=_const.ORIENT_MENU_BG,
                        w=_const.COL_PLACE_2
                    )
                    for i in ATTR[Parm.AUTO_PLACE_OBJECT][P_Attr.OPTIONS]:
                        cmds.menuItem(l=OPT[i])
                    cmds.optionMenu(
                        self.up_axis,
                        e=True,
                        sl=ATTR[Parm.AUTO_PLACE_OBJECT][P_Attr.DEFAULT_VALUE]
                    )

                    cmds.text(
                        l='   {}: '.format(
                            ATTR[Parm.KNOT_PLACEMENT][P_Attr.CONTROL_LABEL]
                        ),
                        align='right'
                    )

                    self.knot_placement = cmds.optionMenu(
                        bgc=_const.ORIENT_MENU_BG,
                        w=_const.COL_PLACE_4
                    )
                    for i in ATTR[Parm.KNOT_PLACEMENT][P_Attr.OPTIONS]:
                        cmds.menuItem(l=OPT[i])
                    cmds.optionMenu(
                        self.up_axis,
                        e=True,
                        sl=ATTR[Parm.KNOT_PLACEMENT][P_Attr.DEFAULT_VALUE]
                    )


    def create_color_section(self):
        return

# def _update_object_placement_menu(self):
#     """ Helper function to toggle the status of the object placement menu """
#     auto_placement_possible = (
#             cmds.optionMenu(orient_opt_menu_up, query=True, value=True)
#             != largest_side_label
#     )
#     cmds.optionMenu(orient_menu_auto, edit=True, enable=auto_possible)
#     cmds.control(orient_auto_txt, edit=True, enable=auto_possible)
#
#     update_auto_menu()
#
#     cmds.optionMenu(orient_opt_menu_up, edit=True,
#                     changeCommand=lambda *args: update_auto_menu())


    # # Info text
    # cmds.text(
    #     parent=wrap_layout,
    #     align='center', width=_const.WIN_W, font='obliqueLabelFont',
    #     l='Wraps selected object(s), animates the whole process\n' +
    #       'by adjusting the connected attribute of the control handle',
    # )

    # wrap_btn_run =_setWrapButtonCommand(
    #     wrap_btn_run,
    #     ctrl_paper_thickness = wrap_sld_paper_w,
    #     # ctrl_paper_color     = wrap_opt_menu_p_color,
    #     ctrl_ribbon_width    = wrap_sld_rib_w,
    #     # ctrl_ribbon_color    = wrap_opt_menu_r_color,
    #     ctrl_anim_start      = wrap_int_anim_s,
    #     ctrl_anim_end        = wrap_int_anim_e
    # )

# def _create_color_controls(parent):
    # # Wrap row for color
    # wrap_row_color = cmds.rowLayout(
    #     numberOfColumns=4, columnWidth4=_const.COLS_4, parent=wrap_layout
    # )
    # cmds.text(l=' Paper color:', parent=wrap_row_color)
    # wrap_opt_menu_p_color = cmds.optionMenu(parent=wrap_row_color)
    # cmds.menuItem(l='Random', parent=wrap_opt_menu_p_color)
    # cmds.menuItem(l='Red', parent=wrap_opt_menu_p_color)
    # cmds.menuItem(l='Green', parent=wrap_opt_menu_p_color)
    # cmds.menuItem(l='Blue', parent=wrap_opt_menu_p_color)
    # cmds.menuItem(l='Yellow', parent=wrap_opt_menu_p_color)
    # cmds.menuItem(l='Black', parent=wrap_opt_menu_p_color)
    # cmds.menuItem(l='White', parent=wrap_opt_menu_p_color)
    #
    # cmds.text(l='Ribbon color:', parent=wrap_row_color)
    # wrap_opt_menu_r_color = cmds.optionMenu(parent=wrap_row_color)
    # cmds.menuItem(l='Random', parent=wrap_opt_menu_r_color)
    # cmds.menuItem(l='Red', parent=wrap_opt_menu_r_color)
    # cmds.menuItem(l='Green', parent=wrap_opt_menu_r_color)
    # cmds.menuItem(l='Blue', parent=wrap_opt_menu_r_color)
    # cmds.menuItem(l='Yellow', parent=wrap_opt_menu_r_color)

def _setWrapButtonCommand(wrap_button, **kwargs):
    """ Helper to connect the 'Wrap' button """
    return cmds.button(
        wrap_button, edit=True,
        command=lambda *args: action_run.runWrap(**kwargs)
    )
