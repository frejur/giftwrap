import maya.cmds as cmds
from enum import Enum, auto
from .ribbon_points import getRibbonPoints

# Constants
_PROF_SUFFIX_1D = 'ribbon_1D_profile_'
_FLAT = 2
_SIDE_MAPPINGS_1_2 = {
    '1U': ['U', 'B', 'D'], '1D': ['U', 'F', 'D'],
    '2L': ['D', 'L', 'U'], '2R': ['D', 'R', 'U']
}

class RibbonType(Enum):
    FLAT = auto()
    SQUARE = auto()
    ROUND = auto()

class Ribbon:
    def __init__(self, obj_width, obj_height, obj_depth, paper_thickness,
                 ribbon_thickness, ribbon_width, wrap_id):
        """
        An extruded Nurbs surface that can be animated as it extends along the
        sides of the gift and ties two loops and a knot at the top.

        Args:
            obj_width:        The width of the object in maya units.
            obj_height:       The height of the object in maya units.
            obj_depth:        The depth of the object in maya units.
            paper_thickness:  The thickness of the paper in maya units.
            ribbon_thickness: The thickness of the ribbon in maya units.
            ribbon_width:     The width of the ribbon in maya units.
            wrap_id:          The unique identifier for the Wrapper object.
        """
        self.object_width = obj_width
        self.object_height = obj_height
        self.object_depth = obj_depth
        self.paper_thickness = paper_thickness
        self.ribbon_thickness = ribbon_thickness
        self.ribbon_width = ribbon_width
        self.wrap_id = wrap_id
        self.points = getRibbonPoints(self.object_width, self.object_height,
                                      self.object_depth, self.paper_thickness,
                                      self.ribbon_thickness, self.ribbon_width)
        self.profile_type = RibbonType.SQUARE # TODO: Enable more profiles

        # Paths
        self.paths = {}
        for ribbon_id in ['1U', '1D', '2L', '2R', '3L', '3R', '4']:
            self.paths[ribbon_id] = self._createCrv(ribbon_id)

        # Profile curves
        self.profiles = {'1D': self._createProfileCrv()}
        cmds.xform(self.profiles['1D'], centerPivots=True)
        xyz_U = self.points['U']
        cmds.move(xyz_U.x, xyz_U.y, xyz_U.z, self.profiles['1D'])
        for prof_id in ['1U', '2R', '2L', '3L', '3R', '4']:
            self.profiles[prof_id] = self._createProfileCrvInstance(prof_id)

        # Slightly offset rotation of Bow profile and paths
        BOW_ROT = 5
        cmds.rotate(0, -BOW_ROT, 0, self.paths['3L'], relative=True)
        cmds.rotate(0, -BOW_ROT, 0, self.profiles['3L'], relative=True)
        cmds.rotate(0, BOW_ROT, 0, self.paths['3R'], relative=True)
        cmds.rotate(0, BOW_ROT, 0, self.profiles['3R'], relative=True)

        for ribbon_id in ['1D', '1U', '2R', '2L', '3L', '3R', '4']:
            self._createExtrusion(ribbon_id)

    # ==========================================================================
    # Getters
    # ==========================================================================

    def getProfile(self):
        return self.profiles['1D']

    def getPath(self, path_id):
        return self.paths[path_id]

    # ==========================================================================
    # Helpers for the creation of curves
    # ==========================================================================

    def _createProfileCrv(self):
        """
        Creates the NURBS curve that will be used as a profile for the ribbon
        extrusion.

        Returns:
            The path to the profile curve.
        """
        if self.profile_type == RibbonType.ROUND:
            # Circle
            transform_node, _ = (
                cmds.circle(n=f'{_PROF_SUFFIX_1D}_{self.wrap_id}')
            )
            cmds.move(self.ribbon_width / 2, self.ribbon_thickness / 2, 0,
                      f'{transform_node}.cv[0]')
            cmds.move(self.ribbon_width / 2, 0, 0,
                      transform_node + '.cv[6]')
            cmds.move(self.ribbon_width / 2, -(self.ribbon_thickness / 2), 0,
                      transform_node + '.cv[7]')
            cmds.move(0, self.ribbon_thickness / 2, 0,
                      transform_node + '.cv[1]')
            cmds.move(-(self.ribbon_width / 2), self.ribbon_thickness / 2, 0,
                      transform_node + '.cv[2]')
            cmds.move(-(self.ribbon_width / 2), 0, 0,
                      transform_node + '.cv[3]')
            cmds.move(-(self.ribbon_width / 2), -(self.ribbon_thickness / 2), 0,
                      transform_node + '.cv[4]')
            cmds.move(0, -(self.ribbon_thickness/2), 0,
                      transform_node + '.cv[5]')
        else:
            # Square
            transform_node, _ = (
                cmds.circle(n=f'{_PROF_SUFFIX_1D}_{self.wrap_id}',
                            sections=4, degree=1,
                            radius=self.ribbon_width / 2)
            )
            cmds.xform(transform_node, rotation=[0, 0, 45])
            cmds.makeIdentity(transform_node, apply=True)
            cmds.xform(transform_node, scale=[1, self.ribbon_thickness, 1])
            cmds.makeIdentity(transform_node, apply=True)

        return transform_node

    def _createCrv(self, ribbon_id):
        """
        Creates the NURBS curve that will be used as the path of extrusion for
        the given ribbon ID.

        Args:
            ribbon_id: The ribbon ID (See 'ribbon_points.py' for details)
        Returns:
            The path to the shape node of the created NURBS curve.
        """

        if ribbon_id in _SIDE_MAPPINGS_1_2:
            s_0, s_1, s_2 = _SIDE_MAPPINGS_1_2[ribbon_id]
            s_0_1, s_1_0, s_1_2, s_2_1 = (
                f'{s_0}{s_1}', f'{s_1}{s_0}', f'{s_1}{s_2}', f'{s_2}{s_1}')

            point_keys = [
                s_0,           f'{s_0_1}mid', f'{s_0_1}end', f'{s_0_1}',
                f'{s_1_0}',    f'{s_1_0}end', f'{s_1_0}mid', s_1,
                f'{s_1_2}mid', f'{s_1_2}end', f'{s_1_2}',    f'{s_2_1}',
                f'{s_2_1}end', f'{s_2_1}mid', s_2]

            crv_list = [tuple(self.points[key]) for key in point_keys]
        elif ribbon_id in ['3L', '3R']:
            crv_list = []
            prefix = 'bow_L' if ribbon_id[1] == 'L' else 'bow_R'
            num_pts = 7      if ribbon_id[1] == 'L' else 6
            for i in range(1, num_pts + 1):
                crv_list.append(tuple(self.points[f'{prefix}{i}']))
        elif ribbon_id == '4':
            crv_list = []
            prefix = 'knot_'
            num_pts = 5
            for i in range(1, num_pts + 1):
                crv_list.append(tuple(self.points[f'{prefix}{i}']))
        else:
            raise ValueError('Invalid ribbon ID')

        return cmds.curve(p=crv_list,
                          n =f'ribbon_{ribbon_id}_path_{self.wrap_id}')

    def _createProfileCrvInstance(self, profile_id):
        """
        Creates an instance of the main NURBS profile curve and places
        it correctly depending on the supplied ribbon ID.

        Args:
            profile_id: The profile curve ID.

        Returns:
            The path to the instanced profile curve.
        """
        if not '1D' in self.profiles:
            raise ValueError('Cannot create instance of \'1D\' before its '
                             'creation')

        if not profile_id in ['1U', '2L', '2R', '3L', '3R', '4']:
            raise ValueError(f'Invalid profile ID \'{profile_id}\'')

        inst, = cmds.instance(self.profiles['1D'],
                              n=f'ribbon_{profile_id}_profile_{self.wrap_id}')

        if profile_id == '1U':
            cmds.setAttr(f'{inst}.rotateY', 180)
        elif profile_id in ['2R', '3R']:
            cmds.setAttr(f'{inst}.rotateY', 90)
            if profile_id == '2R':
                cmds.setAttr(f'{inst}.translateY', self.points['D'].y)
        elif profile_id in ['2L', '3L']:
            cmds.setAttr(f'{inst}.rotateY', -90)
        elif profile_id == '4':
            cmds.setAttr(f'{inst}.translateZ', self.ribbon_width / 2)
            cmds.setAttr(f'{inst}.rotateX', -90)

        return inst

    def _createExtrusion(self, ribbon_id):
        """
            Creates a nurbs surface by extruding the indicated profile curve
            along the path of the same ID.

        Args:
            ribbon_id: The ribbon (path and profile) curve ID.

        Returns:
            The path to the extruded surface
        """
        return cmds.extrude(self.profiles[ribbon_id], self.paths[ribbon_id],
                            n=f'ribbon_ext_{ribbon_id}_{self.wrap_id}',
                            extrudeType=_FLAT, range=True)
