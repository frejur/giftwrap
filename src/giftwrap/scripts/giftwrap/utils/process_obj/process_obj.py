from pathlib import Path
import sys
import argparse
from dataclasses import dataclass
from enum import Enum, auto
import math
import os
from subpx_map import _SUBPIXEL_MAPPINGS

# Use relative paths when importing 'utils.Vec' to enable running this script
# without having to import the whole giftwrap package
vec_path = os.path.join(os.path.dirname(__file__), '..', 'custom_types')
sys.path.insert(0, os.path.abspath(vec_path))
from vec import Vec

_PRECISION = 3
_FORMAT_LEN = _PRECISION + 2
_SKIP_CHARS = ('#', '\n', 'g')
_SKIP_STRINGS = ('vt ', 'vn ', 'vp ')
_MAX_NUM_VERTS = 100
_MIN_WIDTH_UNITS = 4
_MIN_HEIGHT_UNITS = 3
_MAX_WIDTH_UNITS = int(_MIN_WIDTH_UNITS * 3.0)
_MAX_HEIGHT_UNITS = int(_MIN_HEIGHT_UNITS * 1.2)
_NEW_FILE_SUFFIX = '_new'
_EMPTY_CHAR = ' '
_NO_VTX = -1
_VTX_IDX_RHS = -2
_TOP_COMMENT = f"""\
# This is a processed .obj file:
# - All positional values have been confirmed to be in the range of:
#       (0, 0, 0) to (1, 0, 1)    Note: Y must be zero
# - The total number of vertices has been confirmed not to exceed {_MAX_NUM_VERTS}.
# - All positional values have been rounded to a precision of {_PRECISION} digits.
# - An ASCII diagram of the mesh's topology is included at the top of the file,
#   this diagram also indicates the vertex indices (0-indexed).
# - Since only vertex and face definitions are supported (and desired), all
#   other definitions, such as normals and groups, have been stripped from
#   the original data.
# - Relative vertex references are supported on import, but converted to
#   absolute references upon export."""

@dataclass
class GridPoint:
    index: int
    subpixels: int
    def __init__(self, index=_NO_VTX, subpixels=0):
        self.index = index
        self.subpixels = subpixels

