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

        if not self.pattern.hasOverlappingFolds():
            vertices_row_8 = self._getVerticesForRow(8)

        # 1st fold =============================================================
        # Upper
        vertices_1U = vertices_row_1 + vertices_row_2
        self._addVerticesAndCreateCluster(vertices_1U,
                                          ['F1a', 'I1a'],
                                          ['F1b', 'I1b', 'F1c', 'I1c'],
                                          '1U')

        # Lower
        vertices_1B = vertices_row_6 + vertices_row_7
        if not self.pattern.hasOverlappingFolds():
            vertices_1B += vertices_row_8
        self._addVerticesAndCreateCluster(vertices_1B,
                                          ['F7a', 'I7a'],
                                          ['F7b', 'I7b'],
                                          '1B')

        # 2nd fold =============================================================
        vertices_2U = vertices_row_1
        self._addVerticesAndCreateCluster(vertices_2U,
                                          ['F1a', 'I1a'],
                                          ['F1b', 'I1b', 'F1c', 'I1c'],
                                          '2U')

        vertices_2B = vertices_row_7
        if not self.pattern.hasOverlappingFolds():
            vertices_2B += vertices_row_8
        self._addVerticesAndCreateCluster(vertices_2B,
                                          ['F7a', 'I7a'],
                                          ['F7b', 'I7b'],
                                          '2B')

        # 3rd fold =============================================================
        vertices_3UR = [self._getVertexFromPoint('I3')]
        self._addVerticesAndCreateClusterWithPivot(vertices_3UR,
                                                   ['I4a', 'I4b'],
                                                   '3UR',
                                                   rotation_y=-45)

        vertices_3BR = [self._getVertexFromPoint('I5')]
        self._addVerticesAndCreateClusterWithPivot(vertices_3BR,
                                                   ['I4a', 'I4b'],
                                                   '3BR',
                                                   rotation_xyz=(
                                                       Vec(180, 225, 0)))

        vertices_3UL = [self._getVertexFromPoint('F3')]
        self._addVerticesAndCreateClusterWithPivot(vertices_3UL,
                                                   ['F4a', 'F4b'],
                                                   '3UL',
                                                   rotation_y=45)

        vertices_3BL = [self._getVertexFromPoint('F5')]
        self._addVerticesAndCreateClusterWithPivot(vertices_3BL,
                                                   ['F4a', 'F4b'],
                                                   '3BL',
                                                   rotation_xyz=(
                                                       Vec(0, 45, 180)))

        # 4th fold =============================================================
        vertices_4UR = [self._getVertexFromPoint('I2')]
        self._addVerticesAndCreateClusterWithPivot(vertices_4UR,
                                                   ['I1b', 'I7'],
                                                   '4UR',
                                                   rotation_y=135)

        vertices_4BR = [self._getVertexFromPoint('I6')]
        self._addVerticesAndCreateClusterWithPivot(vertices_4BR,
                                                   ['I7a', 'I7b', 'I1', 'I7'],
                                                   '4BR',
                                                   rotation_y=45)

        vertices_4UL = [self._getVertexFromPoint('F2')]
        self._addVerticesAndCreateClusterWithPivot(vertices_4UL,
                                                   ['F1b', 'F7'],
                                                   '4UL',
                                                   rotation_y=225)

        vertices_4BL = [self._getVertexFromPoint('F6')]
        self._addVerticesAndCreateClusterWithPivot(vertices_4BL,
                                                   ['F7a', 'F7b', 'F1', 'F7'],
                                                   '4BL',
                                                   rotation_xyz=(
                                                       Vec(180, 225, 180)))

        # 5th fold =============================================================
        vertices_5R = ([]
                       if self.pattern.hasOverlappingFolds()
                       else [self._getVertexFromPoint('I8')])

        self._addVerticesAndCreateCluster(vertices_5R,
                                          ['I7', 'I1', 'I1a', 'I7a'],
                                          ['I7b', 'I1b', 'I1c'],
                                          '5R')

        vertices_5L = ([]
                       if self.pattern.hasOverlappingFolds()
                       else [self._getVertexFromPoint('F8')])

        self._addVerticesAndCreateCluster(vertices_5L,
                                          ['F7', 'F1', 'F1a', 'F7a'],
                                          ['F7b', 'F1b', 'F1c'],
                                          '5L')

        # 6th fold =============================================================

        self._addVerticesAndCreateCluster([], ['I4a', 'I4b'], ['HI4'], '6R')
        self._addVerticesAndCreateCluster([], ['F4a', 'F4b'], ['FG4'], '6L')

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
                                     new_vertices,
                                     new_vertices_when_overlap,
                                     cluster_id):
        """
        Helper for creating clusters.

        Args:
            vertices_base:             List of vertices to use as a base.
            new_vertices:              List of new vertices to add.
            new_vertices_when_overlap: List of new vertices to add when folds
                                       overlap.
            cluster_id:                The cluster ID.

        Modifies:
            `self.handles` (See `self._addCluster')
        """
        vertices = deepcopy(vertices_base) # TODO: Check if this is necessary

        for point in new_vertices:
            vertices.append(self._getVertexFromPoint(point))

        if self.pattern.hasOverlappingFolds():
            for point in new_vertices_when_overlap:
                vertices.append(self._getVertexFromPoint(point))

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

        if self.pattern.hasOverlappingFolds():
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
