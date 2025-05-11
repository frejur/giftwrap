from ..core import GiftWrap
from . import _const
from ._layout import layout_batch, layout_wrap

import maya.cmds as cmds
import re
import itertools

def windowUI():
    # Create main window and layout
    if cmds.window(_const.WIN_NAME, exists=True):
        cmds.deleteUI(_const.WIN_NAME)
    my_window = cmds.window(
        _const.WIN_NAME, title='Gift Wrapper',
        rtf=True, s=False
    )


    main_layout = cmds.columnLayout(rs=_const.ROW_SP)

    layout_wrap.create(main_layout)

    # --------------------------------------------------------------------------
    # Batch Edit and Export section
    #
    mod_frame = cmds.frameLayout(label='Modify Wrap', parent=main_layout,
                               width=_const.WIN_W, collapsable=True, collapse=True)

    # Modify layout
    mod_layout = cmds.columnLayout(rs=_const.COL_SP, parent=mod_frame)

    # Scan buttons row
    mod_row_scan_btn = cmds.rowLayout(numberOfColumns=3,
                                    columnWidth3=(15, _const.WIN_W / 2 - 15,
                                                  _const.WIN_W / 2 - 10),
                                    parent=mod_frame)
    cmds.text('', parent=mod_row_scan_btn)
    mod_btn_scan_sel = cmds.button(label='Scan selection', width=120,
                                 parent=mod_row_scan_btn)
    mod_btn_scan_scn = cmds.button(label='Scan scene', width=100,
                                 parent=mod_row_scan_btn)

    # Info text
    cmds.text(
        label='Scans for gifts that have already been wrapped',
        font='obliqueLabelFont', align='center', width=_const.WIN_W, parent=mod_layout
    )
    cmds.separator(height=10, width=_const.WIN_W, style='in', parent=mod_layout)
    cmds.text(label=' Result:', font='smallBoldLabelFont', parent=mod_layout)

    # Results list
    mod_txt_list = cmds.textScrollList(numberOfRows=8, allowMultiSelection=True,
                                     width=_const.WIN_W - 5, height=150,
                                     font='smallFixedWidthFont',
                                     parent=mod_layout)

    # Paper weight section
    cmds.text(label=' Paper Weight:', font='smallBoldLabelFont', parent=mod_layout)
    mod_row_pweight = cmds.rowLayout(
        numberOfColumns=2, columnWidth2=(200, 100), parent=mod_layout
    )
    mod_sld_thk = cmds.floatSliderGrp(minValue=0.005, maxValue=0.05, value=0.02,
                                    field=True, width=180, precision=3,
                                    columnWidth2=(50, 130),
                                    parent=mod_row_pweight)
    mod_btn_pweight = cmds.button(label='Edit', width=80, parent=mod_row_pweight)

    cmds.separator(height=10, width=_const.WIN_W, style='in', parent=mod_layout)

    # Color header row
    mod_row_color_hdr = cmds.rowLayout(
        numberOfColumns=3, columnWidth3=(100, 100, 80), parent=mod_layout
    )
    cmds.text(label=' Paper color:', font='tinyBoldLabelFont',
            parent=mod_row_color_hdr)
    cmds.text(label='Ribbon color:', font='tinyBoldLabelFont',
            parent=mod_row_color_hdr)
    cmds.text(' ', parent=mod_row_color_hdr)

    # Color options row
    mod_row_color = cmds.rowLayout(
        numberOfColumns=3, columnWidth3=(100, 100, 80), parent=mod_layout
    )
    mod_opt_menu_p_color = cmds.optionMenu(parent=mod_row_color)
    cmds.menuItem(label='Random', parent=mod_opt_menu_p_color)
    cmds.menuItem(label='Red', parent=mod_opt_menu_p_color)
    cmds.menuItem(label='Green', parent=mod_opt_menu_p_color)
    cmds.menuItem(label='Blue', parent=mod_opt_menu_p_color)
    cmds.menuItem(label='Yellow', parent=mod_opt_menu_p_color)
    cmds.menuItem(label='Black', parent=mod_opt_menu_p_color)
    cmds.menuItem(label='White', parent=mod_opt_menu_p_color)
    cmds.menuItem(label='Current', parent=mod_opt_menu_p_color)

    mod_opt_menu_r_color = cmds.optionMenu(parent=mod_row_color)
    cmds.menuItem(label='Random', parent=mod_opt_menu_r_color)
    cmds.menuItem(label='Red', parent=mod_opt_menu_r_color)
    cmds.menuItem(label='Green', parent=mod_opt_menu_r_color)
    cmds.menuItem(label='Blue', parent=mod_opt_menu_r_color)
    cmds.menuItem(label='Yellow', parent=mod_opt_menu_r_color)
    cmds.menuItem(label='Current', parent=mod_opt_menu_r_color)

    mod_btn_color = cmds.button(label='Edit', width=80, parent=mod_row_color)

    # Separator
    cmds.setParent(mod_layout)
    cmds.separator(height=10, width=_const.WIN_W, style='in')
    cmds.text(label=' Ribbon size:', font='tinyBoldLabelFont')

    # Ribbon size row
    mod_row_r_sz = cmds.rowLayout(numberOfColumns=2, columnWidth2=(200, 80))
    mod_radio_r_sz = cmds.radioButtonGrp(labelArray3=['Small', 'Medium', 'Large'],
                                       numberOfRadioButtons=3,
                                       columnWidth3=(60, 60, 60),
                                       select=3, parent=mod_row_r_sz)
    mod_btn_r_sz = cmds.button(label='Edit', width=80, parent=mod_row_r_sz)

    # Separator
    cmds.setParent(mod_layout)
    cmds.separator(height=10, width=_const.WIN_W, style='in')

    # Animation header row
    mod_row_anim_hdr = cmds.rowLayout(numberOfColumns=3,
                                    columnWidth3=(100, 100, 80))
    cmds.text(label=' Anim. start:', font='tinyBoldLabelFont',
            parent=mod_row_anim_hdr)
    cmds.text(label='Anim. end:', font='tinyBoldLabelFont',
            parent=mod_row_anim_hdr)
    cmds.text(' ', parent=mod_row_anim_hdr)

    # Animation fields row
    cmds.setParent(mod_layout)
    mod_row_anim = cmds.rowLayout(numberOfColumns=3, columnWidth3=(100, 100, 80))
    mod_int_anim_s = cmds.intField(minValue=0, width=45, value=1,
                                 parent=mod_row_anim)
    mod_int_anim_e = cmds.intField(minValue=0, width=45, value=24,
                                 parent=mod_row_anim)
    mod_btn_anim = cmds.button(label='Edit', width=80, parent=mod_row_anim)

    cmds.button(mod_btn_scan_sel, edit=True,
              command=lambda *args: scanForWraps(mod_txt_list, True))

    cmds.button(mod_btn_scan_scn, edit=True,
              command=lambda *args: scanForWraps(mod_txt_list, False))

    cmds.button(mod_btn_pweight, edit=True,
              command=lambda *args: editPaperWeight(mod_txt_list, mod_sld_thk))

    cmds.button(mod_btn_color, edit=True,
              command=lambda *args: editColors(mod_txt_list,
                                               mod_opt_menu_p_color,
                                               mod_opt_menu_r_color))

    cmds.button(mod_btn_r_sz, edit=True,
              command=lambda *args: editRibbonSize(mod_txt_list,
                                                   mod_radio_r_sz))

    cmds.button(mod_btn_anim, edit=True,
              command=lambda *args: editAnimation(mod_txt_list, mod_int_anim_s,
                                                  mod_int_anim_e))

    cmds.textScrollList(mod_txt_list, edit=True,
                      selectCommand=lambda *args: deselectHeader(mod_txt_list))

    # Reset size to fit elements
    cmds.window(my_window, e=True, w=_const.WIN_W, h=1)

    # Show window
    cmds.showWindow(my_window)


