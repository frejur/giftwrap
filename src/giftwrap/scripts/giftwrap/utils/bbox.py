import maya.cmds as cmds
import maya.api.OpenMaya as om
from enum import IntEnum

class BboxFace(IntEnum):
    TOP, BOTTOM, LEFT, RIGHT, FRONT, BACK = range(6)

class ObjectSpaceBoundingBox:
    """
    Object space bounding box.

    Uses the orientation of the root node.
    If no input object is given, attempts to use the current selection.
    """
    def __init__(self, obj=None):
        if obj is None:
            obj = cmds.ls(selection=True)

        if not obj:
            raise ValueError('No object specified / selected')

        if len(obj) > 1:
            raise ValueError('More than one object specified / selected')

        if isinstance(obj, list):
            obj = obj[0]

        if not cmds.objExists(obj):
            raise ValueError(f'Object {obj} does not exist')

        world_matrix = om.MMatrix(
            cmds.xform(obj, query=True, worldSpace=True, matrix=True)
        )

        # Extract rotational values (exclude scale)
        rotation_matrix = om.MMatrix([
            world_matrix[0], world_matrix[1], world_matrix[2], 0,
            world_matrix[4], world_matrix[5], world_matrix[6], 0,
            world_matrix[8], world_matrix[9], world_matrix[10], 0,
            0, 0, 0, 1
        ])
        rotation_inverse = rotation_matrix.inverse()

        # Get all vertices in world space
        all_verts_world = []

        # Collect vertices from the object and all sub nodes
        all_objects = [obj]
        sub_nodes = cmds.listRelatives(
            obj, allDescendents=True, fullPath=True, type='transform'
        ) or []
        all_objects.extend(sub_nodes)

        for o in all_objects:
            shapes = cmds.listRelatives(o, shapes=True, fullPath=True) or []
            if not shapes:
                continue

            for shape in shapes:
                shape_type = cmds.nodeType(shape)

                if shape_type == 'mesh':
                    verts = cmds.xform(
                        f'{o}.vtx[*]',
                        query=True, translation=True, worldSpace=True
                    )
                    for i in range(0, len(verts), 3):
                        all_verts_world.append(
                            om.MPoint(verts[i], verts[i + 1], verts[i + 2])
                        )

                elif shape_type in ['nurbsSurface', 'nurbsCurve']:
                    try:
                        cvs = cmds.xform(
                            f'{o}.cv[*]',
                            query=True, translation=True, worldSpace=True
                        )
                        for i in range(0, len(cvs), 3):
                            all_verts_world.append(
                                om.MPoint(cvs[i], cvs[i + 1], cvs[i + 2])
                            )
                    except:
                        # Fallback to bounding box corners
                        bb = cmds.exactWorldBoundingBox(o)
                        all_verts_world.extend([
                            om.MPoint(bb[0], bb[1], bb[2]),  # min corner
                            om.MPoint(bb[3], bb[1], bb[2]),  # +x, -y, -z
                            om.MPoint(bb[0], bb[4], bb[2]),  # -x, +y, -z
                            om.MPoint(bb[0], bb[1], bb[5]),  # -x, -y, +z
                            om.MPoint(bb[3], bb[4], bb[2]),  # +x, +y, -z
                            om.MPoint(bb[3], bb[1], bb[5]),  # +x, -y, +z
                            om.MPoint(bb[0], bb[4], bb[5]),  # -x, +y, +z
                            om.MPoint(bb[3], bb[4], bb[5])   # max corner
                        ])

        # World translation
        translate = cmds.xform(obj, query=True, translation=True, worldSpace=True)
        translate_vector = om.MVector(translate[0], translate[1], translate[2])

        # Transform all world space points to object space
        all_verts_obj_space = []

        for world_point in all_verts_world:
            # Convert to world-relative (subtract translation)
            rel_point = om.MPoint(
                world_point.x - translate_vector.x,
                world_point.y - translate_vector.y,
                world_point.z - translate_vector.z
            )

            # Transform by inverted rot. matrix to get into object space
            obj_space_point = rel_point * rotation_inverse
            all_verts_obj_space.append(obj_space_point)

        #  Find min and max in object space
        min_x = min(v.x for v in all_verts_obj_space)
        min_y = min(v.y for v in all_verts_obj_space)
        min_z = min(v.z for v in all_verts_obj_space)
        max_x = max(v.x for v in all_verts_obj_space)
        max_y = max(v.y for v in all_verts_obj_space)
        max_z = max(v.z for v in all_verts_obj_space)

        corners_obj = [
            om.MPoint(min_x, min_y, min_z),
            om.MPoint(max_x, min_y, min_z),
            om.MPoint(min_x, max_y, min_z),
            om.MPoint(max_x, max_y, min_z),
            om.MPoint(min_x, min_y, max_z),
            om.MPoint(max_x, min_y, max_z),
            om.MPoint(min_x, max_y, max_z),
            om.MPoint(max_x, max_y, max_z)
        ]

        # Transform corners back to world space
        self.corners_world = []
        for obj_corner in corners_obj:
            # Apply rotation
            world_corner = obj_corner * rotation_matrix

            # Apply translation
            world_corner = om.MPoint(
                world_corner.x + translate_vector.x,
                world_corner.y + translate_vector.y,
                world_corner.z + translate_vector.z
            )

            self.corners_world.append(world_corner)

    def getCorners(self):
        """
        Returns:
            A list of corner position tuples, [(x, y, z), (x, y, z), ...],
            in the following order:
                0: Back-Bottom-Left
                1: Back-Bottom-Right
                2: Back-Top-Left
                3: Back-Top-Right
                4: Front-Bottom-Left
                5: Front-Bottom-Right
                6: Front-Top-Left
                7: Front-Top-Right
        """
        return [(c.x, c.y, c.z) for c in self.corners_world]

    def getCorner(self, x_sign, y_sign, z_sign):
        """
        Returns the position of the given corner.

        Args:
            x_sign: 1 for max, -1 for min
            y_sign: 1 for max, -1 for min
            z_sign: 1 for max, -1 for min
        Returns:
            Tuple (x, y, z)
        """
        if ((x_sign != -1 and x_sign != 1) or
            (y_sign != -1 and y_sign != 1) or
            (z_sign != -1 and z_sign != 1)):
            raise ValueError('Invalid sign')

        index = (
            (1 if x_sign == 1 else 0) +
            (2 if y_sign == 1 else 0) +
            (4 if z_sign == 1 else 0)
        )
        return (self.corners_world[index].x,
                self.corners_world[index].y,
                self.corners_world[index].z)

    @staticmethod
    def avgPos(a, b):
        """
        Helper function to calculate the average position of two points

        Args:
            a: Mpoint
            b: Mpoint

        Returns:
            Tuple (x, y, z)
        """
        return (a.x + b.x) * 0.5, (a.y + b.y) * 0.5, (a.z + b.z) * 0.5

    def getMidPoint(self, face):
        """
        Returns the position of the middle point of the given face.

        Args:
            face: Front, Bottom, Left, etc.
        Returns:
            Tuple (x, y, z)
        """
        if face == BboxFace.TOP:
            p = self.avgPos(self.corners_world[2], self.corners_world[7])
        elif face == BboxFace.BOTTOM:
            p = self.avgPos(self.corners_world[0], self.corners_world[5])
        elif face == BboxFace.LEFT:
            p = self.avgPos(self.corners_world[0], self.corners_world[6])
        elif face == BboxFace.RIGHT:
            p = self.avgPos(self.corners_world[1], self.corners_world[7])
        elif face == BboxFace.FRONT:
            p = self.avgPos(self.corners_world[4], self.corners_world[7])
        elif face == BboxFace.BACK:
            p = self.avgPos(self.corners_world[0], self.corners_world[3])
        else:
            raise ValueError('Invalid face')
        return p


