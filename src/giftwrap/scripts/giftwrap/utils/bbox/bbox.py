import copy
import math
import maya.cmds as cmds
import maya.api.OpenMaya as om
from enum import IntEnum

class BboxFace(IntEnum):
    TOP, BOTTOM, LEFT, RIGHT, FRONT, BACK = range(6)

class BboxSpace(IntEnum):
    WORLD, OBJECT = range(2)

class BoundingBox:
    def __init__(self, obj=None):
        """
        Creates a world-space bounding box with a bunch of useful helper
        methods.

        If no input object is given, attempts to use the current selection.
        """
        self.normalized = False
        obj = self._validate_selection(obj)

        if isinstance(self, BoundingBox):
            self._create_bbox(obj)

    def _create_bbox(self, obj):
        """
        Base class specific implementation.
        TODO: Create abstract base class
        """
        world_verts = self._extract_world_vertices(obj)
        translation_vector = self._get_translation_vector(obj)
        self._set_object_corners(world_verts,
                                 translation_vector)

        # Transform corners back to world space
        self.corners_world = []
        for obj_corner in self.corners_object:
            world_corner = om.MPoint(
                obj_corner.x + translation_vector.x,
                obj_corner.y + translation_vector.y,
                obj_corner.z + translation_vector.z
            )

            self.corners_world.append(world_corner)

    @staticmethod
    def _validate_selection(obj):
        """
        Raises a ValueError if the input object is invalid or if more than
        one object has been provided.

        Returns:
            The object (If valid).
        """
        objects = cmds.ls(obj) if obj else cmds.ls(selection=True)

        if not objects:
            raise ValueError(
                'No objects selected' if obj is None
                else f'No objects selected: {objects}')
        if len(objects) > 1:
            raise ValueError(
                'Multiple ' +
                'objects selected' if obj is None
                else 'objects matched.'
                + ' Please specify a single object.')
        return obj

    @staticmethod
    def _extract_world_vertices(obj):
        """
        Gets all vertices (and points) of the given object in world space.

        Args:
            The object to extract vertices from.
        Returns:
            A list of vertices.
        """
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
                            om.MPoint(bb[3], bb[4], bb[5])  # max corner
                        ])
        return all_verts_world

    def _set_object_corners(
            self,
            all_verts_world,
            translation_vector,
            rotation_matrix=None
    ):
        """
       Transforms world space vertices to object space and calculates the
       axis-aligned bounding box corners.

       Args:
           all_verts_world:  List of MPoint vertices in world space
           translation_vector: The object's translation from origin (MVector)
           rotation_matrix:  MMatrix representing the object's rotation.
                             If set to None, only translation will be applied.

       Modifies:
           self.corners_object: Sets this attribute to a list of eight MPoints
                                with the corners of the bounding box
       """
        rotation_inverse =(
            rotation_matrix.inverse() if rotation_matrix is not None else None)

        # Transform all world space points to object space
        all_verts_obj_space = []
        for world_point in all_verts_world:
            # Convert to world-relative (subtract translation)
            rel_point = om.MPoint(
                world_point.x - translation_vector.x,
                world_point.y - translation_vector.y,
                world_point.z - translation_vector.z
            )

            if rotation_inverse is not None:
                # Transform by inverted rot. matrix to get into object space
                rel_point *= rotation_inverse

            all_verts_obj_space.append(rel_point)

        #  Find min and max in object space
        min_x = min(v.x for v in all_verts_obj_space)
        min_y = min(v.y for v in all_verts_obj_space)
        min_z = min(v.z for v in all_verts_obj_space)
        max_x = max(v.x for v in all_verts_obj_space)
        max_y = max(v.y for v in all_verts_obj_space)
        max_z = max(v.z for v in all_verts_obj_space)

        self.corners_object = [
            om.MPoint(min_x, min_y, min_z),
            om.MPoint(max_x, min_y, min_z),
            om.MPoint(min_x, max_y, min_z),
            om.MPoint(max_x, max_y, min_z),
            om.MPoint(min_x, min_y, max_z),
            om.MPoint(max_x, min_y, max_z),
            om.MPoint(min_x, max_y, max_z),
            om.MPoint(max_x, max_y, max_z)
        ]

    def _get_translation_vector(self, obj):
        """
            Gets the positional offset of the object in world space.
            Args:
                obj: Object

            Returns:
                MVector
        """
        translate = cmds.xform(obj, query=True, translation=True,
                               worldSpace=True)
        translation_vector = om.MVector(translate[0], translate[1], translate[2])
        return translation_vector

    def getCorners(self, space=BboxSpace.WORLD):
        """
        Gets each the position of each corner of the bounding box.

        Args:
            space: Cooordinate space (BboxSpace.WORLD or BboxSpace.OBJECT)

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
        if space == BboxSpace.WORLD:
            return [(c.x, c.y, c.z) for c in self.corners_world]
        else:
            return [(c.x, c.y, c.z) for c in self.corners_object]

    def getCorner(self, x_sign, y_sign, z_sign, space=BboxSpace.WORLD):
        """
        Returns the position of the given corner.

        Args:
            x_sign: 1 for max, -1 for min
            y_sign: 1 for max, -1 for min
            z_sign: 1 for max, -1 for min
            space: Cooordinate space (BboxSpace.WORLD or BboxSpace.OBJECT)

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

        if space == BboxSpace.WORLD:
            return (self.corners_world[index].x,
                    self.corners_world[index].y,
                    self.corners_world[index].z)
        else:
            return (self.corners_object[index].x,
                    self.corners_object[index].y,
                    self.corners_object[index].z)

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

    def getMidPoint(self, face, space=BboxSpace.WORLD):
        """
        Returns the position of the middle point of the given face.

        Args:
            face: Front, Bottom, Left, etc.
            space: Coordinate space (BboxSpace.WORLD or BboxSpace.OBJECT)
        Returns:
            Tuple (x, y, z)
        """
        if face == BboxFace.TOP:
            idx_pair = (2, 7)
        elif face == BboxFace.BOTTOM:
            idx_pair = (0, 5)
        elif face == BboxFace.LEFT:
            idx_pair = (0, 6)
        elif face == BboxFace.RIGHT:
            idx_pair = (1, 7)
        elif face == BboxFace.FRONT:
            idx_pair = (4, 7)
        elif face == BboxFace.BACK:
            idx_pair = (0, 3)
        else:
            raise ValueError('Invalid face')

        if space==BboxSpace.WORLD:
            return self.avgPos(self.corners_world[idx_pair[0]],
                               self.corners_world[idx_pair[1]])
        else:
            return self.avgPos(self.corners_object[idx_pair[0]],
                               self.corners_object[idx_pair[1]])

    def getCentroid(self, space=BboxSpace.WORLD):
        """
        Returns the position of the bounding box centroid.

        Args:
            space: Coordinate space (BboxSpace.WORLD or BboxSpace.OBJECT)

        Returns:
            Tuple (x, y, z)
        """
        if space==BboxSpace.WORLD:
            return self.avgPos(self.corners_world[0],
                               self.corners_world[7])
        else:
            return self.avgPos(self.corners_object[0],
                               self.corners_object[7])

    def getMinMax(self, space=BboxSpace.WORLD):
        """
        Gets the minimum and maximum positional values of the bounding box.

        Args:
            space: Coordinate space (BboxSpace.WORLD or BboxSpace.OBJECT)

        Returns:
           Tuple (x_min, y_min, z_min, x_max, y_max, z_max)
        """
        if space==BboxSpace.WORLD:
            return (self.corners_world[0].x, self.corners_world[0].y,
                    self.corners_world[0].z,
                    self.corners_world[7].x, self.corners_world[7].y,
                    self.corners_world[7].z)
        else:
            return (self.corners_object[0].x, self.corners_object[0].y,
                    self.corners_object[0].z,
                    self.corners_object[7].x, self.corners_object[7].y,
                    self.corners_object[7].z)

    def getDimensions(self):
        """
        Gets the dimensions of the bounding box.

        Returns:
            Tuple (width, height, depth)
        """
        minmax = self.getMinMax(space=BboxSpace.OBJECT)
        return (minmax[3] - minmax[0],
                minmax[4] - minmax[1],
                minmax[5] - minmax[2])

    def __deepcopy__(self, memo):
        """
        Returns a deep copy of this instance.

        Notes:
            The following Open Maya objects aren't picklable and need special
            handling when being copied:
                - MMatrix
                - MVector
                - MPoint (List of)
        """
        new_bb = self.__class__
        result = new_bb.__new__(new_bb)
        memo[id(self)] = result

        for k, v in self.__dict__.items():
            if v is None:
                setattr(result, k, None)

            elif isinstance(v, om.MVector):
                setattr(result, k, om.MVector(v.x, v.y, v.z))

            elif isinstance(v, om.MMatrix):
                matrix_list = [v[i] for i in range(16)]
                new_matrix = om.MMatrix(matrix_list)
                setattr(result, k, new_matrix)

            elif isinstance(v, list):
                list_has_mpoints = any(
                    isinstance(item, om.MPoint) for item in v)

                if list_has_mpoints:
                    new_list = []
                    for item in v:
                        if isinstance(item, om.MPoint):
                            new_list.append(
                                om.MPoint(item.x, item.y, item.z, item.w))
                        else:
                            new_list.append(copy.deepcopy(item, memo))
                    setattr(result, k, new_list)
                else:
                    # Regular list without MPoints
                    setattr(result, k, copy.deepcopy(v, memo))

            else:
                try:
                    setattr(result, k, copy.deepcopy(v, memo))
                except TypeError:
                    print(
                        f'Could not deepcopy attribute `{k}`'
                        f' of type `{type(v).__name__}`'
                    )
                    setattr(result, k, None)

        return result

    @property
    def hasBeenNormalized(self):
        return bool(self.normalized)