def deselectHeader(txt_list):
    cmds.textScrollList(txt_list, edit=True, deselectIndexedItem=[1, 2])




def scanForWraps(txt_list, _scan_mode, selection=None):
    global wrap_list

    _scan_mode = None  # TODO: Implement `scan_mode`

    if selection is None:
        all_transforms = cmds.ls(type='transform')
        p_grp = re.compile('^.*_gift_wrap_[0-9A-Z]{5}_GRP$')
        p_ctrl = re.compile('^CTRL_gift_[0-9A-Z]{5}$')

        all_groups = filter(p_grp.match, all_transforms)
        all_children = map(
            lambda g: cmds.listRelatives(g, type='transform') or [], all_groups)
        wrap_list = list(
            filter(p_ctrl.match, itertools.chain.from_iterable(all_children)))

    cmds.textScrollList(txt_list, edit=True, removeAll=True)

    # Titles
    col1_title = addPadding('Object', 1)
    col2_title = addPadding('ID', 2)
    col3_title = addPadding('P. Weight', 3)
    col4_title = addPadding('P. Color', 4)
    col5_title = addPadding('R. Color', 5)
    col6_title = addPadding('R. Size', 6)
    col7_title = addPadding('Animation', 7)

    if len(wrap_list) > 0:
        titles = col1_title + col2_title + col3_title + col4_title
        titles += col5_title + col6_title + col7_title
        cmds.textScrollList(txt_list, edit=True, append=[titles])

        cmds.textScrollList(txt_list, edit=True, append=[addPadding('-', 0)])

        for w in wrap_list:
            wrap = GiftWrap(w, 'load')
            wrap_name = addPadding(wrap.wrap_name, 1)
            wrap_id = addPadding(wrap.wrap_id, 2)
            paper_thickness = addPadding(str(wrap.wrap_thickness), 3)
            paper_color = addPadding(wrap.wrap_color, 4)
            ribbon_color = addPadding(wrap.ribbon_color, 5)
            ribbon_size = addPadding(wrap.ribbon_size, 6)
            animation = addPadding(
                str(wrap.animation_start) + ' - ' + str(wrap.animation_end), 7)

            attributes = wrap_name + wrap_id + paper_thickness
            attributes += paper_color + ribbon_color + ribbon_size
            attributes += animation

            cmds.textScrollList(txt_list, edit=True, append=[attributes])

        if selection is None:
            num_items = cmds.textScrollList(txt_list, query=True,
                                          numberOfItems=True) + 1
            for i in range(3, num_items):
                cmds.textScrollList(txt_list, edit=True, selectIndexedItem=i)
        else:
            for s in selection:
                cmds.textScrollList(txt_list, edit=True, selectIndexedItem=s + 3)
    else:
        cmds.textScrollList(txt_list, edit=True, append=['None found'])
        cmds.textScrollList(txt_list, edit=True, append=[addPadding(' ', 0)])


