import maya.cmds as cmds
from enum import Enum, auto

from .folding_pattern import *

class FoldingPlane:
    def __init__(self, pattern, wrap_id):
        """
        A polygon plane with topology that conforms to the given folding pattern
        and that folds / serves as a wrap deformer for the paper mesh.
        """
        self.wrap_id = wrap_id
        plane_name = f'folding_plane_{self.wrap_id}'

        self.pattern = pattern
        num_rows = 5 if self.pattern.hasOverlappingFolds() else 6
        self.plane = cmds.polyPlane(name=plane_name, subdivisionsX=3,
                                   subdivisionsY=num_rows,
                                   constructionHistory=0)[0]
        self.state = self.FoldingState.NO_FOLDS_DONE

        self.vertices = {} # Stores vertice-fold-point pairs

        # Align vertices with folding pattern
        vertex_mappings = [
            (0,  'F7'), (1,  'G7'), (2,  'H7'), (3,  'I7'),
            (4,  'F6'), (5,  'G6'), (6,  'H6'), (7,  'I6'),
            (8,  'F5'), (9,  'G5'), (10, 'H5'), (11, 'I5'),
            (12, 'F3'), (13, 'G3'), (14, 'H3'), (15, 'I3'),
            (16, 'F2'), (17, 'G2'), (18, 'H2'), (19, 'I2'),
            (20, 'F1'), (21, 'G1'), (22, 'H1'), (23, 'I1')
        ]

        if not self.pattern.hasOverlappingFolds():
            # Insert row
            vertex_mappings =(
                [(0, 'F8'), (1, 'G8'), (2, 'H8'), (3, 'I8')]
                + [(vtx + 4, pt) for vtx, pt in vertex_mappings]
            )

        for vertex, fold_point in vertex_mappings:
            self._alignVertex(vertex, fold_point)

        # Model folds (Note: Order is important)
        self._model_mid_folds(self.FoldingSide.RIGHT)
        self._model_mid_folds(self.FoldingSide.LEFT)
        self._model_top_folds(self.FoldingSide.RIGHT)
        self._model_top_folds(self.FoldingSide.LEFT)
        self._model_bottom_folds(self.FoldingSide.RIGHT)
        self._model_bottom_folds(self.FoldingSide.LEFT)

    # Getters ==================================================================

    def getTransformNode(self):
        return self.plane

    def getVertex(self, fold_point):
        return self.vertices[fold_point]

    # Enums ====================================================================

    class FoldingState(Enum):
        NO_FOLDS_DONE = auto()
        MID_RIGHT_FOLDS_DONE = auto()
        MID_LEFT_FOLDS_DONE = auto()
        TOP_RIGHT_FOLDS_DONE = auto()
        TOP_LEFT_FOLDS_DONE = auto()
        BOTTOM_RIGHT_FOLDS_DONE = auto()
        BOTTOM_LEFT_FOLDS_DONE = auto()

    class FoldingSide(Enum):
        LEFT  = auto()
        RIGHT = auto()

    # Model folds ==============================================================

    def _model_mid_folds(self, side):
        """
        Helper class to divide faces and merge vertices of the folding plane to
        create the topology for the Mid Folds.

        Args:
            side:   LEFT or RIGHT (FoldingSide enum)
        """
        # Confirm correct order of operations
        if side == self.FoldingSide.RIGHT:
            if self.state != self.FoldingState.NO_FOLDS_DONE:
                raise ValueError("Invalid state")
        elif side == self.FoldingSide.LEFT:
            if self.state != self.FoldingState.MID_RIGHT_FOLDS_DONE:
                raise ValueError("Invalid state")
        else:
            raise ValueError("Invalid side")

        # Adjust variables for the right / left side
        no_overlap = not self.pattern.hasOverlappingFolds()
        IS_R = (side == self.FoldingSide.RIGHT)
        col_X      =                  'H'   if IS_R else   'G'
        col_Y      =                  'I'   if IS_R else   'F'
        col_XY     =    f'{col_X}{col_Y}'   if IS_R else   f'{col_Y}{col_X}'
        div_face_0 =  (8, 11)[no_overlap]   if IS_R else   (6, 9)[no_overlap]
        div_face_1 = (15, 18)[no_overlap]   if IS_R else   (6, 9)[no_overlap]
        div_UV     =               (3, 1)   if IS_R else   (1, 3)
        X3         = (24, 31)[no_overlap]   if IS_R else   (27, 31)[no_overlap]
        X5         = (25, 30)[no_overlap]   if IS_R else   (28, 30)[no_overlap]
        Y4a        = (25, 29)[no_overlap]   if IS_R else   (28, 31)[no_overlap]
        Y4b        = (26, 28)[no_overlap]   if IS_R else   (29, 30)[no_overlap]
        XY4_0      = (24, 28)[no_overlap]   if IS_R else   (27, 31)[no_overlap]
        XY4_1      = (25, 29)[no_overlap]   if IS_R else   (28, 32)[no_overlap]

        if no_overlap:
            cmds.polySubdivideFacet(f'{self.plane}.f[{div_face_0}]',
                                    divisionsU=1, divisionsV=3,
                                    subdMethod=1, constructionHistory=0)
            self._mergeAndAlignVertices(X3, f'{col_X}3')
            self._mergeAndAlignVertices(X5, f'{col_X}5')
            self._alignVertex(Y4a, f'{col_Y}4a')
            self._alignVertex(Y4b, f'{col_Y}4b')
        else:
            cmds.polySubdivideFacet(f'{self.plane}.f[{div_face_0}]',
                                    divisionsU=2, divisionsV=1,
                                    subdMethod=1, constructionHistory=0)
            cmds.polySubdivideFacet(f'{self.plane}.f[{div_face_1}]',
                                    divisionsU=div_UV[0],
                                    divisionsV=div_UV[1],
                                    subdMethod=1, constructionHistory=0)
            self._mergeAndAlignVertices(X5, f'{col_X}5')
            self._mergeAndAlignVertices(X3, f'{col_X}3')
            self._alignVertex(XY4_0, f'{col_XY}4')
            self._mergeAndAlignVertices(XY4_1, f'{col_XY}4')
            self._alignVertex(Y4a, f'{col_Y}4a')
            self._alignVertex(Y4b, f'{col_Y}4b')

        self.state = (self.FoldingState.MID_RIGHT_FOLDS_DONE
                      if side == self.FoldingSide.RIGHT
                      else self.FoldingState.MID_LEFT_FOLDS_DONE)

    def _model_top_folds(self, side):
        """
        Helper class to divide faces and merge vertices of the folding plane to
        create the topology for the Top Folds.

        Args:
            side:   LEFT or RIGHT (FoldingSide enum)
        """
        # Confirm correct order of operations
        if side == self.FoldingSide.RIGHT:
            if self.state != self.FoldingState.MID_LEFT_FOLDS_DONE:
                raise ValueError("Invalid state")
        elif side == self.FoldingSide.LEFT:
            if self.state != self.FoldingState.TOP_RIGHT_FOLDS_DONE:
                raise ValueError("Invalid state")
        else:
            raise ValueError("Invalid side")

        # Adjust variables for the right / left side
        no_overlap = not self.pattern.hasOverlappingFolds()
        IS_R = (side == self.FoldingSide.RIGHT)
        col_X      =                  'H'   if IS_R else   'G'
        col_Y      =                  'I'   if IS_R else   'F'
        col_XY     =    f'{col_X}{col_Y}'   if IS_R else   f'{col_Y}{col_X}'
        div_face_0 = (14, 17)[no_overlap]   if IS_R else   (12, 15)[no_overlap]
        div_face_1 = (20, 23)[no_overlap]   if IS_R else   (25, 28)[no_overlap]
        div_UV     =               (1, 2)   if IS_R else   ((2, 1),
                                                            (1, 2))[no_overlap]
        X2         = ([32, 33],
                      33)[no_overlap]  if IS_R else   ([34, 36],
                                                       33)[no_overlap]
        Y1         = (34, 38)[no_overlap]   if IS_R else   (37, 41)[no_overlap]
        Y1a_0      = (32, 32)[no_overlap]   if IS_R else   (35, 33)[no_overlap]
        Y1a_1      = (33, 37)[no_overlap]   if IS_R else   (36, 40)[no_overlap]
        Y1b        = (31, 35)[no_overlap]   if IS_R else   (34, 38)[no_overlap]
        Y1c        = (30, 34)[no_overlap]   if IS_R else   (33, 37)[no_overlap]


        if no_overlap:
            cmds.polySubdivideFacet(f'{self.plane}.f[{div_face_0}]',
                                    divisionsU=div_UV[0], divisionsV=div_UV[1],
                                    subdMethod=1, constructionHistory=0)
            self._mergeAndAlignVertices(X2, f'{col_X}2')
            self._alignVertex(Y1a_0, f'{col_Y}1a')
        else:
            cmds.polySubdivideFacet(f'{self.plane}.f[{div_face_0}]',
                                    divisionsU=2, divisionsV=2,
                                    subdMethod=1, constructionHistory=0)
            self._mergeAndAlignVertices(X2, f'{col_X}2')
            cmds.polySubdivideFacet(f'{self.plane}.f[{div_face_1}]',
                                    divisionsU=div_UV[0], divisionsV=div_UV[1],
                                    subdMethod=1, constructionHistory=0)
            self._mergeAndAlignVertices(Y1, f'{col_Y}1')
            self._alignVertex(Y1a_0, f'{col_Y}1a')
            self._mergeAndAlignVertices(Y1a_1, f'{col_Y}1a')
            self._alignVertex(Y1c, f'{col_Y}1c')
            self._alignVertex(Y1b, f'{col_Y}1b')


        self.state = (self.FoldingState.TOP_RIGHT_FOLDS_DONE
                      if side == self.FoldingSide.RIGHT
                      else self.FoldingState.TOP_LEFT_FOLDS_DONE)

    def _model_bottom_folds(self, side):
        """
        Helper class to divide faces and merge vertices of the folding plane to
        create the topology for the Bottom Folds.

        Args:
            side:   LEFT or RIGHT (FoldingSide enum)
        """
        # Confirm correct order of operations
        if side == self.FoldingSide.RIGHT:
            if self.state != self.FoldingState.TOP_LEFT_FOLDS_DONE:
                raise ValueError("Invalid state")
        elif side == self.FoldingSide.LEFT:
            if self.state != self.FoldingState.BOTTOM_RIGHT_FOLDS_DONE:
                raise ValueError("Invalid state")
        else:
            raise ValueError("Invalid side")

        # Adjust variables for the right / left side
        no_overlap = not self.pattern.hasOverlappingFolds()
        IS_R = (side == self.FoldingSide.RIGHT)
        col_X      =                  'H'   if IS_R else   'G'
        col_Y      =                  'I'   if IS_R else   'F'
        col_XY     =    f'{col_X}{col_Y}'   if IS_R else   f'{col_Y}{col_X}'
        div_face_0 =   (2, 5)[no_overlap]   if IS_R else   (0, 3)[no_overlap]
        div_face_1 =                   27   if IS_R else   (0, 28)[no_overlap]
        div_UV_0   = ((2, 1),
                      (1, 2))[no_overlap]   if IS_R else   ((2, 1),
                                                            (1, 2))[no_overlap]
        div_UV_1   =               (2, 1)   if IS_R else   ((1, 2),
                                                            (2, 1))[no_overlap]
        X6         = (36, 35)[no_overlap]   if IS_R else   (38, 35)[no_overlap]
        Y7a_0      = (36, 34)[no_overlap]   if IS_R else   (38, 35)[no_overlap]
        Y7a_1      =                   37   if IS_R else   (39, 37)[no_overlap]
        Y7b        =                   37   if IS_R else   (39, 37)[no_overlap]

        if no_overlap:
            cmds.polySubdivideFacet(f'{self.plane}.f[{div_face_0}]',
                                    divisionsU=div_UV_0[0],
                                    divisionsV=div_UV_0[1],
                                    subdMethod=1, constructionHistory=0)
            self._mergeAndAlignVertices(X6, f'{col_X}6')
            self._alignVertex(Y7a_0, f'{col_Y}7a')
        else:
            cmds.polySubdivideFacet(f'{self.plane}.f[{div_face_0}]',
                                    divisionsU=div_UV_0[0],
                                    divisionsV=div_UV_0[1],
                                    subdMethod=1, constructionHistory=0)
            cmds.polySubdivideFacet(f'{self.plane}.f[{div_face_1}]',
                                    divisionsU=div_UV_1[0],
                                    divisionsV=div_UV_1[1],
                                    subdMethod=1, constructionHistory=0)
            self._mergeAndAlignVertices(X6, f'{col_X}6')
            self._alignVertex(Y7a_0, f'{col_Y}7a')
            self._mergeAndAlignVertices(Y7a_1, f'{col_Y}7a')
            self._alignVertex(Y7b, f'{col_Y}7b')

        self.state = (self.FoldingState.BOTTOM_RIGHT_FOLDS_DONE
                      if side == self.FoldingSide.RIGHT
                      else self.FoldingState.BOTTOM_LEFT_FOLDS_DONE)

    # Other helpers ============================================================

    def _vtx_path(self, vertex_id):
        """
        Helper function to transform a vertice id into a path.
        """
        return self.plane + '.vtx[%d]' % vertex_id

    def _vtx_path_list(self, vertex_id_list):
        """
        Helper function to transform a list of vertices into a list of paths.
        """
        return [self._vtx_path(i) for i in vertex_id_list]

    def _setVertexPosition(self, vertex_index, position):
        """
        Helper function to set the position of a vertex in a mesh
        Args:
            vertex_index: The index of the vertex to move
            position:     The new position of the vertex (Tuple: x, y, z)
        """
        vertex_path = self._vtx_path(vertex_index)
        cmds.xform(vertex_path, translation=list(position), worldSpace=True)

    def _alignVertex(self, vertex_index, fold_point):
        """
        Helper function to align a vertex in the mesh with the given
        pattern fold point. Moves the given vertice into the fold point's
        position and updates the internal list of vertice ID's.
        Args:
            vertex_index: The index of the vertex to move
            fold_point:   The ID of the fold point
        Modifies:
            self.vertices
        """
        position = self.pattern.point(fold_point)
        self._setVertexPosition(vertex_index, position)
        self.vertices[fold_point] = vertex_index

    def _mergeAndAlignVertices(self, vertex_list, fold_point):
        """
        Merges the given vertices at the fold point's position.
        Args:
            vertex_list: The indexes of the vertices to align and merge.
            fold_point:  The ID of the fold point whose position will be used
                         as the merging point.
        """
        if isinstance(vertex_list, int):
            paths = [self._vtx_path(vertex_list)]
        else:
            paths = self._vtx_path_list(vertex_list)

        merge_vertex = self._vtx_path(self.vertices[fold_point])
        paths.append(merge_vertex)
        result = cmds.polyMergeVertex(paths, mergeToComponents=merge_vertex,
                                      constructionHistory=0)
