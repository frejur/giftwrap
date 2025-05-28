import maya.cmds as cmds

from .layout_constants import *
from .layout import layout_modify_export, layout_wrap
from .actions import action_run
from ..globals.parameters import *
from ..wrapper import WrapperMode


# def windowUI(debug=False):
# DEBUG BEGIN ==================================================================
def windowUI(debug=False):
# DEBUG BREAK ==================================================================
    # ==========================================================================
    # Layout
    if cmds.window(WIN_NAME, exists=True):
        cmds.deleteUI(WIN_NAME)
    my_window = cmds.window(
        WIN_NAME, title='giftwrap',
        resizeToFitChildren=False, sizeable=False,
        w=WIN_W
    )

    main_layout = cmds.columnLayout(rs=ROW_SP)

    # DEBUG BEGIN ==============================================================
    debug_btn  = None
    if debug:
        debug_btn = cmds.button(l='Debug Wrap', p=main_layout)
    # DEBUG BREAK ==============================================================

    new = layout_wrap.create(main_layout)
    layout_modify_export.create(main_layout)

    cmds.window(my_window, e=True, w=WIN_W, h=1) # Reset size to fit vertically
    cmds.showWindow(my_window)
    # ==========================================================================
    # Callbacks

    # Use-plane toggle deactivates the paper thickness slider
    cmds.checkBox(
        new.paper_and_ribbon.use_plane, edit=True,
        changeCommand=lambda *args: _toggle_use_plane(
            new.paper_and_ribbon.paper_thickness,
            new.paper_and_ribbon.use_plane
        )
    )

    # Object placement controls are active / deactivated depending on
    _setup_dynamic_object_placement_control(
        [new.tweaks.up_axis, new.tweaks.object_placement_menu],
        new.anim_and_wrap.animate_placement,
        new.tweaks.up_axis,
        new.tweaks.object_placement_label,
        new.tweaks.object_placement_menu,
        initialize=True
    )

    # The Wrap Button creates new Wrapper instances from the current selection
    AW = new.anim_and_wrap; PR = new.paper_and_ribbon; TW = new.tweaks
    button_kwargs = {
        Parm.WRAPPER_MODE.name.lower():      WrapperMode.CREATE,
        Parm.KEEP_ORIGINAL.name.lower():     AW.keep_original,
        Parm.PAPER_THICKNESS.name.lower():   PR.paper_thickness,
        Parm.PAPER_USE_PLANE.name.lower():   PR.use_plane,
        Parm.PAPER_COLOR.name.lower():       TW.paper_color,
        Parm.RIBBON_WIDTH.name.lower():      PR.ribbon_width,
        Parm.RIBBON_COLOR.name.lower():      TW.ribbon_color,
        Parm.RIBBON_THICKNESS.name.lower():  PR.ribbon_thickness,
        Parm.ANIM_START_FRAME.name.lower():  AW.start_frame,
        Parm.ANIM_END_FRAME.name.lower():    AW.end_frame,
        Parm.ANIMATE_PLACEMENT.name.lower(): AW.animate_placement,
        Parm.ANIMATE_GIFT_FLIP.name.lower(): AW.animate_gift_flip,
        Parm.COORDINATE_SPACE.name.lower():  TW.coordinate_space,
        Parm.UP_AXIS.name.lower():           TW.up_axis,
        Parm.AUTO_PLACE_OBJECT.name.lower(): TW.object_placement_menu,
        Parm.KNOT_PLACEMENT.name.lower():    TW.knot_placement,
    }

    cmds.button(
        new.anim_and_wrap.wrap_button, edit=True,
        command=lambda *args: action_run.runWrap(**button_kwargs)
    )

    # DEBUG BEGIN ==============================================================
    if debug:
        cmds.button(
            debug_btn, edit=True,
            command=lambda *args: action_run.runWrapDebug(**button_kwargs)
        )
    # DEBUG BEGIN ==============================================================


def _toggle_use_plane(paper_thickness_slider,
                      use_plane_toggle):
    """
    Deactivate the paper thickness slider when the checkbox for using
    only a plane is ticked.
    """
    cmds.floatSlider(
        paper_thickness_slider,
        edit=True,
        enable=(not cmds.checkBox(use_plane_toggle, query=True, value=True))
    )

def _setup_dynamic_object_placement_control(controls,
                                            anim_toggle, up_axis_menu,
                                            placemt_label, placemt_menu,
                                            initialize=False):
    """
    Adds callbacks to the given controls so that they may be dynamically
    activate / deactivated.
    """
    for c in controls:
        cmds.optionMenu(
            c,
            edit=True,
            changeCommand=(
                lambda *args: _update_object_placement_menu(
                    anim_toggle,
                    up_axis_menu,
                    placemt_label,
                    placemt_menu
                )
            )
        )
    if initialize:
        _update_object_placement_menu(anim_toggle, up_axis_menu,
                                      placemt_label, placemt_menu)

def _update_object_placement_menu(anim_toggle, up_axis_menu,
                                  placemt_label, placemt_menu):
    """
    Callback function that toggles the active / inactive status of the
    object placement controls.
    """
    auto_placement_possible = (
            cmds.optionMenu(up_axis_menu, query=True, value=True)
            != OPT[P_Opt.USE_LARGEST_SIDE_UP]
    )
    auto_placement_selected = (
            cmds.optionMenu(placemt_menu, query=True, value=True)
            == OPT[P_Opt.PLACE_LARGEST_SIDE_DOWN]
    )
    cmds.checkBox(anim_toggle, edit=True,
                  enable=(auto_placement_possible and auto_placement_selected))
    cmds.text(placemt_label, edit=True, enable=auto_placement_possible)
    cmds.optionMenu(placemt_menu, edit=True, enable=auto_placement_possible)

