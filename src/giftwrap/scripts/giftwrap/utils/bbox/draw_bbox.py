import maya.cmds as cmds
from .bbox import BboxSpace

def drawBoundingBox(bbox, color=(0, 1, 1), space=BboxSpace.WORLD):
    """
    Draw bounding box as curves.

    Args:
        bbox:  ObjectOrientedBoundingBox instance
        color: Color of bounding box curves (RGB tuple)
        space: Cooordinate space (BboxSpace.WORLD or BboxSpace.OBJECT)

    Returns:
        The group node containing all curves
    """
    corners = bbox.getCorners(space)

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
