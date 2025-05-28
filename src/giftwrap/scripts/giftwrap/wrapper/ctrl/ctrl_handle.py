import maya.cmds as cmds

class Control_handle:
    def __init__(self, x_min, z_min, x_max, z_max, wrap_id):
        """
        A NURBS curve that serves as the Wrapper's visual control handle, but
        also contains attributes related to the Wrapper instance and its
        current state.

        Args:
            x_min:   The front left corner X-coordinate for the unwrapped paper.
            z_min:   The front left corner Z-coordinate for the unwrapped paper.
            x_max:   The back right corner X-coordinate for the unwrapped paper.
            z_max:   The back right corner Z-coordinate for the unwrapped paper.
            wrap_id: The unique identifier for the Wrapper object.
        """
        self.x_min = x_min
        self.z_min = z_min
        self.x_max = x_max
        self.z_max = z_max
        self.wrap_id = wrap_id
        self.handle = self._createOutlineCrv()


    # ==========================================================================
    # Helpers
    # ==========================================================================

    def _createOutlineCrv(self):
        CTRL_WIDTH = self.x_max - self.x_min
        CTRL_DEPTH = self.z_max - self.z_min
        PAD = CTRL_WIDTH * 0.1 if CTRL_WIDTH > CTRL_DEPTH else CTRL_DEPTH * 0.1
        outline, _ = cmds.circle(n=f'CTRL_wrapper_{self.wrap_id}',
                                 sections=8, degree=1)
        cv_positions = [
            (self.x_max + PAD, 0, self.z_min),
            (self.x_max,       0, self.z_min - PAD),
            (self.x_min,       0, self.z_min - PAD),
            (self.x_min - PAD, 0, self.z_min),
            (self.x_min - PAD, 0, self.z_max),
            (self.x_min,       0, self.z_max + PAD),
            (self.x_max,       0, self.z_max + PAD),
            (self.x_max + PAD, 0, self.z_max),
            (self.x_max + PAD, 0, self.z_min),  # Close the curve
        ]
        for i, pos in enumerate(cv_positions):
            cmds.move(*pos, f'{outline}.cv[{i}]',
                      absolute=True, worldSpace=True)

        return outline