@dataclass
class XY:
    x: int
    y: int
    def __add__(self, other):
        return XY(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return XY(self.x - other.x, self.y - other.y)
    def __mul__(self, other):
        return XY(self.x * other.x, self.y * other.y)
    def __rmul__(self, other):
        return self.__mul__(other)
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __iter__(self):
        yield self.x
        yield self.y
    def sign(self):
        return XY(int(math.copysign(1, self.x)), int(math.copysign(1, self.y)))

class ObjState(Enum):
    No_data = auto()
    Done_parsing = auto()
    Determined_grid_unit_size = auto()
    Created_compressed_grid_vertices = auto()
    Assigned_vertices_to_grid = auto()
    Finished = auto()

def _roundVec(vec):
    return Vec(*(round(v, _PRECISION) for v in vec))

class ProcessedObj:
    """
    A rudimentary Wavefront .obj parser that validates and performs various
    formatting operations on its contents.
    """
    def __init__(self, filepath):
        self.state = ObjState.No_data
        self.filepath = filepath

        # These lists share internal index ordering
        self.vertices = []
        self.vertices_rounded = []

        self.faces = [] # This list maps to the indices of the above

        self._extractData(filepath)
        self.state = ObjState.Done_parsing

        min_x_dist, min_z_dist = self._getMinDistanceForXZ()
        self.grid_unit_width = min_x_dist / _MIN_WIDTH_UNITS
        self.grid_unit_height = min_z_dist / _MIN_HEIGHT_UNITS

        self.state = ObjState.Determined_grid_unit_size

        self.grid_vertices = self._compressXZ(self.vertices)
        self.state = ObjState.Created_compressed_grid_vertices

        self.grid = []
        self._assignVerticesToGrid()
        self.state = ObjState.Assigned_vertices_to_grid

        self._plotFaceEdges()
        self.state = ObjState.Finished

    def _plotFaceEdges(self):
        if self.state != ObjState.Assigned_vertices_to_grid:
            raise RuntimeError("Invalid state")

        for face_vertices in self.faces:
            for idx_a in range(0, len(face_vertices)):
                idx_b = idx_a + 1 if idx_a < len(face_vertices) - 1 else 0
                vtx_pos_a = self.grid_vertices[face_vertices[idx_a]]
                vtx_pos_b = self.grid_vertices[face_vertices[idx_b]]
                grid_pos_a = self._getGridPositionXY(vtx_pos_a,
                                                     self.grid_unit_width,
                                                     self.grid_unit_height)
                grid_pos_b = self._getGridPositionXY(vtx_pos_b,
                                                     self.grid_unit_width,
                                                     self.grid_unit_height)
                self._plotLine(grid_pos_a, grid_pos_b)

    @staticmethod
    def _getGridPositionXY(vertex_position, unit_width, unit_height):
        row = round(vertex_position.z / unit_height + 1)
        col = round(vertex_position.x / unit_width + 1)
        return XY(col, row)

    def _assignVerticesToGrid(self):
        if self.state != ObjState.Created_compressed_grid_vertices:
            raise RuntimeError("Invalid state")

        max_x = max(self.grid_vertices, key=lambda v: v.x).x
        max_z = max(self.grid_vertices, key=lambda v: v.z).z
        cols = math.ceil(max_x / self.grid_unit_width) + 3
        rows = math.ceil(max_z / self.grid_unit_height) + 2

        self.grid = [[GridPoint() for _ in range(cols)] for _ in range(rows)]

        for idx, vtx_pos in enumerate(self.grid_vertices):
            xy = self._getGridPositionXY(vtx_pos,
                                         self.grid_unit_width,
                                         self.grid_unit_height)
            self.grid[xy.y][xy.x].index = idx
            if idx > 9:
                self.grid[xy.y][xy.x + 1].index = _VTX_IDX_RHS

    def _extractData(self, filepath):
        """
        Extracts vertices and faces from the given .obj file and stores them
        internally.
        """
        f = open(filepath,'r', encoding='utf-8')
        line_count = 0
        for line in f:
            line = line.strip()
            c = line[0] if len(line) >0 else None
            if c is None or c in _SKIP_CHARS:
                line_count += 1
                continue
            if len(line) >3 and c[:3] in _SKIP_STRINGS:
                line_count += 1
                continue

            if c == 'v':
                if len(self.vertices) == _MAX_NUM_VERTS:
                    raise RuntimeError(
                        f'Mesh contains more than {_MAX_NUM_VERTS} vertices.')

                vtx = self._extractVertex(line[1:])
                self._validate_vertex(vtx)
                vtx_rounded = _roundVec(vtx)
                self._validate_density(vtx, vtx_rounded)
                self.vertices.append(vtx)
                self.vertices_rounded.append(vtx_rounded)
            elif c == 'f':
                face = self._extractFace(line[1:])
                self.faces.append(face)
            else:
                raise RuntimeError(
                    f'Unknown leading character \'{c}\' at line #{line_count}')
            line_count += 1

        if len(self.faces) == 0:
            raise RuntimeError(f'Could not extract any data from "{filepath}"')


    def _extractVertex(self, s):
        """
        Extracts whitespace-separated coordinates and converts them into
        a vector.
            Args:
                s: The string.
            Returns:
                A vector (X, Y, Z)
        """
        xyz_strings = s.split()
        xyz_numbers = []
        for xyz_s in xyz_strings:
            try:
                xyz_numbers.append(float(xyz_s))
            except ValueError:
                raise RuntimeError(f'Cannot convert "{xyz_s}" to float')

        if len(xyz_numbers) != 3:
            raise RuntimeError(f'Expected 3 numbers, got "{s}"')
        return Vec(*xyz_numbers)

    def _extractFace(self, s):
        """
        Extracts whitespace-separated vertex indices and returns them as a list.
            Args:
                s: The string.
            Returns:
                A list of vertex indices.
        """
        idx_strings = s.split()
        idx_numbers = []
        for idx_s in idx_strings:
            try:
                actual_idx = int(idx_s)
            except ValueError:
                raise RuntimeError(f'Cannot convert "{idx_s}" to an index')

            if actual_idx == 0:
                raise RuntimeError('Vertex index cannot be zero.')
            elif abs(actual_idx) > len(self.vertices):
                raise RuntimeError(f'Vertex index out of range')

            if actual_idx < 0:
                actual_idx = len(self.vertices) + actual_idx
            else:
                actual_idx = actual_idx - 1

            idx_numbers.append(actual_idx)
        if len(idx_numbers) < 3:
            raise RuntimeError(f'Expected at least 3 vertices, got "{s}"')

        return idx_numbers

    @staticmethod
    def _validate_vertex(vertex_position):
        """
        Raises runtime error if the given vertex position is invalid:
            1. X & Z must be > 0 and < 1
            2. Y must be 0
        """
        if (vertex_position.x < 0 or vertex_position.x > 1 or
            vertex_position.z < 0 or vertex_position.z > 1):
            raise RuntimeError(f'Invalid vertex position "{vertex_position}"')

    def _validate_density(self, vtx_pos, vtx_pos_rounded):
        """
        Raises runtime error if the given vertex position is too close to any
        existing vertices.
        """
        overlap = None
        idx = 0
        for existing_rounded in self.vertices_rounded:
            if existing_rounded == vtx_pos_rounded:
                overlap = self.vertices[idx]
                break
            idx += 1
        if overlap is not None:
            raise RuntimeError('The placement of vertices is too dense:'
                               f'{vtx_pos} overlaps with {overlap}')

    def _getMinDistanceForXZ(self):
        if self.state != ObjState.Done_parsing:
            raise RuntimeError(f'Invalid state "{self.state}"')

        dist = { 'x': [], 'z': []}

        for i in range(len(self.vertices)):
            for j in range(i + 1, len(self.vertices)):
                x_dist = abs(self.vertices[i].x -
                             self.vertices[j].x)
                z_dist = abs(self.vertices[i].z -
                             self.vertices[j].z)

                if x_dist > 0:
                    dist['x'].append(x_dist)
                if z_dist > 0:
                    dist['z'].append(z_dist)

        return min(dist['x']), min(dist['z'])

    def _compressXZ(self, vertices):
        """
        Creates a copy of the given vertices where any sections void of vertices
        that exceed the max. width or height are compressed.
        Args:
            vertices: A list of vertex positions.
        Returns:
            A copy of the compressed vertices.
        """
        if self.state != ObjState.Determined_grid_unit_size:
            raise RuntimeError(f'Invalid state "{self.state}"')

        vtx_copy = [Vec(v.x, v.y, v.z) for v in vertices]

        # X compression
        sorted_x = sorted(vtx_copy, key=lambda v: v.x)
        max_width = self.grid_unit_width * _MAX_WIDTH_UNITS
        offset_x = 0
        for i in range(1, len(sorted_x)):
            sorted_x[i].x -= offset_x
            gap = sorted_x[i].x - sorted_x[i - 1].x
            if gap > max_width:
                adjusted_gap = gap - max_width
                sorted_x[i].x -= adjusted_gap
                offset_x += adjusted_gap

        # Z compression
        sorted_z = sorted(vtx_copy, key=lambda v: v.z)
        max_height = self.grid_unit_height * _MAX_HEIGHT_UNITS
        offset_z = 0
        for i in range(1, len(sorted_z)):
            sorted_z[i].z -= offset_z
            gap = sorted_z[i].z - sorted_z[i - 1].z
            if gap > max_height:
                adjusted_gap = gap - max_height
                sorted_z[i].z -= adjusted_gap
                offset_z += adjusted_gap

        return vtx_copy

    def _plotLine(self, start_xy, end_xy):
        delta = end_xy - start_xy
        sign = delta.sign()
        delta *= XY(sign.x, sign.y * -1) # Make values absolute, invert y

        subpx_current = start_xy * XY(2, 3)
        subpx_end = end_xy * XY(2, 3)
        subpx_delta = delta * XY(2, 3)
        error = sum(subpx_delta)

        while True:
            self._setSubPixel(subpx_current)
            if subpx_current == subpx_end:
                break
            threshold = 2 * error
            if subpx_delta.y <= threshold:
                error += subpx_delta.y
                subpx_current.x += sign.x
            if subpx_delta.x >= threshold:
                error += subpx_delta.x
                subpx_current.y += sign.y

    def _setSubPixel(self, position):
        grid_col = position.x // 2
        grid_row = position.y // 3

        # Check bounds
        if 0 <= grid_row < len(self.grid) and 0 <= grid_col < len(self.grid[0]):
            sub_x = position.x % 2  # 0=left   1=right
            sub_y = position.y % 3  # 0=top    1=middle    2=bottom

            #                                          _______
            #                                         | 5 | 4 |
            # Align bit position with ASCII mappings: | 3 | 2 |                               | 3 | 2 |
            #                                         | 1 | 0 |
            bit_position = (2 - sub_y) * 2 + (1 - sub_x)

            self.grid[grid_row][grid_col].subpixels |= (1 << bit_position)

    def export(self, output_file):
        """
        Writes the processed obj to disk.
        """
        if self.state != ObjState.Finished:
            raise RuntimeError(
                f'Invalid state, expected "{ObjState.Finished.name}" '
                f' but got "{self.state}"')

        with open(output_file, 'w', encoding='utf-8') as outfile:
            # Diagram
            outfile.write(f'{_TOP_COMMENT}\n#\n# Topology:\n')
            for row in self.grid:
                line = ''
                for ptnum, point in enumerate(row):
                    if point.index == _NO_VTX:
                        line += _SUBPIXEL_MAPPINGS[point.subpixels]
                    elif point.index == _VTX_IDX_RHS:
                        if ptnum == 0:
                            raise RuntimeError(
                                'The right portion of a vertex index must be at'
                                ' a position greater than 0 (Zero)')
                        line += str(row[ptnum - 1].index)[1]
                    else:
                        line += str(point.index)[0]
                outfile.write(f'# {line.rstrip()}\n')

            outfile.write('\n')

            # Vertices
            for vtx in self.vertices_rounded:
                outfile.write('v '
                              f'{vtx.x:{_FORMAT_LEN}.{_PRECISION}f} '
                              f'{vtx.y:{_FORMAT_LEN}.{_PRECISION}f} '
                              f'{vtx.z:{_FORMAT_LEN}.{_PRECISION}f}\n')

            outfile.write('\n')

            # Faces
            for face_vertices in self.faces:
                outfile.write(
                    f'f {" ".join(map(str, [n + 1 for n in face_vertices]))}\n')

def main():
    parser = argparse.ArgumentParser(
        description='Parses a Wavefront .obj file and applies formatting '
                    'to the data before re-exporting it'
    )
    parser.add_argument('input_file', help='Input obj file path')
    parser.add_argument('-o', '--output',
                        help='Output obj file path '
                            f'(default: adds "{_NEW_FILE_SUFFIX}" to'
                             ' input filename)')
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f'Error: Input file "{args.input_file}" does not exist')
        sys.exit(1)

    if not input_path.suffix.lower() == '.obj':
        print("Warning: Input file does not have .obj extension")

    if args.output:
        output_file = args.output
    else:
        output_file = f'{input_path.stem}{_NEW_FILE_SUFFIX}.obj'

    obj = ProcessedObj(input_path)
    obj.export(output_file)

if __name__ == "__main__":
    main()
