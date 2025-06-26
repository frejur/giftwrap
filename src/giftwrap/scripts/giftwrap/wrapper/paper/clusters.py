from _ast import pattern
from copy import deepcopy

import maya.cmds as cmds
from .pivots import calculateFoldingPivots
from ...utils.custom_types.vec import Vec

class Clusters:
    def __init__(self, folding_pattern, folding_plane, paper_mesh, wrap_id):
        self.pattern = folding_pattern
        self.plane = folding_plane
        self.plane_transform = folding_plane.getTransformNode()
        self.mesh = paper_mesh
        self.mesh_transform = paper_mesh.getTransformNode()
        self.wrap_id = wrap_id
        self.pivot_xyz = calculateFoldingPivots(self.pattern)
        self.handles = {}        # Used to store paths to cluster handles
        self.pivot_locators = {} # Used to store paths to cluster pivot locators
        self.cluster_groups = {} # Used to store paths to cluster-locator groups

        # Create lists of rows of vertices to include in clusters
        vertices_row_1 = self._getVerticesForRow(1)
        vertices_row_2 = self._getVerticesForRow(2)
        vertices_row_6 = self._getVerticesForRow(6)
        vertices_row_7 = self._getVerticesForRow(7)
        vertices_row_8 = self._getVerticesForRow(8) \
                         if not self.pattern.hasOverlappingFolds() \
                         else []

        vertices_row_1_flaps = self._getVerticesFromPoints(['F1a', 'I1a'])
        vertices_row_1_flaps_overlap = \
            self._getVerticesFromPoints(['F1b', 'I1b', 'F1c', 'I1c']) \
            if self.pattern.hasOverlappingFolds() else []
        vertices_row_1_pad = \
            self._getVerticesFromPoints(
                ['F1u', 'I1u', 'F1d', 'I1d', 'F1s', 'I1s'])
        vertices_row_7_flaps = self._getVerticesFromPoints(['F7a', 'I7a'])
        vertices_row_7_flaps_overlap = \
            self._getVerticesFromPoints(['F7b', 'I7b']) \
            if self.pattern.hasOverlappingFolds() else []
        vertices_row_7_pad = \
            self._getVerticesFromPoints(['F7u', 'I7u', 'F7s', 'I7s'])
        vertices_row_7_pad_overlap = \
            self._getVerticesFromPoints(['F7d', 'I7d']) \
            if self.pattern.hasOverlappingFolds() else []
        vertices_row_7_pad_no_overlap = \
            self._getVerticesFromPoints(['F7m', 'I7m', 'F8d', 'I8d']) \
            if not self.pattern.hasOverlappingFolds() else []

        # 1st fold =============================================================
        # Upper
        vertices_1U = vertices_row_1 + vertices_row_2 + \
                      vertices_row_1_flaps + vertices_row_1_pad
        print(vertices_1U)
        self._addVerticesAndCreateCluster(vertices_1U, '1U',
            new_vertices_when_overlap=vertices_row_1_flaps_overlap)

        # Lower
        vertices_1B = vertices_row_6 + vertices_row_7 + \
                      vertices_row_7_flaps + vertices_row_7_pad
        self._addVerticesAndCreateCluster(vertices_1B, '1B',
            new_vertices_when_overlap=vertices_row_7_flaps_overlap + \
                                      vertices_row_7_pad_overlap,
            new_vertices_when_no_overlap=vertices_row_8 + \
                                         vertices_row_7_pad_no_overlap)

        # 2nd fold =============================================================
        vertices_2U = vertices_row_1 + vertices_row_1_flaps + vertices_row_1_pad
        self._addVerticesAndCreateCluster(vertices_2U, '2U',
            new_vertices_when_overlap=vertices_row_1_flaps_overlap)

        vertices_2B = vertices_row_7 + vertices_row_7_flaps + vertices_row_7_pad
        if not self.pattern.hasOverlappingFolds():
            vertices_2B += vertices_row_8
        self._addVerticesAndCreateCluster(vertices_2B, '2B',
            new_vertices_when_overlap=vertices_row_7_flaps_overlap + \
                                       vertices_row_7_pad_overlap,
            new_vertices_when_no_overlap=vertices_row_8 + \
                                          vertices_row_7_pad_no_overlap)

        # 3rd fold =============================================================
        vertices_3UR = [self._getVertexFromPoint('I3'),
                        self._getVertexFromPoint('I4us')]
        self._addVerticesAndCreateClusterWithPivot(vertices_3UR,
                                                   ['I4b'],
                                                   '3UR',
                                                   rotation_y=-45)

        vertices_3BR = [self._getVertexFromPoint('I5'),
                        self._getVertexFromPoint('I4ds')]
        self._addVerticesAndCreateClusterWithPivot(vertices_3BR,
                                                   ['I4a'],
                                                   '3BR',
                                                   rotation_xyz=(
                                                       Vec(180, 225, 0)))

        vertices_3UL = [self._getVertexFromPoint('F3'),
                        self._getVertexFromPoint('F4us')]
        self._addVerticesAndCreateClusterWithPivot(vertices_3UL,
                                                   ['F4b'],
                                                   '3UL',
                                                   rotation_y=45)

        vertices_3BL = [self._getVertexFromPoint('F5'),
                        self._getVertexFromPoint('F4ds')]
        self._addVerticesAndCreateClusterWithPivot(vertices_3BL,
                                                   ['F4a'],
                                                   '3BL',
                                                   rotation_xyz=(
                                                       Vec(0, 45, 180)))

        # 4th fold =============================================================
        vertices_4UR = [self._getVertexFromPoint('I2'),
                        self._getVertexFromPoint('I1s')]
        self._addVerticesAndCreateClusterWithPivot(vertices_4UR,
                                                   ['I1b', 'I7'],
                                                   '4UR',
                                                   rotation_y=135)

        vertices_4BR = [self._getVertexFromPoint('I6'),
                        self._getVertexFromPoint('I7s')]
        self._addVerticesAndCreateClusterWithPivot(vertices_4BR,
                                                   ['I7b', 'I7', 'I1'],
                                                   '4BR',
                                                   rotation_y=45)

        vertices_4UL = [self._getVertexFromPoint('F2'),
                        self._getVertexFromPoint('F1s')]
        self._addVerticesAndCreateClusterWithPivot(vertices_4UL,
                                                   ['F1b', 'F7'],
                                                   '4UL',
                                                   rotation_y=225)

        vertices_4BL = [self._getVertexFromPoint('F6'),
                        self._getVertexFromPoint('F7s')]
        self._addVerticesAndCreateClusterWithPivot(vertices_4BL,
                                                   ['F7b', 'F7', 'F1'],
                                                   '4BL',
                                                   rotation_xyz=(
                                                       Vec(180, 225, 180)))

        # 5th fold =============================================================
        vertices_5R = self._getVerticesFromPoints(['I7', 'I1', 'I1a', 'I7a'])
        vertices_5R_when_overlap = \
            self._getVerticesFromPoints(['I7b', 'I1b', 'I1c']) \
            if self.pattern.hasOverlappingFolds() \
            else []
        vertices_5R_when_no_overlap = \
            self._getVerticesFromPoints(['I8']) \
            if self.pattern.hasOverlappingFolds() \
            else []

        self._addVerticesAndCreateCluster(vertices_5R, '5R',
            new_vertices_when_no_overlap=vertices_5R_when_no_overlap,
            new_vertices_when_overlap=vertices_5R_when_overlap)

        vertices_5L = self._getVerticesFromPoints(['F7', 'F1', 'F1a', 'F7a'])
        vertices_5L_when_overlap = \
            self._getVerticesFromPoints(['F7b', 'F1b', 'F1c']) \
                if self.pattern.hasOverlappingFolds() \
                else []
        vertices_5L_when_no_overlap = \
            self._getVerticesFromPoints(['F8']) \
                if self.pattern.hasOverlappingFolds() \
                else []

        self._addVerticesAndCreateCluster(vertices_5L, '5L',
            new_vertices_when_no_overlap=vertices_5L_when_no_overlap,
            new_vertices_when_overlap=vertices_5L_when_overlap)

        # 6th fold =============================================================
        vertices_6R = self._getVerticesFromPoints(['I4a', 'I4b'])
        vertices_6R_when_overlap = self._getVerticesFromPoints(['HI4']) \
                                   if self.pattern.hasOverlappingFolds() \
                                   else []

        self._addVerticesAndCreateCluster( vertices_6R, '6R',
            new_vertices_when_overlap=vertices_6R_when_overlap)

        vertices_6L = self._getVerticesFromPoints(['F4a', 'F4b'])
        vertices_6L_when_overlap = self._getVerticesFromPoints(['FG4']) \
            if self.pattern.hasOverlappingFolds() \
            else []

        self._addVerticesAndCreateCluster(vertices_6L, '6L',
            new_vertices_when_overlap=vertices_6L_when_overlap)

        # Grouping =============================================================

        self.main_group = cmds.group(n=f'clusters_{self.wrap_id}_grp', em=True)
        # Set inheritsTransform to make clusters stay in place
        cmds.setAttr(f'{self.main_group}.inheritsTransform', 0)

        for _, h in self.handles.items():
            cmds.parent(h, self.main_group)

        for _, grp in self.cluster_groups.items():
            cmds.parent(grp, self.main_group)

    # ==========================================================================
    # Getters
    # ==========================================================================

    def getClusterHandle(self, cluster_id):
        try:
            return self.handles[cluster_id]
        except KeyError:
            raise RuntimeError(f'Cluster handle for \'{cluster_id}\' not found')

    def getPivotLocator(self, cluster_id):
        try:
            return self.pivot_locators[cluster_id]
        except KeyError:
            raise RuntimeError(f'Pivot locator for \'{cluster_id}\' not found')

    def getMainGroup(self):
        return self.main_group

    # ==========================================================================
    # Helpers
    # ==========================================================================

    def _addVerticesAndCreateCluster(self, vertices_base,
                                     cluster_id,
                                     new_vertices_when_no_overlap=None,
                                     new_vertices_when_overlap=None):
        """
        Helper for creating clusters.

        Args:
            vertices_base:                List of vertices to use as a base.
            cluster_id:                   The cluster ID.
            new_vertices_when_no_overlap: List of new vertices to add only when
                                          folds DON't overlap.
            new_vertices_when_overlap:    List of new vertices to add only when
                                          folds overlap.

        Modifies:
            `self.handles` (See `self._addCluster`)
        """
        vertices = deepcopy(vertices_base) # TODO: Check if this is necessary

        if (not self.pattern.hasOverlappingFolds() and
            new_vertices_when_no_overlap is not None):
            vertices += new_vertices_when_no_overlap
        if (self.pattern.hasOverlappingFolds() and
            new_vertices_when_overlap is not None):
            vertices += new_vertices_when_overlap

        self._addCluster(vertices, cluster_id)

    def _addVerticesAndCreateClusterWithPivot(self, vertices_base,
                                              new_vertices_when_overlap,
                                              cluster_id,
                                              rotation_y=None,
                                              rotation_xyz=None):
        """
        Helper for creating cluster-pivot groups.

        Args:
            vertices_base:             List of vertices to use as a base.
            new_vertices_when_overlap: List of new vertices to add when folds
                                       overlap.
            cluster_id:                The cluster ID.
            rotation_y:                The rotation angle in degrees for Y.
            rotation_xyz:              The rotation angle in degrees for X,Y,Z.

        Modifies:
            `self.pivot_locators` and `self.groups`
            (See `self._addClusterWithPivot')
        """
        vertices = deepcopy(vertices_base) # TODO: Check if this is necessary

        if (self.pattern.hasOverlappingFolds() and
            new_vertices_when_overlap is not None):
            for point in new_vertices_when_overlap:
                vertices.append(self._getVertexFromPoint(point))

        if rotation_y is not None:
            self._addClusterWithPivot(vertices, cluster_id,
                                      rotation_y=rotation_y)
        else:
            self._addClusterWithPivot(vertices, cluster_id,
                                      rotation_xyz=rotation_xyz)

    def _addCluster(self, vertices, cluster_id):
        """
        Creates a cluster from the given vertice paths.

        Args:
            vertices: A list of vertex paths.
            cluster_id: The cluster ID.

        Modifies:
            Stores the new cluster handle in `self.handles`
        """
        _, new_handle = cmds.cluster(
            vertices, name=f'cluster_{cluster_id}_{self.wrap_id}'
        )
        new_handle = cmds.rename(new_handle,
                                 f'cluster_{cluster_id}_handle_{self.wrap_id}')
        cmds.xform(new_handle, rotatePivot=list(self.pivot_xyz[cluster_id]))

        if cluster_id in self.handles:
            raise ValueError(f"Duplicate cluster ID detected: {cluster_id}")

        self.handles[cluster_id] = new_handle

    def _addClusterWithPivot(self, vertices, cluster_id,
                             rotation_xyz=None, rotation_y=None):
        """
        Helper function to create a group with a cluster, and a locator
        that serves as the cluster's local pivot point.

        Args:
            vertices: A list of vertex paths.
            cluster_id: The cluster ID.
            rotation_y: The rotation angle in degrees for Y.
            rotation_xyz: The rotation angle in degrees for X,Y,Z.

        Modifies:
            Stores the pivot point locator in `self.pivot_locators`
            Stores the new group in `self.groups`
        """
        if ((rotation_xyz is None and rotation_y is None) or
            (rotation_xyz is not None and rotation_y is not None)):
            raise ValueError('Must specify either rotation_xyz or rotation_y')

        base_name = f'cluster_{cluster_id}'

        # Create locator
        pivot = cmds.spaceLocator(position=list(self.pivot_xyz[cluster_id]),
                                  name=f'{base_name}_pivot_{self.wrap_id}')[0]

        # Create group
        pivot_group = cmds.group(pivot, name=f'{base_name}_{self.wrap_id}_grp')

        # Set rotation
        if rotation_y is not None:
            cmds.setAttr(f'{pivot_group}.rotateY', rotation_y)
        else:
            cmds.setAttr(f'{pivot_group}.rotate',
                         rotation_xyz.x, rotation_xyz.y, rotation_xyz.z,
                         type='double3')
        cmds.xform(pivot, centerPivots=True)

        # Create cluster
        _, new_handle = cmds.cluster(vertices,
                                     name=f'{base_name}_{self.wrap_id}')
        new_handle = cmds.rename(new_handle,
                                 f'{base_name}_handle_{self.wrap_id}')
        cmds.parent(new_handle, pivot)

        if (cluster_id in self.pivot_locators
            or cluster_id in self.cluster_groups):
            raise ValueError(f"Duplicate cluster ID detected: {cluster_id}")

        self.pivot_locators[cluster_id] = pivot
        self.cluster_groups[cluster_id] = pivot_group

    def _getVertexFromPoint(self, point):
        """
        Helper function to get the vertex path for the given folding point.

        Args:
            point:  Folding point ID
        Returns:
            The path to the vertex.
        """
        try:
            return f'{self.plane_transform}.vtx[{self.plane.getVertex(point)}]'
        except KeyError:
            raise KeyError(
                f'Could not find fold point {point} in folding plane'
            )

    def _getVerticesFromPoints(self, points):
        """
        Helper function to get the vertex paths for the given folding points.

        Args:
            points:  List of folding point ID
        Returns:
            The paths to the vertices.
        """
        paths = []
        for point in points:
            paths.append(self._getVertexFromPoint(point))
        return paths

    def _getVerticesForRow(self, row_index):
        """
        Helper function to get a list of vertex paths for a row.
        """
        row_letters = ['F', 'G', 'H', 'I']
        vertices = []

        for letter in row_letters:
            point = f'{letter}{row_index}'
            vertices.append(self._getVertexFromPoint(point))

        return vertices