def drawObjectSpaceBoundingBox(bbox, color=(0, 1, 1)):
    """
    Draw bounding box as curves.

    Args:
        bbox:  ObjectOrientedBoundingBox instance
        color: Color of bounding box curves (RGB tuple)

    Returns:
        The group node containing all curves
    """
    corners = bbox.getCorners()

    bbox_group = cmds.group(empty=True, name='bbox_curves_grp')

    edges = [
        (0, 1), (1, 5), (5, 4), (4, 0), # Bottom
        (2, 3), (3, 7), (7, 6), (6, 2), # Top
        (0, 2), (1, 3), (5, 7), (4, 6)  # Connecting
    ]

    curves = []
    for i, (start_idx, end_idx) in enumerate(edges):
        start_point = corners[start_idx]
        end_point = corners[end_idx]

        curve = cmds.curve(
            p=[start_point, end_point],
            degree=1,
            name=f'bbox_edge_{i}'
        )

        shape = cmds.listRelatives(curve, shapes=True)[0]
        cmds.setAttr(f'{shape}.overrideEnabled', 1)
        cmds.setAttr(f'{shape}.overrideRGBColors', 1)
        cmds.setAttr(f'{shape}.overrideColorRGB', color[0], color[1], color[2])

        curves.append(curve)

    cmds.parent(curves, bbox_group)

    return bbox_group
