import maya.cmds as cmds
import maya.api.OpenMaya as om
from collections import namedtuple

from .bbox import BoundingBox

class ObjectSpaceBoundingBox(BoundingBox):
    def __init__(self, obj=None):
        """
        Object space bounding box.

        If no input object is given, attempts to use the current selection.
        """
        BoundingBox.__init__(self, obj)

        world_matrix = om.MMatrix(
            cmds.xform(obj, query=True, worldSpace=True, matrix=True)
        )

        normalized_rot_matrix = self._extract_rotation_matrix(world_matrix)

        all_verts_world = self._extract_world_vertices(obj)
        translation_vector = self._get_translation_vector(obj)
        self._set_object_corners(all_verts_world,
                                 translation_vector,
                                 normalized_rot_matrix)

        # Transform corners back to world space
        self.corners_world = []
        for obj_corner in self.corners_object:
            # Apply rotation
            world_corner = obj_corner * normalized_rot_matrix

            # Apply translation
            world_corner = om.MPoint(
                world_corner.x + translation_vector.x,
                world_corner.y + translation_vector.y,
                world_corner.z + translation_vector.z
            )

            self.corners_world.append(world_corner)

    def _extract_rotation_matrix(self, world_matrix):
        # Extract 3-by-3 portion with rotational values (exclude scale)
        rot_matrix = om.MMatrix([
            world_matrix[0], world_matrix[1], world_matrix[2], 0,
            world_matrix[4], world_matrix[5], world_matrix[6], 0,
            world_matrix[8], world_matrix[9], world_matrix[10], 0,
            0, 0, 0, 1
        ])
        # Normalize rows / axes to remove scale influence
        axes = [om.MVector(rot_matrix[0], rot_matrix[1], rot_matrix[2]),  # x
                om.MVector(rot_matrix[4], rot_matrix[5], rot_matrix[6]),  # y
                om.MVector(rot_matrix[8], rot_matrix[9], rot_matrix[10])]  # z
        for a in axes:
            a.normalize()
        # Use the normalized axes to rebuild rotation matrix
        normalized_rot_matrix = om.MMatrix([
            axes[0].x, axes[0].y, axes[0].z, 0,
            axes[1].x, axes[1].y, axes[1].z, 0,
            axes[2].x, axes[2].y, axes[2].z, 0,
            0, 0, 0, 1
        ])
        return normalized_rot_matrix
