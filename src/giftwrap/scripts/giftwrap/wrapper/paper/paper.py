import maya.cmds as cmds
from .folding_pattern import FoldingPattern
from .folding_plane import FoldingPlane
from .mesh import PaperMesh
from .clusters import Clusters

from ...globals.constants import *

class Paper:
    def __init__(self, obj_width, obj_height, obj_depth, p_thickness, wrap_id):
        """
        A collection of paper objects used to wrap any object with the specified
        dimensions.

        Args:
            obj_width:   The width of the object in maya units
            obj_height:  The height of the object in maya units
            obj_depth:   The depth of the object in maya units
            p_thickness: The thickness of the paper mesh in maya units
            wrap_id:     The unique identifier for the Wrapper object.
        """
        self.object_width = obj_width
        self.object_height = obj_height
        self.object_depth = obj_depth
        self.thickness = p_thickness
        self.wrap_id = wrap_id

        self.fold_number = self._validFoldNumber(0)

        # Value used to slightly offset the x value of some of the fold clusters
        # to prevent them from acting up
        self.fold_fix = self.object_depth / 113

        self.pattern = FoldingPattern(
            self.object_width, self.object_height, self.object_depth,
            self.thickness
        )
        self.mesh = None
        self.folding_plane = FoldingPlane(self.pattern, self.wrap_id)
        self.mesh = PaperMesh(self.folding_plane, self.thickness, self.wrap_id)

        # Create Wrap Deformer (Paper mesh conforms to Folding plane)
        cmds.select(clear=True)
        cmds.select(self.mesh.getTransformNode(),
                    self.folding_plane.getTransformNode())
        cmds.CreateWrap()

        self.clusters = Clusters(self.pattern, self.folding_plane,
                                 self.mesh, self.wrap_id)

        # Group
        self.paper_group = cmds.group(name=f'GRP_gift_{wrap_id}_paper',
                                      empty=True)
        cmds.parent(self.folding_plane.getTransformNode(), self.paper_group)
        cmds.parent(self.mesh.getTransformNode(), self.paper_group)
        cmds.parent(self.clusters.getMainGroup(), self.paper_group)

        # for i in range(17):
        #     self.setFoldNumber(i)
        #     dup_plane = cmds.duplicate(self.folding_plane.getTransformNode())
        #     dup_mesh = cmds.duplicate(self.mesh.getTransformNode())
        #     for j in range(2):
        #         cmds.xform([dup_plane, dup_mesh][j - 1],
        #                    translation=[
        #                        i * (self.object_width + self.object_height * 2)
        #                        * 1.1,
        #                        0,
        #                        (self.object_height + self.object_depth)
        #                        * j * 1.2],
        #                    worldSpace=True)
        #
        # self.setFoldNumber(0)


    # Setters ==================================================================

    def setFoldNumber(self, fold_number):
        """
        Sets the internal fold number, which wraps / unwraps the gift by
        rotating and translating the clusters of the folding plane.

        Args:
            fold_number: The fold number
        """
        self.fold_number = self._validFoldNumber(fold_number)

        if fold_number >= 1:
            self._setClusterRotate('1B', x=-90)
        if fold_number >= 2:
            self._setClusterRotate('2B', x=-90)
        if fold_number >= 3:
            self._setClusterRotate('1U', x=90)
        if fold_number >= 4:
            self._setClusterRotate('2U', x=89.8)
        if fold_number >= 5:
            self._setClusterRotate('3UL', x=178.8)
            self._setClusterTranslate('3UL', x=self.fold_fix, y=0, z=0)
        if fold_number >= 6:
            self._setClusterRotate('3BL', x=178)
            self._setClusterTranslate('3BL', x=self.fold_fix * -1, y=0, z=0)
        if fold_number >= 7:
            self._setClusterRotate('3UR', x=178)
            self._setClusterTranslate('3UR', x=self.fold_fix * -1, y=0, z=0)
        if fold_number >= 8:
            self._setClusterRotate('3BR', x=178)
            self._setClusterTranslate('3BR', x=self.fold_fix, y=0, z=0)
        if fold_number >= 9:
            self._setClusterRotate('4UL', x=178)
        if fold_number >= 10:
            self._setClusterRotate('4BL', x=178)
        if fold_number >= 11:
            self._setClusterRotate('4UR', x=178)
        if fold_number >= 12:
            self._setClusterRotate('4BR', x=178)
        if fold_number >= 13:
            self._setClusterRotate('5L', z=86)
        if fold_number >= 14:
            self._setClusterRotate('5R', z=-86)
        if fold_number >= 15:
            self._setClusterRotate('6L', z=-84)
        if fold_number >= 16:
            self._setClusterRotate('6R', z=84)
        if fold_number == 0:
            self._setClusterRotate('1B', x=0, y=0, z=0)
        if fold_number < 2:
            self._setClusterRotate('2B', x=0, y=0, z=0)
        if fold_number < 3:
            self._setClusterRotate('1U', x=0, y=0, z=0)
        if fold_number < 4:
            self._setClusterRotate('2U', x=0, y=0, z=0)
        if fold_number < 5:
            self._setClusterRotate('3UL', x=0, y=0, z=0)
            self._setClusterTranslate('3UL', x=0, y=0, z=0)
        if fold_number < 6:
            self._setClusterRotate('3BL', x=0, y=0, z=0)
            self._setClusterTranslate('3BL', x=0, y=0, z=0)
        if fold_number < 7:
            self._setClusterRotate('3UR', x=0, y=0, z=0)
            self._setClusterTranslate('3UR', x=0, y=0, z=0)
        if fold_number < 8:
            self._setClusterRotate('3BR', x=0, y=0, z=0)
            self._setClusterTranslate('3BR', x=0, y=0, z=0)
        if fold_number < 9:
            self._setClusterRotate('4UL', x=0, y=0, z=0)
        if fold_number < 10:
            self._setClusterRotate('4BL', x=0, y=0, z=0)
        if fold_number < 11:
            self._setClusterRotate('4UR', x=0, y=0, z=0)
        if fold_number < 12:
            self._setClusterRotate('4BR', x=0, y=0, z=0)
        if fold_number < 13:
            self._setClusterRotate('5L', x=0, y=0, z=0)
        if fold_number < 14:
            self._setClusterRotate('5R', x=0, y=0, z=0)
        if fold_number < 15:
            self._setClusterRotate('6L', x=0, y=0, z=0)
        if fold_number < 16:
            self._setClusterRotate('6R', x=0, y=0, z=0)

    # Getters ==================================================================

    def getGroup(self):
        return self.paper_group

    def getFoldingPlane(self):
        return self.folding_plane.getTransformNode()

    def getFoldPointPosition(self, fold_point):
        return self.pattern.point(fold_point)

    def getUnwrappedFrontLeftCorner(self):
        if self.pattern.hasOverlappingFolds():
            return self.pattern.point('F7')
        else:
            return self.pattern.point('F8')

    def getUnwrappedBackRightCorner(self):
        return self.pattern.point('I1')

    # Helpers ==================================================================

    @staticmethod
    def _validFoldNumber(fold_number):
        if fold_number <FOLD_MIN or fold_number > FOLD_MAX:
            raise AttributeError('Fold number out of range')
        return fold_number

    def _getClusterPath(self, cluster_id):
        return (
            self.clusters.getClusterHandle(cluster_id)
            if (cluster_id[0] != '3' and cluster_id[0] != '4')
            else self.clusters.getPivotLocator(cluster_id)
        )

    def _setClusterTranslate(self, cluster_id, x=None, y=None, z=None):
        base_path = f'{self._getClusterPath(cluster_id)}.translate'

        for key, value in {'X': x, 'Y': y, 'Z': z}.items():
            if value is not None:
                cmds.setAttr(f'{base_path}{key}', value)

    def _setClusterRotate(self, cluster_id, x=None, y=None, z=None):
        base_path = f'{self._getClusterPath(cluster_id)}.rotate'

        for key, value in {'X': x, 'Y': y, 'Z': z}.items():
            if value is not None:
                cmds.setAttr(f'{base_path}{key}', value)


