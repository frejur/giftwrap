from .tweak import *
from ..utils import (
    Scoped_layout
)
from ...layout_constants import *


class Fine_tuning_controls:
    """
    Creates the controls used to tweak Animation and Color attributes.
    A 2-column layout, the first one being empty to serve as padding / indent.
    The layout contains collapsible sections defined externally.
    """
    def __init__(self):
        self.coordinate_space       = None
        self.up_axis                = None
        self.invert_up              = None
        self.object_placement_label = None
        self.object_placement_menu  = None
        self.knot_placement         = None
        self.paper_color            = None
        self.ribbon_color           = None

        cmds.text(l=' Fine tuning', font=FNT_SM)

        with Scoped_layout(
                cmds.rowLayout(
                    numberOfColumns=2,
                    columnWidth2=COLS_TWEAK
                )
        ) as row_orientation_and_placement:
            cmds.text('') # Left padding / indent
            self.create_orientation_and_placement_section()

        with Scoped_layout(
                cmds.rowLayout(
                    numberOfColumns=2,
                    columnWidth2=COLS_TWEAK
                )
        ) as row_colors:
            cmds.text('') # Left padding / indent
            self.create_color_section()

    def create_orientation_and_placement_section(self):
        """ Implementation in tweak/layout_orient_placemt.py """

    def create_color_section(self):
        """ Implementation in tweak/layout_colors.py """

# Redefine member function to implementations in external files
Fine_tuning_controls.create_orientation_and_placement_section = (
    create_orientation_and_placement_section
)
Fine_tuning_controls.create_color_section = create_color_section