def addPadding(text, column):
    """
    Add spaces to the given text in order to
    align it properly in the scroll list.
    """
    # Column length
    col_len = [0, 18, 8, 10, 10, 10, 10, 10]  # 0 to 7

    if column == 0:
        return text[:1] * (sum(col_len) + 7)
    else:
        text = text[:col_len[column]]
        padding = col_len[column] - len(text)
        text += ' ' * (padding + 1)

        return text


def editPaperWeight(txt_list, p_weight):
    selection = removeHeader(txt_list)

    wrap_thickness = cmds.floatSliderGrp(p_weight, query=True, value=True)

    if selection is not None:
        for s in selection:
            edit_gift = GiftWrap(wrap_list[s], 'load')
            edit_gift.wrap_thickness = wrap_thickness
            edit_gift.reloadGiftWrap()
            wrap_list[s] = edit_gift.ctrl_handle[0]

        scanForWraps(txt_list, 0, selection)


def editColors(txt_list, p_color, r_color):
    selection = removeHeader(txt_list)

    wrap_color = cmds.optionMenu(p_color, query=True, value=True).lower()
    ribbon_color = cmds.optionMenu(r_color, query=True, value=True).lower()

    if selection is not None:
        for s in selection:
            edit_gift = GiftWrap(wrap_list[s], 'load')
            edit_gift.newColor(wrap_color, ribbon_color)

        scanForWraps(txt_list, 0, selection)  # Refresh scroll list


def editRibbonSize(txt_list, r_size):
    selection = removeHeader(txt_list)

    r_size_value = cmds.radioButtonGrp(r_size, query=True, select=True)

    if r_size_value == 1:
        ribbon_size = 'S'
    elif r_size_value == 2:
        ribbon_size = 'M'
    else:
        ribbon_size = 'L'

    if selection is not None:
        for s in selection:
            edit_gift = GiftWrap(wrap_list[s], 'load')
            edit_gift.changeRibbon(ribbon_size)

        scanForWraps(txt_list, 0, selection)


def editAnimation(txt_list, anim_s, anim_e):
    selection = removeHeader(txt_list)

    animation_start = cmds.intField(anim_s, query=True, value=True)
    animation_end = cmds.intField(anim_e, query=True, value=True)

    if selection is not None:
        for s in selection:
            edit_gift = GiftWrap(wrap_list[s], 'load')

            edit_gift.setAnimation(animation_start, animation_end)

        scanForWraps(txt_list, 0, selection)  # Refresh scroll list


def removeHeader(txt_list):
    """
    Remove header from the selection so that it
    corresponds to the wrap_list.
    """
    hdr_rows = 2  # Number of header rows

    items = cmds.textScrollList(txt_list, query=True, selectIndexedItem=True)

    if not items:
        return None
    else:
        gifts = [((hdr_rows + 1) * -1) + item for item in items]
        return gifts

