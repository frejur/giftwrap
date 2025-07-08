import maya.cmds as cmds
from .pivots import calculateFoldingPivots
from ...utils.custom_types.vec import Vec

_DIAGONAL_FOLDS_MAP = {
    '3_F2_1': ('F1', True),
    '3_F2_2': ('F1', False),
    '3_F3_1': ('F3', True),
    '3_F3_2': ('F3', False),
    '3_I2_1': ('F1', True),
    '3_I2_2': ('F1', False),
    '3_I3_1': ('F3', True),
    '3_I3_2': ('F3', False),
    '3_F5_1': ('F5', True),
    '3_F5_2': ('F5', False),
    '3_F6_1': ('F6', True),
    '3_F6_2': ('F6', False),
    '3_I5_1': ('F5', True),
    '3_I5_2': ('F5', False),
    '3_I6_1': ('F6', True),
    '3_I6_2': ('F6', False),
}

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
        row_map = {'F1 until F2':    (1, 1),
                   'F2 until F3':    (2, 2),
                   'After I5 to I6': (6, 5),
                   'After I6 to I7': (7, 6)}
        row_vertices = {
            key: self._getVerticesForRow(a) + self._getVerticesInBetweenRows(b)
            for key, (a, b) in row_map.items()
        }

        if not self.pattern.hasOverlappingFolds():
            row_vertices['F8 to I8'] = self._getVerticesForRow(8)

        # 1st fold =============================================================
        # Upper
        self._addCluster(row_vertices['F1 until F2'] +
                         row_vertices['F2 until F3'], '1_F1_I1')

        # Lower
        vertices_1B = (row_vertices['After I5 to I6'] +
                       row_vertices['After I6 to I7'] +
                       (row_vertices['F8 to I8']
                        if not self.pattern.hasOverlappingFolds() else []))
        self._addCluster(vertices_1B, '1_F8_I8')

        # 2nd fold =============================================================
        self._addCluster(row_vertices['F1 until F2'], '2_F1_I1')

        vertices_2B = (row_vertices['After I6 to I7'] +
                       (row_vertices['F8 to I8']
                        if not self.pattern.hasOverlappingFolds() else []))
        self._addCluster(vertices_2B, '2_F8_I8')

        # 3rd fold =============================================================

        self._addCluster(row_vertices['F8 to I8'], '3_F8_I8')

        # self._addVerticesAndCreateClusterWithPivot(
        #     self._getVerticesFromPoints(pts_3UR_pad), '3UR', rotation_y=-45)
        #
        # vertices_3BR = [self._getVertexFromPoint('I5'),
        #                 self._getVertexFromPoint('I4ds')]
        # self._addVerticesAndCreateClusterWithPivot(vertices_3BR,
        #                                            '3BR',
        #                                            rotation_xyz=(
        #                                                Vec(180, 225, 0)))
        #
        # vertices_3UL = [self._getVertexFromPoint('F3'),
        #                 self._getVertexFromPoint('F4us')]
        # self._addVerticesAndCreateClusterWithPivot(vertices_3UL,
        #                                            '3UL',
        #                                            rotation_y=45)
        #
        # vertices_3BL = [self._getVertexFromPoint('F5'),
        #                 self._getVertexFromPoint('F4ds')]
        # self._addVerticesAndCreateClusterWithPivot(vertices_3BL,
        #                                            '3BL',
        #                                            rotation_xyz=(
        #                                                Vec(0, 45, 180)))
        #
        # # 4th fold =============================================================
        # vertices_4UR = [self._getVertexFromPoint('I2'),
        #                 self._getVertexFromPoint('I1s')]
        # self._addVerticesAndCreateClusterWithPivot(vertices_4UR,
        #                                            '4UR',
        #                                            rotation_y=135)
        #
        # vertices_4BR = [self._getVertexFromPoint('I6'),
        #                 self._getVertexFromPoint('I7s')]
        # self._addVerticesAndCreateClusterWithPivot(vertices_4BR,
        #                                            '4BR',
        #                                            rotation_y=45)
        #
        # vertices_4UL = [self._getVertexFromPoint('F2'),
        #                 self._getVertexFromPoint('F1s')]
        # self._addVerticesAndCreateClusterWithPivot(vertices_4UL,
        #                                            '4UL',
        #                                            rotation_y=225)
        #
        # vertices_4BL = [self._getVertexFromPoint('F6'),
        #                 self._getVertexFromPoint('F7s')]
        # self._addVerticesAndCreateClusterWithPivot(vertices_4BL,
        #                                            '4BL',
        #                                            rotation_xyz=(
        #                                                Vec(180, 225, 180)))
        #
        # # 5th fold =============================================================
        # vertices_5R = self._getVerticesFromPoints(['I7', 'I1', 'I1a', 'I7a'])
        # vertices_5R_when_overlap = \
        #     self._getVerticesFromPoints(['I7b', 'I1b', 'I1c']) \
        #     if self.pattern.hasOverlappingFolds() \
        #     else []
        # vertices_5R_when_no_overlap = \
        #     self._getVerticesFromPoints(['I8']) \
        #     if self.pattern.hasOverlappingFolds() \
        #     else []
        #
        # self._addCluster(vertices_5R, '5R')
        #
        # vertices_5L = self._getVerticesFromPoints(['F7', 'F1', 'F1a', 'F7a'])
        # vertices_5L_when_overlap = \
        #     self._getVerticesFromPoints(['F7b', 'F1b', 'F1c']) \
        #         if self.pattern.hasOverlappingFolds() \
        #         else []
        # vertices_5L_when_no_overlap = \
        #     self._getVerticesFromPoints(['F8']) \
        #         if self.pattern.hasOverlappingFolds() \
        #         else []
        #
        # self._addCluster(vertices_5L, '5L')
        #
        # # 6th fold =============================================================
        # vertices_6R = self._getVerticesFromPoints(['I4a', 'I4b'])
        # vertices_6R_when_overlap = self._getVerticesFromPoints(['HI4']) \
        #                            if self.pattern.hasOverlappingFolds() \
        #                            else []
        #
        # self._addCluster(vertices_6R, '6R')
        #
        # vertices_6L = self._getVerticesFromPoints(['F4a', 'F4b'])
        # vertices_6L_when_overlap = self._getVerticesFromPoints(['FG4']) \
        #     if self.pattern.hasOverlappingFolds() \
        #     else []
        #
        # self._addCluster(vertices_6L, '6L')

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

    def _addVerticesAndCreateClusterWithPivot(self,
                                              vertex_paths,
                                              cluster_id,
                                              rotation_y=None,
                                              rotation_xyz=None):
        """
        Helper for creating cluster-pivot groups.

        Args:
            vertex_paths: List of vertex paths to include in the cluster.
            cluster_id:     The cluster ID.
            rotation_y:     The rotation angle in degrees for Y.
            rotation_xyz:   The rotation angle in degrees for X,Y,Z.

        Modifies:
            `self.pivot_locators` and `self.groups`
            (See `self._addClusterWithPivot`)
        """
        if len(vertex_paths) == 0:
            raise RuntimeError(f'Cluster "{cluster_id}" cannot be created: '
                               'No vertex indices provided')

        self._validateRotParms(rotation_y, rotation_xyz)
        if rotation_y is not None:
            self._addClusterWithPivot(vertex_paths, cluster_id,
                                      rotation_y=rotation_y,
                                      skip_rotation_validation=True)
        else:
            self._addClusterWithPivot(vertex_paths, cluster_id,
                                      rotation_xyz=rotation_xyz,
                                      skip_rotation_validation=True)

    @staticmethod
    def _validateRotParms(rotation_y, rotation_xyz):
        if (rotation_y is not None and rotation_xyz is not None) or \
                (rotation_y is None and rotation_xyz is None):
            raise RuntimeError(
                'Must provide either rotation_y or rotation_xyz')

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
        cmds.xform(new_handle,
                   rotatePivot=list(self.pivot_xyz[cluster_id].position))

        if cluster_id in self.handles:
            raise ValueError(f"Duplicate cluster ID detected: {cluster_id}")

        self.handles[cluster_id] = new_handle

    def _addClusterWithPivot(self, vertices, cluster_id,
                             rotation_xyz=None, rotation_y=None,
                             skip_rotation_validation=False):
        """
        Helper function to create a group with a cluster, and a locator
        that serves as the cluster's local pivot point.

        Args:
            vertices:                 A list of vertex paths.
            cluster_id:               The cluster ID.
            rotation_y:               The rotation angle in degrees for Y.
            rotation_xyz:             The rotation angle in degrees for X,Y,Z.
            skip_rotation_validation: If True, skip validation of rotation
                                      angles.

        Modifies:
            Stores the pivot point locator in `self.pivot_locators`
            Stores the new group in `self.groups`
        """
        if not skip_rotation_validation:
            self._validateRotParms(rotation_y, rotation_xyz)

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

    def _getVertexFromIndex(self, index):
        """
        Helper function to get the vertex path for the given index.

        Args:
            index:  Vertex index
        Returns:
            The path to the vertex.
        """
        return f'{self.plane_transform}.vtx[{index}]'

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

        Args:
            row_index:  The row index (1-based indexing)
        Returns:
            A list of vertex paths.
        """
        vertices = []
        for idx in self.plane.getRowVertices(row_index):
            vertices.append(self._getVertexFromIndex(idx))

        return vertices

    def _getVerticesInBetweenRows(self, row_index):
        """
        Helper function to get a list of vertex paths for the gap between rows.

        Args:
            row_index: The row index (1-based indexing), e.g. row=1 returns the
                       vertices in the gap between row 1 and row 2.
        Returns:
            A list of vertex paths.
        """
        vertices = []
        for idx in self.plane.getVerticesInBetweenRows(row_index):
            vertices.append(self._getVertexFromIndex(idx))

        return vertices

    def _getVerticesForDiagonalFold(self, fold_id):
        """
        Helper function to get a list of vertex paths for the given diagonal
        fold.

        Args:
            fold_id: The row index (1-based indexing), e.g. row=1 returns the
                       vertices in the gap between row 1 and row 2.
        Returns:
            A list of vertex paths.
        """
        vertices = []
        for idx in self.plane.getVerticesForDiagonalFold(
                *_DIAGONAL_FOLDS_MAP[fold_id]):
            vertices.append(self._getVertexFromIndex(idx))

        return vertices
