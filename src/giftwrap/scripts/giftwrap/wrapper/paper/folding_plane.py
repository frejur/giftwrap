import maya.cmds as cmds
from enum import Enum, auto
import os

from .folding_pattern import *
from .map.map_box import _BOX_MAPPINGS
from .map.map_box_overlap import _BOX_OVERLAP_MAPPINGS

class TemplateType(Enum):
    Box = auto()
    BoxWithOverlappingFolds = auto()

_OBJ_DIR = os.path.join(os.path.dirname(__file__), 'obj')
_TEMPLATE_GRP = '_giftwrap_templates_grp'
_OBJ_TEMPLATES = {
    TemplateType.Box: {
        'Name'    : '_template_box_geo',
        'Mappings': _BOX_MAPPINGS,
        'Filepath': os.path.join(_OBJ_DIR, 'template_box.obj')
    },
    TemplateType.BoxWithOverlappingFolds: {
        'Name'    : '_template_box_overlap_geo',
        "Mappings": _BOX_OVERLAP_MAPPINGS,
        'Filepath': os.path.join(_OBJ_DIR, 'template_box_overlap.obj')
    },
}

class FoldingPlane:
    def __init__(self, pattern, wrap_id):
        """
        A polygon plane with topology that conforms to the given folding pattern
        and that folds / serves as a wrap deformer for the paper mesh.
        """
        self.wrap_id = wrap_id
        plane_name = f'folding_plane_{self.wrap_id}_geo'

        template_group = (cmds.group(name=_TEMPLATE_GRP, empty=True)
                          if not cmds.objExists(_TEMPLATE_GRP)
                          else _TEMPLATE_GRP)

        template = (_OBJ_TEMPLATES[TemplateType.Box]
                    if not pattern.hasOverlappingFolds()
                    else _OBJ_TEMPLATES[TemplateType.BoxWithOverlappingFolds])

        if not cmds.objExists(f':{template_group}:{template["Name"]}'):
            source_geo = self._importObj(template['Filepath'])
            source_geo = cmds.rename(source_geo,
                                     f':{template_group}:{template["Name"]}')
        else:
            source_geo = template['Name']

        self.plane = cmds.duplicate(source_geo, name=plane_name)[0]

        self.pattern = pattern
        self.vertices = {}

        for fold_point, vtx in template['Mappings'].items():
            self._alignVertex(vtx, fold_point)

        print(self.vertices)

    # Getters ==================================================================

    def getTransformNode(self):
        return self.plane

    def getVertex(self, fold_point):
        return self.vertices[fold_point]

    def _vtxPath(self, vertex_id):
        """
        Helper function to transform a vertice id into a path.
        """
        return self.plane + '.vtx[%d]' % vertex_id

    def _vtxPathList(self, vertex_id_list):
        """
        Helper function to transform a list of vertices into a list of paths.
        """
        return [self._vtxPath(i) for i in vertex_id_list]

    def _setVertexPosition(self, vertex_index, position):
        """
        Helper function to set the position of a vertex in a mesh
        Args:
            vertex_index: The index of the vertex to move
            position:     The new position of the vertex (Tuple: x, y, z)
        """
        vertex_path = self._vtxPath(vertex_index)
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

    @staticmethod
    def _importObj(filepath):
        """
        Helper function to import single .obj mesh and return its name
        Args:
            filepath: The path to the .obj file
        Returns:
            The name of the imported mesh
        """
        new_nodes = cmds.file(filepath, i=True, type='OBJ', returnNewNodes=True)

        if len(new_nodes) != 2:
            raise RuntimeError('Expected two nodes on import: 1 transform node'
                               f'and 1 shape node. Got {len(new_nodes)} nodes.')

        types = [cmds.nodeType(node) for node in new_nodes]
        if types[0] != 'transform':
            raise RuntimeError('Expected a transform node after importing but '
                              f'got {types[0]}')
        if types[1] != 'mesh':
            raise RuntimeError('Expected a mesh shape node after importing but '
                               f'got {types[1]}')

        return new_nodes[0]
