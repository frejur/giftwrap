# -*- coding: utf-8 *-*
"""
Gift Wrap Script, Fredrik Juréen 2025
"""

import maya.cmds as mc
import maya.mel as mel
import string
import random
import re
import itertools

obj_num_min = 3
obj_num_max = 32
obj_scale_min = 1.0
obj_scale_max = 6.0

wrap_list = []

class GiftWrap(object):
    """
    Wraps object in wrapping paper, creates control handle.
    Animation is then driven by the control handle attribute.
    Note: Just ignore this warning when animating the ribbon:
     "(Extrude): invalid path curve"

    Folding pattern:

     UL quadrant <--         :             --> UR quadrant
     ^                                                   ^
     |         F     G       :       H     I             |
               |     |               |     |
            1_  _____ _______________ _____ 
        (a+b)- |¤    |               |    ¤|   ^
               |  ¤  |       :       |  ¤  |   |-- C
            2_ |____¤|_______________|¤____|   v
               |     |       :       |     |     ^
               |     |               |     |     |-- D
               |     |       :       |     |     |
            3_ |_____|_______________|_____|     v
               |    ¤|               |¤    |   ^
               |  ¤  |       :       |  ¤  |   |
           (a)-|¤    |        ,origin|    ¤|   |
    -  -  - 4- |-----|-  -  -x-  -  -|-----|   |-- E  -  -
           (b)-|¤    |               |    ¤|   |
               |  ¤  |<===== A =====>|  ¤  |   |
            5_ |____¤|_______________|¤____|   v
               |     |               |     |
               |     |       :       |     |
               |     |               |     |
            6_ |_____|_______________|_____|
               |    ¤|               |¤    |
         (a+b),|  ¤  |       :       |  ¤  |
            7_ |%_ _ |_ _ _ _ _ _ _ _|_ _ %|  _____
            8_ |_____|_______________|_____|  _____ F
                             :
                                     <= B =>
                             :
    |                                                    |
    v                        :                           v
    BL quadrant <--          :             --> BR quadrant

                Right hand side diagonal folds:
            (Left hand side is identical but mirrored)

        Overlapping folds    :              No overlap 
                             :
      Upper  c               :    Upper                   Lower
      -------+---------      :    -----------------       -----------------
      |      +       +|      :    |               |       |+              |
      |        +   +  |      :    |               |       |  +            |
      |          a    |      :    |              +| - a   |    +          |
      |        +   +  |      :    |            +  |       |      +        |
      |      +       +| - b  :    |          +    |       |        +      |
      |    +          |      :    |        +      |       |          +    |
      |  +            |      :    |      +        |       |            +  |
      |+              |      :    |    +          |       |              +| - a
      -----------------      :    |  +            |       |               |
                             :    |+              |       |               |
                             :    -----------------       -----------------
                             :                            |               |
                             :    Mid                     |               |
      Mid                    :    -----------------       -----------------
       ---------------       :    |+              |
      |+              |      :    |  +            |
      |  +            |      :    |    +          |
      |    +          |      :    |      +        |
      |      +       +| - b  :    |        +      |
      |        +   +  |      :    |          +    |
      |          X    |      :    |            +  |
      |        +   +  |      :    |              +| - a
      |      +       +| - a  :    |               |
      |    +          |      :    |               |
      |  +            |      :    |               |
      |+              |      :    |              +| - b
      -----------------      :    |            +  |
                             :    |          +    |
      Lower                  :    |        +      |
       ---------------       :    |      +        |
      |+              |      :    |    +          |
      |  +            |      :    |  +            |
      |    +          |      :    |+              |
      |      +       +| - b  :    -----------------
      |        +   +  |      :
      |          +    |      :
      -----------------      :     
                 |           :
                 a           :

    """
    def __init__(self, name, mode='create', ribbon_size='L', thickness=0.02, wrap_color='random', ribbon_color='random', anim_s=1, anim_e=24):
        # Don't create object if node can't be found

        if  not mc.objExists(name):
            raise ValueError('Node "%s" does not exist' % (name,))

        self.wrap_name = name
        self.pivots = {}

        # Initialize members to None
        self.wrap_gift = None
        self.wrap_paper = None
        self.ctrl_handle = None

        self.main_group_name = None
        self.r_curve_group_name = None
        self.cluster_group_name = None
        self.obj_group_name = None
        self.fold_group_name = None
        self.gift_group_name = None
        self.ribbon_group_name = None

        self.side_depth = None
        self.side_height = None
        self.side_width = None

        self.f_plane = None
        self.folding_pattern = None
        self.fold_fix = None

        self.ribbons = None
        self.ribbon_points = None
        self.ribbon_width = None
        self.ribbon_prof = None
        self.r_profile = None

        self.bbox_width = None
        self.bbox_depth = None
        self.bbox_height = None

        self.ini_rp = None
        self.ini_sp = None
        self.ini_t = None
        self.ini_r = None
        self.ini_pivot_offs = None

        if mode == 'create':
            self.wrap_id = self.idGenerator(size=5) # Unique ID used for naming
            if thickness < 0.02 : thickness = 0.02
            self.wrap_thickness = thickness # Paper density in maya units
            self.ribbon_thickness = thickness
            self.ribbon_size = ribbon_size

            self.wrap_color = self.setColor(wrap_color, 1)
            self.ribbon_color = self.setColor(ribbon_color, 2)

            self.animation_start = anim_s
            self.animation_end = anim_e

            self.wrap_overlap = False # Should folds overlap...
            self.createGiftWrap()
        if mode == 'load':
            self.loadGiftWrap()

    def createGiftWrap(self, obj=None):
        self.ribbon_thickness = self.wrap_thickness

        # Group hierarchy
        mc.select(d=True) # Deselect
        self.main_group_name = mc.group(n="%s_gift_wrap_%s_GRP" % (self.wrap_name, self.wrap_id), empty=True)
        mc.select(d=True)
        self.ribbon_group_name = mc.group(n="ribbon_%s_GRP" % self.wrap_id, empty=True)
        mc.select(d=True)
        self.gift_group_name = mc.group(n="gift_%s_GRP" % self.wrap_id, empty=True)
        mc.select(d=True)
        self.fold_group_name = mc.group(n="fold_%s_GRP" % self.wrap_id, empty=True)
        mc.select(d=True)
        self.obj_group_name = mc.group(n="obj_%s_GRP" % self.wrap_id, empty=True)
        mc.select(d=True)
        self.cluster_group_name = mc.group(n="cluster_%s_GRP" % self.wrap_id, empty=True)
        mc.setAttr("%s.inheritsTransform" % self.cluster_group_name, 0) # Clusters need to stay where they are
        mc.select(d=True)
        self.r_curve_group_name = mc.group(n="ribbon_crv_%s_GRP" % self.wrap_id, empty=True)
        mc.setAttr("%s.inheritsTransform" % self.r_curve_group_name, 0) # Ribbon curves need to stay where they are

        if not obj:
            self.wrap_gift = self.wrap_name
            self.moveGift()

        side_a, side_d, side_e = self.getObjectSides() # bounding box
        self.fold_fix = side_d / 113 # value used to slightly offset the x value of some of the fold clusters that act up

        # parent all groups to ctrl handle
        self.ctrl_handle = self.createControlHandle(side_a*1.4)
        self.storeCtrlValues() # Store values in the CTRL handle for future reference
        mc.parent(self.ctrl_handle[0], self.main_group_name)
        mc.parent([self.fold_group_name, self.obj_group_name], self.gift_group_name)
        mc.parent([self.gift_group_name, self.cluster_group_name, self.ribbon_group_name, self.r_curve_group_name], self.ctrl_handle[0])
        mc.parent(self.wrap_gift, self.obj_group_name)

        mc.setAttr(self.cluster_group_name + ".visibility", 0)
        mc.setAttr(self.r_curve_group_name + ".visibility", 0)

        # get folding pattern, create folding plane
        self.folding_pattern = self.getFoldingPattern(side_a, side_d, side_e, self.wrap_thickness)
        self.f_plane, self.folding_pattern = self.createFoldingPlane(self.folding_pattern)
        mc.setAttr(self.f_plane[0] + ".visibility", 0)
        mc.parent(self.f_plane, self.fold_group_name)

        # create paper mesh and folding clusters
        self.wrap_paper = self.createPaper(self.f_plane, self.wrap_thickness)
        mc.setAttr(self.wrap_paper[0] + ".visibility", 1)
        self.pivots =  self.getFoldingPivots(self.folding_pattern)
        self.createClusters(self.folding_pattern)

        # get bounding box of final wrap (no  ribbon)
        self.foldPaper(16)
        self.side_width, self.side_height, self.side_depth = self.getWrapSides()
        self.foldPaper(0)

        # create ribbon
        self.ribbon_width = self.getRibbonWidth(self.ribbon_size, side_d, side_e)
        self.ribbon_points = self.getRibbonPoints(self.side_width, self.side_height, self.side_depth, side_a, self.wrap_thickness, self.ribbon_thickness, self.ribbon_width)
        self.ribbons, self.r_profile = self.createRibbon(self.ribbon_points, self.ribbon_thickness, self.ribbon_width)

        self.setDrivenKeys() # Animate

        self.applyColor()

        self.moveBack()

        self.setAnimation()

        mc.setAttr(self.ctrl_handle[0] + ".animation", 15)

    def removeGiftWrap(self):
        """
        Unparents object to be wrapped, resets rotate/translate,
        deletes everything else.
        """
        mc.parent(self.wrap_gift, world=True)
        mc.move(0, self.wrap_thickness, 0, self.wrap_gift, relativeTo=['parent'])
        mc.setAttr(self.wrap_gift + ".rotate", 0, 0, 0, type="double3")
        mc.delete(self.main_group_name)

    def loadGiftWrap(self):
        self.ctrl_handle = [self.wrap_name]
        self.retrieveCtrlValues()
        main_grp_name = "%s_gift_wrap_%s_GRP" % (self.wrap_name, self.wrap_id)
        gift_grp_name = "gift_%s_GRP" % (self.wrap_id,)
        obj_grp_name = "obj_%s_GRP" % (self.wrap_id,)
        obj_name = str(self.ctrl_handle[0]) + "|"
        obj_name += gift_grp_name + "|" + obj_grp_name + "|"
        obj_name += self.wrap_name
        fold_grp_name = "fold_%s_GRP" % (self.wrap_id,)
        paper_name = main_grp_name + "|" + str(self.ctrl_handle[0]) + "|"
        paper_name += gift_grp_name + "|" + fold_grp_name + "|"
        paper_name += "wrap_paper_%s" % (self.wrap_id,)
        self.wrap_gift = obj_name
        self.main_group_name = main_grp_name
        self.wrap_paper = [paper_name]
        self.ribbons = mc.listRelatives(self.ctrl_handle, allDescendents=True, fullPath=False, type="nurbsSurface")
        ribbon_prof = mc.listRelatives(self.ctrl_handle, allDescendents=True, fullPath=False, type="nurbsCurve")[-1]
        self.ribbon_prof = mc.listRelatives(ribbon_prof, allParents=True)

        self.ini_r = mc.getAttr(self.main_group_name + ".rotate")[0]
        self.ini_t = mc.getAttr(self.main_group_name + ".translate")[0]

    def storeCtrlValues(self):
        mc.setAttr(self.ctrl_handle[0] + ".wrap_name", self.wrap_name, type="string")
        mc.setAttr(self.ctrl_handle[0] + ".wrap_id", self.wrap_id, type="string")
        mc.setAttr(self.ctrl_handle[0] + ".wrap_thickness", self.wrap_thickness)
        mc.setAttr(self.ctrl_handle[0] + ".wrap_color", self.wrap_color, type="string")
        mc.setAttr(self.ctrl_handle[0] + ".ribbon_size", self.ribbon_size, type="string")
        mc.setAttr(self.ctrl_handle[0] + ".ribbon_color", self.ribbon_color, type="string")
        mc.setAttr(self.ctrl_handle[0] + ".animation_start", self.animation_start)
        mc.setAttr(self.ctrl_handle[0] + ".animation_end", self.animation_end)

    def retrieveCtrlValues(self):
        self.wrap_name = mc.getAttr(self.ctrl_handle[0] + ".wrap_name")
        self.wrap_id = mc.getAttr(self.ctrl_handle[0] + ".wrap_id")
        self.wrap_thickness = mc.getAttr(self.ctrl_handle[0] + ".wrap_thickness")
        self.wrap_color = mc.getAttr(self.ctrl_handle[0] + ".wrap_color")
        self.ribbon_size = mc.getAttr(self.ctrl_handle[0] + ".ribbon_size")
        self.ribbon_color = mc.getAttr(self.ctrl_handle[0] + ".ribbon_color")
        self.animation_start = mc.getAttr(self.ctrl_handle[0] + ".animation_start")
        self.animation_end = mc.getAttr(self.ctrl_handle[0] + ".animation_end")

    def moveGift(self):
        """
        Move object to be wrapped(the gift) to the origin.
        Before wrapping we want to position the gift:
         > The largest sides facing down/up along the y-axis
         > The smallest sides pointing to the left/right along the x-axis
        """

        # Store initial transform values
        self.ini_r = mc.xform(self.wrap_gift, query=True, rotation=True, worldSpace=True)
        self.ini_t = mc.xform(self.wrap_gift, query=True, translation=True, worldSpace=True)
    
        # Store initial pivot values
        self.ini_sp = mc.xform(self.wrap_gift, query=True, scalePivot=True, worldSpace=True)
        self.ini_rp = mc.xform(self.wrap_gift, query=True, rotatePivot=True, worldSpace=True)
        
        mc.xform(self.wrap_gift, centerPivots=True)
        mc.xform(self.wrap_gift, rotation=[0, 0, 0], objectSpace=True)
        mc.move(0, 0, 0, self.wrap_gift, rotatePivotRelative=True)

        # Get bounding box dimensions
        bbox = mc.exactWorldBoundingBox(self.wrap_gift)
        bbox_min = [bbox[0], bbox[1], bbox[2]]
        bbox_max = [bbox[3], bbox[4], bbox[5]]
        bbox_minmax = [bbox_max[0] - bbox_min[0], bbox_max[1] - bbox_min[1], bbox_max[2] - bbox_min[2]]
        self.bbox_height = bbox_minmax[1]
        self.bbox_depth = bbox_minmax[2]
        self.bbox_width = bbox_minmax[0]
    
        # Determine sides with the largest and smallest area
        side_area = [
            ('dw', self.bbox_depth * self.bbox_width),
            ('dh', self.bbox_depth * self.bbox_height),
            ('wh', self.bbox_width * self.bbox_height)
        ]
        
        side_area.sort(key = lambda sArea: sArea[1])
        smallest_a = side_area[0][0]
        largest_a = side_area[2][0]
        
        # Positions object, largest side facing down(Y), pivot centered to bottom
        gift_new_pivot = []

        # Offset pivot
        if largest_a == 'dw':
            gift_new_pivot = [0, self.bbox_height * -0.5, 0]
        elif largest_a == 'dh':
            gift_new_pivot = [self.bbox_width * -0.5, 0, 0]
        elif largest_a == 'wh':
            gift_new_pivot = [0, 0, self.bbox_depth * 0.5]
        
        mc.xform(self.wrap_gift, scalePivot=gift_new_pivot, relative=True)
        mc.xform(self.wrap_gift, rotatePivot=gift_new_pivot, relative=True)
        self.ini_pivot_offs = [0, mc.xform(self.wrap_gift, query=True, scalePivot=True, worldSpace=True)[1], 0]
                
        # Place gift on top of paper
        mc.move(0, self.wrap_thickness, 0, self.wrap_gift, rotatePivotRelative=True)

        if largest_a == 'dh':
            mc.xform(self.wrap_gift, rotation=[0, 0, 90], objectSpace=True)
        elif largest_a == 'wh':
            mc.xform(self.wrap_gift, rotation=[90, 0, 0], objectSpace=True)

        # Rotates object, smallest side pointing left/right(X)
        if ((largest_a == 'dw' and smallest_a == 'wh') or
            (largest_a == 'dh' and smallest_a == 'wh') or
            (largest_a == 'wh' and smallest_a == 'dw')):
            mc.xform(self.wrap_gift, rotation=[0, 90, 0], euler=True, relative=True, objectSpace=True)

        # Restore pivots
        mc.xform(self.wrap_gift, rotatePivot=self.ini_rp, objectSpace=True)
        mc.xform(self.wrap_gift, scalePivot=self.ini_sp, objectSpace=True)
        
                
                
    def moveBack(self):
        """
        Moves the object back to its initial position
        """
        mc.setAttr(self.main_group_name + ".translate", self.ini_t[0], self.ini_t[1], self.ini_t[2], type="double3")
        mc.setAttr(self.main_group_name + ".rotate", self.ini_r[0], self.ini_r[1], self.ini_r[2], type="double3")
        
        # Place the gift at the lowest center point of the original object
        mc.xform(self.main_group_name, translation=self.ini_pivot_offs, euler=True, relative=True, worldSpace=True)

    def createControlHandle(self, radius):
        ctrl = mc.circle(radius=radius, name="CTRL_gift_" + self.wrap_id)

        # Add custom attributes
        mc.addAttr(ctrl[0], longName="animation", keyable=True)
        mc.addAttr(ctrl[0], longName="wrap_name", dataType='string', hidden=True, keyable=False)
        mc.addAttr(ctrl[0], longName="wrap_id", dataType='string', hidden=True, keyable=False)
        mc.addAttr(ctrl[0], longName="wrap_thickness", attributeType='float', hidden=True, keyable=False)
        mc.addAttr(ctrl[0], longName="wrap_color", dataType='string', hidden=True, keyable=False)
        mc.addAttr(ctrl[0], longName="ribbon_size", dataType='string', hidden=True, keyable=False)
        mc.addAttr(ctrl[0], longName="ribbon_color", dataType='string', hidden=True, keyable=False)
        mc.addAttr(ctrl[0], longName="animation_start", hidden=True, keyable=False)
        mc.addAttr(ctrl[0], longName="animation_end", hidden=True, keyable=False)
        
        # Set rotation and freeze transformations
        mc.setAttr(ctrl[0] + ".rotateX", 90)
        mc.makeIdentity(ctrl[0], apply=True)
        
        return ctrl

    @staticmethod
    def setColor(color, ctype=1):
        c_list = ['green', 'red', 'blue', 'yellow']
        if ctype == 1 : c_list += ['white', 'black']
        if not color in c_list:
            random.shuffle(c_list)
            color = c_list[0]

        return color

    def getFoldingPattern(self, gft_side_a, gft_side_d, gft_side_e, gft_thick):
        """
        Finds the coordinates for the wrapping folds
        """
        # y-axis
        y_gft = gft_thick / 2

        # calculate sides
        gft_side_a += gft_thick
        gft_side_d += gft_thick
        gft_side_b = gft_side_d * 0.6
        gft_side_c = gft_side_e / 2 + y_gft
        gft_side_e += gft_thick # needs to be run last

        # check if folds will overlap
        self.wrap_overlap = gft_side_e < (2 * gft_side_b)

        # calculate side f
        if not self.wrap_overlap:
            gft_side_f = gft_side_c - gft_side_b
        else:
            gft_side_f = gft_side_b - gft_side_c

        # x-axis
        x_h = (gft_side_a / 2)
        x_i = x_h + gft_side_b
        x_g = x_h * -1
        x_f = x_i * -1

        # y-axis
        z_5 = (gft_side_e / 2)
        z_6 = z_5 + gft_side_d
        z_7 = z_6 + gft_side_c
        z_3 = z_5 * -1
        z_2 = z_6 * -1

        # calculate z-1 axis
        if not self.wrap_overlap:
            z_1 = z_7 * -1
        else:
            z_1 = z_2 - gft_side_b

        # calculate z-8 axis
        if not self.wrap_overlap:
            z_8 = z_7 + gft_side_f
        else:
            z_8 = z_7

        # Coordinates in world space, vertex ID is added later
        gift_fold_points = {
            'F1': [[x_f, y_gft, z_1], 0], 'F2': [[x_f, y_gft, z_2], 0], 'F3': [[x_f, y_gft, z_3], 0],
            'F4': [[x_f, y_gft, 0.0], 0], 'F5': [[x_f, y_gft, z_5], 0], 'F6': [[x_f, y_gft, z_6], 0],
            'F7': [[x_f, y_gft, z_7], 0], 'F8': [[x_f, y_gft, z_8], 0],
            'G1': [[x_g, y_gft, z_1], 0],
            'G2': [[x_g, y_gft, z_2], 0], 'G3': [[x_g, y_gft, z_3], 0], 'G4': [[x_g, y_gft, 0.0], 0],
            'G5': [[x_g, y_gft, z_5], 0], 'G6': [[x_g, y_gft, z_6], 0], 'G7': [[x_g, y_gft, z_7], 0],
            'G8': [[x_g, y_gft, z_8], 0],
            'H1': [[x_h, y_gft, z_1], 0], 'H2': [[x_h, y_gft, z_2], 0], 'H3': [[x_h, y_gft, z_3], 0],
            'H4': [[x_h, y_gft, 0.0], 0], 'H5': [[x_h, y_gft, z_5], 0], 'H6': [[x_h, y_gft, z_6], 0],
            'H7': [[x_h, y_gft, z_7], 0], 'H8': [[x_h, y_gft, z_8], 0],
            'I1': [[x_i, y_gft, z_1], 0],
            'I2': [[x_i, y_gft, z_2], 0], 'I3': [[x_i, y_gft, z_3], 0], 'I4': [[x_i, y_gft, 0.0], 0],
            'I5': [[x_i, y_gft, z_5], 0], 'I6': [[x_i, y_gft, z_6], 0], 'I7': [[x_i, y_gft, z_7], 0],
            'I8': [[x_i, y_gft, z_8], 0], 'I4a': [[x_i, y_gft, z_3], 0]
        }

        # calculate diagonal folds F4a, F4b, I4a, I4b
        gift_fold_points['I4a'][0][2] += gft_side_b
        gift_fold_points['I4b'] = [[x_i, y_gft, z_5], 0]
        gift_fold_points['I4b'][0][2] -= gft_side_b
        
        gift_fold_points['F4a'] = [[x_f, y_gft, z_3], 0]
        gift_fold_points['F4a'][0][2] += gft_side_b
        gift_fold_points['F4b'] = [[x_f, y_gft, z_5], 0]
        gift_fold_points['F4b'][0][2] -= gft_side_b
        
        # calculate intersecting points HI4, FG4
        if self.wrap_overlap:
            gift_fold_points['HI4'] = [[x_h, y_gft, 0.0], 0]
            gift_fold_points['HI4'][0][0] += gft_side_e / 2
            gift_fold_points['FG4'] = [[x_g, y_gft, 0.0], 0]
            gift_fold_points['FG4'][0][0] -= gft_side_e / 2
        
        # calculate diagonal folds F1a, I1a
        if not self.wrap_overlap:
            gift_fold_points['I1a'] = [[x_i, y_gft, z_2], 0]
            gift_fold_points['I1a'][0][2] -= gft_side_b
            gift_fold_points['F1a'] = [[x_f, y_gft, z_2], 0]
            gift_fold_points['F1a'][0][2] -= gft_side_b
        else:
            gift_fold_points['I1a'] = [[x_i, y_gft, z_1], 0]
            gift_fold_points['I1a'][0][2] += gft_side_b - gft_side_c
            gift_fold_points['I1a'][0][0] -= gft_side_b - gft_side_c
            gift_fold_points['F1a'] = [[x_f, y_gft, z_1], 0]
            gift_fold_points['F1a'][0][2] += gft_side_b - gft_side_c
            gift_fold_points['F1a'][0][0] += gft_side_b - gft_side_c
        
        # calculate diagonal folds F1b, I1b
        if self.wrap_overlap:
            gift_fold_points['I1b'] = [[x_i, y_gft, z_1], 0]
            gift_fold_points['I1b'][0][2] += (gft_side_b - gft_side_c) * 2
            gift_fold_points['F1b'] = [[x_f, y_gft, z_1], 0]
            gift_fold_points['F1b'][0][2] += (gft_side_b - gft_side_c) * 2
        
        # calculate diagonal folds F1c, I1c
        if self.wrap_overlap:
            gift_fold_points['I1c'] = [[x_i, y_gft, z_1], 0]
            gift_fold_points['I1c'][0][0] -= (gft_side_b - gft_side_c) * 2
            gift_fold_points['F1c'] = [[x_f, y_gft, z_1], 0]
            gift_fold_points['F1c'][0][0] += (gft_side_b - gft_side_c) * 2
        
        # calculate diagonal folds F7a, I7a
        if not self.wrap_overlap:
            gift_fold_points['I7a'] = [[x_i, y_gft, z_6], 0]
            gift_fold_points['I7a'][0][2] += gft_side_b
            gift_fold_points['F7a'] = [[x_f, y_gft, z_6], 0]
            gift_fold_points['F7a'][0][2] += gft_side_b
        else:
            gift_fold_points['I7a'] = [[x_i, y_gft, z_7], 0]
            gift_fold_points['I7a'][0][2] -= gft_side_b - gft_side_c
            gift_fold_points['F7a'] = [[x_f, y_gft, z_7], 0]
            gift_fold_points['F7a'][0][2] -= gft_side_b - gft_side_c
        
        # calculate diagonal folds F7b, I7b
        if self.wrap_overlap:
            gift_fold_points['I7b'] = [[x_i, y_gft, z_7], 0]
            gift_fold_points['I7b'][0][0] -= gft_side_b - gft_side_c
            gift_fold_points['F7b'] = [[x_f, y_gft, z_7], 0]
            gift_fold_points['F7b'][0][0] += gft_side_b - gft_side_c

        return gift_fold_points

    @staticmethod
    def setVertexPosition(mesh_name, vertex_index, position):
        """
        Helper function to set the position of a vertex in a mesh
        """
        vertex_path = mesh_name + ".vtx[%d]" % vertex_index
        mc.xform(vertex_path, translation=position, worldSpace=True)

    @staticmethod
    def mergeVertices(vertex_list):
        """
        Helper function to merge a list of vertices
        """
        mc.polyMergeVertex(vertex_list, constructionHistory=0)

    @staticmethod
    def mergeVertexRange(mesh_name, start_index, end_index):
        """
        Helper function to merge a range of vertices in a mesh
        """
        vertex_list = []
        for i in range(start_index, end_index + 1):
            vertex_list.append(mesh_name + ".vtx[%d]" % i)
        
        mc.polyMergeVertex(vertex_list, constructionHistory=0)

    @staticmethod
    def deleteEdge(mesh_name, edge_index, cleanup=True):
        """
        Helper function to delete an edge from a mesh
        """
        edge_path = mesh_name + ".e[%d]" % edge_index
        mc.polyDelEdge(edge_path, constructionHistory=0, cleanVertices=cleanup)

    @staticmethod
    def getVertexRangeList(mesh_name, range_list):
        """
        Helper function to create a list of vertex component paths from multiple ranges
        """
        vertex_list = []
        for start, end in range_list:
            for i in range(start, end + 1):
                vertex_list.append(mesh_name + ".vtx[%d]" % i)
        return vertex_list

    def createFoldingPlane(self, wrap_points):
        """
        Create polyplane that will fold up and serve as a wrap deformer
        """
        plane_name = "folding_plane_%s" % (self.wrap_id,)
        wrap_fold_pln = mc.polyPlane(name=plane_name, subdivisionsX=3, subdivisionsY=6, constructionHistory=0)

        # Moves vertices to align them with folding pattern,
        self.setVertexPosition(wrap_fold_pln[0], 0, wrap_points['F8'][0])
        self.setVertexPosition(wrap_fold_pln[0], 1, wrap_points['G8'][0])
        self.setVertexPosition(wrap_fold_pln[0], 2, wrap_points['H8'][0])
        self.setVertexPosition(wrap_fold_pln[0], 3, wrap_points['I8'][0])
        self.setVertexPosition(wrap_fold_pln[0], 4, wrap_points['F7'][0])
        self.setVertexPosition(wrap_fold_pln[0], 5, wrap_points['G7'][0])
        self.setVertexPosition(wrap_fold_pln[0], 6, wrap_points['H7'][0])
        self.setVertexPosition(wrap_fold_pln[0], 7, wrap_points['I7'][0])
        self.setVertexPosition(wrap_fold_pln[0], 8, wrap_points['F6'][0])
        self.setVertexPosition(wrap_fold_pln[0], 9, wrap_points['G6'][0])
        self.setVertexPosition(wrap_fold_pln[0], 10, wrap_points['H6'][0])
        self.setVertexPosition(wrap_fold_pln[0], 11, wrap_points['I6'][0])
        self.setVertexPosition(wrap_fold_pln[0], 12, wrap_points['F5'][0])
        self.setVertexPosition(wrap_fold_pln[0], 13, wrap_points['G5'][0])
        self.setVertexPosition(wrap_fold_pln[0], 14, wrap_points['H5'][0])
        self.setVertexPosition(wrap_fold_pln[0], 15, wrap_points['I5'][0])
        self.setVertexPosition(wrap_fold_pln[0], 16, wrap_points['F3'][0])
        self.setVertexPosition(wrap_fold_pln[0], 17, wrap_points['G3'][0])
        self.setVertexPosition(wrap_fold_pln[0], 18, wrap_points['H3'][0])
        self.setVertexPosition(wrap_fold_pln[0], 19, wrap_points['I3'][0])
        self.setVertexPosition(wrap_fold_pln[0], 20, wrap_points['F2'][0])
        self.setVertexPosition(wrap_fold_pln[0], 21, wrap_points['G2'][0])
        self.setVertexPosition(wrap_fold_pln[0], 22, wrap_points['H2'][0])
        self.setVertexPosition(wrap_fold_pln[0], 23, wrap_points['I2'][0])
        self.setVertexPosition(wrap_fold_pln[0], 24, wrap_points['F1'][0])
        self.setVertexPosition(wrap_fold_pln[0], 25, wrap_points['G1'][0])
        self.setVertexPosition(wrap_fold_pln[0], 26, wrap_points['H1'][0])
        self.setVertexPosition(wrap_fold_pln[0], 27, wrap_points['I1'][0])

        # Models mid right diagonal folds
        if not self.wrap_overlap:
            temp_face = wrap_fold_pln[0] + ".f[11]"
            mc.polySubdivideFacet(temp_face, divisionsU=1, divisionsV=3, subdMethod=1, constructionHistory=0)
            self.setVertexPosition(wrap_fold_pln[0], 31, wrap_points['H3'][0])
            self.setVertexPosition(wrap_fold_pln[0], 30, wrap_points['H5'][0])
            self.setVertexPosition(wrap_fold_pln[0], 29, wrap_points['I4a'][0])
            self.setVertexPosition(wrap_fold_pln[0], 28, wrap_points['I4b'][0])
            self.mergeVertexRange(wrap_fold_pln[0], 14, 31)
        else:
            temp_face = wrap_fold_pln[0] + ".f[11]"
            mc.polySubdivideFacet(temp_face, divisionsU=2, divisionsV=3, subdMethod=1, constructionHistory=0)
            self.setVertexPosition(wrap_fold_pln[0], 35, wrap_points['HI4'][0])
            self.setVertexPosition(wrap_fold_pln[0], 34, wrap_points['HI4'][0])
            self.setVertexPosition(wrap_fold_pln[0], 33, wrap_points['H5'][0])
            self.setVertexPosition(wrap_fold_pln[0], 32, wrap_points['H3'][0])
            self.setVertexPosition(wrap_fold_pln[0], 31, wrap_points['H5'][0])
            self.setVertexPosition(wrap_fold_pln[0], 30, wrap_points['I4b'][0])
            self.setVertexPosition(wrap_fold_pln[0], 29, wrap_points['I4a'][0])
            self.setVertexPosition(wrap_fold_pln[0], 28, wrap_points['H3'][0])
            self.mergeVertexRange(wrap_fold_pln[0], 14, 35)

        # Models mid left diagonal folds
        if not self.wrap_overlap:
            temp_face = wrap_fold_pln[0] + ".f[9]"
            mc.polySubdivideFacet(temp_face, divisionsU=1, divisionsV=3, subdMethod=1, constructionHistory=0)
            self.setVertexPosition(wrap_fold_pln[0], 31, wrap_points['G3'][0])
            self.setVertexPosition(wrap_fold_pln[0], 30, wrap_points['G5'][0])
            self.setVertexPosition(wrap_fold_pln[0], 33, wrap_points['F4a'][0])
            self.setVertexPosition(wrap_fold_pln[0], 32, wrap_points['F4b'][0])
            self.mergeVertexRange(wrap_fold_pln[0], 12, 33)
        else:
            temp_face = wrap_fold_pln[0] + ".f[9]"
            mc.polySubdivideFacet(temp_face, divisionsU=2, divisionsV=3, subdMethod=1, constructionHistory=0)
            self.setVertexPosition(wrap_fold_pln[0], 38, wrap_points['FG4'][0])
            self.setVertexPosition(wrap_fold_pln[0], 37, wrap_points['FG4'][0])
            self.setVertexPosition(wrap_fold_pln[0], 36, wrap_points['G5'][0])
            self.setVertexPosition(wrap_fold_pln[0], 35, wrap_points['F4b'][0])
            self.setVertexPosition(wrap_fold_pln[0], 34, wrap_points['F4a'][0])
            self.setVertexPosition(wrap_fold_pln[0], 33, wrap_points['G3'][0])
            self.setVertexPosition(wrap_fold_pln[0], 32, wrap_points['G5'][0])
            self.setVertexPosition(wrap_fold_pln[0], 31, wrap_points['G3'][0])
            self.mergeVertexRange(wrap_fold_pln[0], 12, 38)

        # Models top right diagonal folds
        if not self.wrap_overlap:
            temp_face = wrap_fold_pln[0] + ".f[17]"
            mc.polySubdivideFacet(temp_face, divisionsU=1, divisionsV=2, subdMethod=1, constructionHistory=0)
            self.setVertexPosition(wrap_fold_pln[0], 33, wrap_points['H2'][0])
            self.setVertexPosition(wrap_fold_pln[0], 32, wrap_points['I1a'][0])
            self.mergeVertexRange(wrap_fold_pln[0], 22, 33)
        else:
            temp_face = wrap_fold_pln[0] + ".f[16]"
            mc.polySubdivideFacet(temp_face, divisionsU=2, divisionsV=2, subdMethod=1, constructionHistory=0)
            self.setVertexPosition(wrap_fold_pln[0], 38, wrap_points['I1a'][0])
            self.setVertexPosition(wrap_fold_pln[0], 37, wrap_points['H2'][0])
            self.setVertexPosition(wrap_fold_pln[0], 35, wrap_points['I1b'][0])
            self.setVertexPosition(wrap_fold_pln[0], 34, wrap_points['I1'][0])
            self.mergeVertexRange(wrap_fold_pln[0], 22, 38)
            self.deleteEdge(wrap_fold_pln[0], 62)

        # Models top left diagonal folds
        if not self.wrap_overlap:
            temp_face = wrap_fold_pln[0] + ".f[15]"
            mc.polySubdivideFacet(temp_face, divisionsU=1, divisionsV=2, subdMethod=1, constructionHistory=0)
            self.setVertexPosition(wrap_fold_pln[0], 33, wrap_points['G2'][0])
            self.setVertexPosition(wrap_fold_pln[0], 34, wrap_points['F1a'][0])
            self.mergeVertexRange(wrap_fold_pln[0], 21, 33)
        else:
            temp_face = wrap_fold_pln[0] + ".f[14]"
            mc.polySubdivideFacet(temp_face, divisionsU=2, divisionsV=2, subdMethod=1, constructionHistory=0)
            self.setVertexPosition(wrap_fold_pln[0], 40, wrap_points['F1a'][0])
            self.setVertexPosition(wrap_fold_pln[0], 39, wrap_points['G2'][0])
            self.setVertexPosition(wrap_fold_pln[0], 36, wrap_points['F1'][0])
            self.setVertexPosition(wrap_fold_pln[0], 38, wrap_points['F1b'][0])
            self.mergeVertexRange(wrap_fold_pln[0], 20, 40)
            self.deleteEdge(wrap_fold_pln[0], 65)

        # Models bottom right diagonal folds
        if not self.wrap_overlap:
            temp_face = wrap_fold_pln[0] + ".f[5]"
            mc.polySubdivideFacet(temp_face, divisionsU=1, divisionsV=2, subdMethod=1, constructionHistory=0)
            self.setVertexPosition(wrap_fold_pln[0], 35, wrap_points['H6'][0])
            self.setVertexPosition(wrap_fold_pln[0], 34, wrap_points['I7a'][0])
            self.mergeVertexRange(wrap_fold_pln[0], 10, 35)
        else:
            temp_face = [wrap_fold_pln[0] + ".f[2]", wrap_fold_pln[0] + ".f[5]"]
            mc.polySubdivideFacet(temp_face, divisionsU=2, divisionsV=1, subdMethod=1, constructionHistory=0)
            self.setVertexPosition(wrap_fold_pln[0], 40, wrap_points['I7b'][0])
            self.setVertexPosition(wrap_fold_pln[0], 39, wrap_points['I7b'][0])
            self.setVertexPosition(wrap_fold_pln[0], 7, wrap_points['I7a'][0])
            self.setVertexPosition(wrap_fold_pln[0], 6, wrap_points['H6'][0])
            vertex_ranges = [[2, 3], [6, 7], [10, 11], [38, 40]]
            temp_vertex = self.getVertexRangeList(wrap_fold_pln[0], vertex_ranges)
            self.mergeVertices(temp_vertex)
            self.deleteEdge(wrap_fold_pln[0], 67)

        # Models bottom left diagonal folds
        if not self.wrap_overlap:
            temp_face = wrap_fold_pln[0] + ".f[3]"
            mc.polySubdivideFacet(temp_face, divisionsU=1, divisionsV=2, subdMethod=1, constructionHistory=0)
            self.setVertexPosition(wrap_fold_pln[0], 35, wrap_points['G6'][0])
            self.setVertexPosition(wrap_fold_pln[0], 36, wrap_points['F7a'][0])
            self.mergeVertexRange(wrap_fold_pln[0], 9, 35)
        else:
            temp_face = [wrap_fold_pln[0] + ".f[0]", wrap_fold_pln[0] + ".f[3]"]
            mc.polySubdivideFacet(temp_face, divisionsU=2, divisionsV=1, subdMethod=1, constructionHistory=0)
            self.setVertexPosition(wrap_fold_pln[0], 40, wrap_points['F7b'][0])
            self.setVertexPosition(wrap_fold_pln[0], 39, wrap_points['F7b'][0])
            self.setVertexPosition(wrap_fold_pln[0], 4, wrap_points['F7a'][0])
            self.setVertexPosition(wrap_fold_pln[0], 5, wrap_points['G6'][0])
            vertex_ranges = [[0, 1], [4, 5], [8, 9], [38, 40]]
            temp_vertex = self.getVertexRangeList(wrap_fold_pln[0], vertex_ranges)
            self.mergeVertices(temp_vertex)
            self.deleteEdge(wrap_fold_pln[0], 67)

        # Model top diagonal fold points F1c, I1c
        if self.wrap_overlap:
            temp_face = [wrap_fold_pln[0] + ".f[15]", wrap_fold_pln[0] + ".f[25]"]
            mc.polySubdivideFacet(temp_face, divisionsU=1, divisionsV=2, subdMethod=1, constructionHistory=0)
            self.setVertexPosition(wrap_fold_pln[0], 41, wrap_points['I1c'][0])
            self.setVertexPosition(wrap_fold_pln[0], 40, wrap_points['I1a'][0])
            self.setVertexPosition(wrap_fold_pln[0], 39, wrap_points['F1c'][0])
            self.setVertexPosition(wrap_fold_pln[0], 38, wrap_points['F1a'][0])
            self.mergeVertexRange(wrap_fold_pln[0], 33, 41)

        # Store vertex IDs in folding pattern
        if not self.wrap_overlap:
            # x = 8
            wrap_points['F8'][1] = 0
            wrap_points['G8'][1] = 1
            wrap_points['H8'][1] = 2
            wrap_points['I8'][1] = 3
            # x = 7
            wrap_points['F7'][1] = 4
            wrap_points['G7'][1] = 5
            wrap_points['H7'][1] = 6
            wrap_points['I7'][1] = 7
            # diagonal folds x = 7
            wrap_points['F7a'][1] = 35
            wrap_points['I7a'][1] = 34
            # x = 6
            wrap_points['F6'][1] = 8
            wrap_points['G6'][1] = 9
            wrap_points['H6'][1] = 10
            wrap_points['I6'][1] = 11
            # x = 5
            wrap_points['F5'][1] = 12
            wrap_points['G5'][1] = 13
            wrap_points['H5'][1] = 14
            wrap_points['I5'][1] = 15
            # diagonal folds x = 4
            wrap_points['F4a'][1] = 31
            wrap_points['F4b'][1] = 30
            wrap_points['I4a'][1] = 29
            wrap_points['I4b'][1] = 28
            # x = 3
            wrap_points['F3'][1] = 16
            wrap_points['G3'][1] = 17
            wrap_points['H3'][1] = 18
            wrap_points['I3'][1] = 19
            # x = 2
            wrap_points['F2'][1] = 20
            wrap_points['G2'][1] = 21
            wrap_points['H2'][1] = 22
            wrap_points['I2'][1] = 23
            # x = 1
            wrap_points['F1'][1] = 24
            wrap_points['G1'][1] = 25
            wrap_points['H1'][1] = 26
            wrap_points['I1'][1] = 27
            # x = 1 diagonal folds
            wrap_points['F1a'][1] = 33
            wrap_points['I1a'][1] = 32
        else:
            # x = 7
            wrap_points['F7'][1] = 0
            wrap_points['G7'][1] = 1
            wrap_points['H7'][1] = 2
            wrap_points['I7'][1] = 3
            # x = 7 diagonal folds
            wrap_points['F7a'][1] = 4
            wrap_points['F7b'][1] = 37
            wrap_points['I7a'][1] = 7
            wrap_points['I7b'][1] = 36
            # x = 6
            wrap_points['F6'][1] = 8
            wrap_points['G6'][1] = 5
            wrap_points['H6'][1] = 6
            wrap_points['I6'][1] = 9
            # x = 5
            wrap_points['F5'][1] = 10
            wrap_points['G5'][1] = 11
            wrap_points['H5'][1] = 12
            wrap_points['I5'][1] = 13
            # x = 4
            wrap_points['FG4'][1] = 31
            wrap_points['F4a'][1] = 29
            wrap_points['F4b'][1] = 30
            wrap_points['HI4'][1] = 28
            wrap_points['I4a'][1] = 26
            wrap_points['I4b'][1] = 27
            # x = 3
            wrap_points['F3'][1] = 14
            wrap_points['G3'][1] = 15
            wrap_points['H3'][1] = 16
            wrap_points['I3'][1] = 17
            # x = 2
            wrap_points['F2'][1] = 18
            wrap_points['G2'][1] = 19
            wrap_points['H2'][1] = 20
            wrap_points['I2'][1] = 21
            # x = 1
            wrap_points['F1'][1] = 22
            wrap_points['G1'][1] = 23
            wrap_points['H1'][1] = 24
            wrap_points['I1'][1] = 25
            # x = 1 diagonal folds
            wrap_points['F1a'][1] = 35
            wrap_points['F1b'][1] = 34
            wrap_points['F1c'][1] = 38
            wrap_points['I1a'][1] = 33
            wrap_points['I1b'][1] = 32
            wrap_points['I1c'][1] = 39

        return wrap_fold_pln, wrap_points

    @staticmethod
    def getFoldingPivots(points):
        """
        Get pivots for the clusters controlling the folding.
        Returns them as a dict.
        Var names: 1U = 1st fold, upper quadrant, and so on
        """
         # Helper function to average two positions
        def avgPos(pos1, pos2):
            return [(pos1[0] + pos2[0]) / 2,
                    (pos1[1] + pos2[1]) / 2,
                    (pos1[2] + pos2[2]) / 2]
        
        # Helper function to copy a position
        def cpPos(pos):
            return [pos[0], pos[1], pos[2]]
        
        temp_I3_H3 = (points['I3'][0][0] - points['H3'][0][0]) / 2
        temp_1U = avgPos(points['I3'][0], points['F3'][0])
        temp_2U = cpPos(temp_1U)
        temp_2U[1] += (points['F2'][0][2] - points['F3'][0][2]) * -1
        temp_2B = cpPos(temp_2U)
        temp_2B[2] *= -1
        temp_3UR = cpPos(points['H3'][0])
        temp_3UR[0] += temp_I3_H3
        temp_3UR[2] += temp_I3_H3
        temp_3BR = cpPos(points['H5'][0])
        temp_3BR[0] += temp_I3_H3
        temp_3BR[2] -= temp_I3_H3
        temp_3UL = cpPos(points['G3'][0])
        temp_3UL[0] -= temp_I3_H3
        temp_3UL[2] += temp_I3_H3
        temp_3BL = cpPos(points['G5'][0])
        temp_3BL[0] -= temp_I3_H3
        temp_3BL[2] -= temp_I3_H3
        temp_4UR = cpPos(temp_3UR)
        temp_4UR[1] = temp_2U[1]
        temp_4BR = cpPos(temp_3BR)
        temp_4BR[1] = temp_2U[1]
        temp_4UL = cpPos(temp_3UL)
        temp_4UL[1] = temp_2U[1]
        temp_4BL = cpPos(temp_3BL)
        temp_4BL[1] = temp_2U[1]
        temp_5R = cpPos(points['H4'][0])
        temp_5R[1] = temp_2U[1]
        temp_5L = cpPos(points['G4'][0])
        temp_5L[1] = temp_2U[1]
        wrap_pivots = {'1U': temp_1U, '1B': avgPos(points['I5'][0], points['F5'][0]),
                       '2U': temp_2U, '2B': temp_2B,
                       '3UR': temp_3UR, '3BR': temp_3BR, '3UL': temp_3UL, '3BL': temp_3BL,
                       '4UR': temp_4UR, '4BR': temp_4BR, '4UL': temp_4UL, '4BL': temp_4BL,
                       '5R': temp_5R, '5L': temp_5L,
                       '6R': cpPos(points['H4'][0]), '6L': cpPos(points['G4'][0])}

        return wrap_pivots

    @staticmethod
    def getVertexFromPoint(mesh_name, points, point_index):
        """
        Helper function to get a vertex path from a point
        """
        return mesh_name + ".vtx[%d]" % points[point_index][1]

    @staticmethod
    def getVerticesForRow(mesh_name, points, row_index):
        """
        Helper function to get a list of vertex paths for a row
        """
        row_letters = ['F', 'G', 'H', 'I']
        vertices = []
        
        for letter in row_letters:
            key = letter + row_index
            if key in points:
                vertices.append(mesh_name + ".vtx[%d]" % points[key][1])
    
        return vertices

    @staticmethod
    def createPivotAndCluster(wid, pivot_key, pivot_pos, vertices, rotate_values):
        """
        Helper function to create a pivot locator and cluster
        """
        # Create locator
        pivot = [mc.spaceLocator(position=pivot_pos, name=f"gift_{wid}_pivot_{pivot_key}"), None]
        pivot[1] = mc.listRelatives(pivot[0], shapes=True)[0]
        
        # Create group
        mc.select(pivot[0])
        pivot_group = mc.group(name=f"GRP_gift_{wid}_pivot_{pivot_key}")
        
        # Set rotation
        if len(rotate_values) == 1:
            mc.setAttr(f"{pivot_group}.rotateY", rotate_values[0])
        else:
            mc.setAttr(f"{pivot_group}.rotate", rotate_values[0], rotate_values[1], rotate_values[2], type="double3")
        
        mc.xform(pivot[0], centerPivots=True)
        
        # Create cluster
        mc.select(vertices)
        cluster = mc.cluster(name=f"gift_{wid}_cluster_{pivot_key}")
        mc.parent(cluster[1], pivot[0])
        
        return pivot, pivot_group

    @staticmethod
    def createSimpleCluster(wid, cluster_key, vertices, pivot_pos):
        """
        Helper function to create a simple cluster with just a rotation pivot
        """
        mc.select(vertices)
        cluster = mc.cluster(name=f"gift_{wid}_cluster_{cluster_key}")
        mc.xform(cluster[1], rotatePivot=pivot_pos)
        
        weighted_node = mc.ls(selection=True)[0]
        
        return cluster, weighted_node

    def createClusters(self, points):
        """
        Create clusters used for folding the plane.
        """
        mesh_name = self.f_plane[0]
        
        # Create lists of rows of vertices to select
        vertices_x1 = self.getVerticesForRow(mesh_name, points, '1')
        vertices_x2 = self.getVerticesForRow(mesh_name, points, '2')
        vertices_x6 = self.getVerticesForRow(mesh_name, points, '6')
        vertices_x7 = self.getVerticesForRow(mesh_name, points, '7')
        vertices_x8 = self.getVerticesForRow(mesh_name, points, '8')

        if not self.wrap_overlap:
            vertices_x8 = self.getVerticesForRow(mesh_name, points, '8')

        mc.select(d=True)

        # 1st fold
        # Upper
        vertices_1U = vertices_x1 + vertices_x2
        vertices_1U.append(self.getVertexFromPoint(self.f_plane[0], points, 'F1a'))
        vertices_1U.append(self.getVertexFromPoint(self.f_plane[0], points, 'I1a'))
        if self.wrap_overlap:
            vertices_1U.append(self.getVertexFromPoint(self.f_plane[0], points, 'F1b'))
            vertices_1U.append(self.getVertexFromPoint(self.f_plane[0], points, 'I1b'))
            vertices_1U.append(self.getVertexFromPoint(self.f_plane[0], points, 'F1c'))
            vertices_1U.append(self.getVertexFromPoint(self.f_plane[0], points, 'I1c'))
        
        mc.select(vertices_1U)
        cluster_1U = mc.cluster(name="gift_%s_cluster_1U" % self.wrap_id)
        mc.xform(cluster_1U[1], rotatePivot=self.pivots['1U'])
        self.pivots["1U"] = cluster_1U[1]
        
        # Lower
        vertices_1B = vertices_x6 + vertices_x7
        if not self.wrap_overlap:
            vertices_1B += vertices_x8
        vertices_1B.append(self.getVertexFromPoint(self.f_plane[0], points, 'F7a'))
        vertices_1B.append(self.getVertexFromPoint(self.f_plane[0], points, 'I7a'))
        if self.wrap_overlap:
            vertices_1B.append(self.getVertexFromPoint(self.f_plane[0], points, 'F7b'))
            vertices_1B.append(self.getVertexFromPoint(self.f_plane[0], points, 'I7b'))
        
        mc.select(vertices_1B)
        cluster_1B = mc.cluster(name="gift_%s_cluster_1B" % self.wrap_id)
        mc.xform(cluster_1B[1], rotatePivot=self.pivots['1B'])
        self.pivots["1B"] = cluster_1B[1]

        # 2nd fold
        # Upper
        vertices_2U = vertices_x1
        vertices_2U.append(self.getVertexFromPoint(self.f_plane[0], points, 'F1a'))
        vertices_2U.append(self.getVertexFromPoint(self.f_plane[0], points, 'I1a'))
        if self.wrap_overlap:
            vertices_2U.append(self.getVertexFromPoint(self.f_plane[0], points, 'F1b'))
            vertices_2U.append(self.getVertexFromPoint(self.f_plane[0], points, 'I1b'))
            vertices_2U.append(self.getVertexFromPoint(self.f_plane[0], points, 'F1c'))
            vertices_2U.append(self.getVertexFromPoint(self.f_plane[0], points, 'I1c'))
        
        mc.select(vertices_2U)
        cluster_2U = mc.cluster(name="gift_%s_cluster_2U" % self.wrap_id)
        mc.xform(cluster_2U[1], rotatePivot=self.pivots['2U'])
        self.pivots["2U"] = cluster_2U[1]
        
        # Lower
        vertices_2B = vertices_x7
        if not self.wrap_overlap:
            vertices_2B += vertices_x8
        vertices_2B.append(self.getVertexFromPoint(self.f_plane[0], points, 'F7a'))
        vertices_2B.append(self.getVertexFromPoint(self.f_plane[0], points, 'I7a'))
        if self.wrap_overlap:
            vertices_2B.append(self.getVertexFromPoint(self.f_plane[0], points, 'F7b'))
            vertices_2B.append(self.getVertexFromPoint(self.f_plane[0], points, 'I7b'))
        
        mc.select(vertices_2B)
        cluster_2B = mc.cluster(name="gift_%s_cluster_2B" % self.wrap_id)
        mc.xform(cluster_2B[1], rotatePivot=self.pivots['2B'])
        self.pivots["2B"] = cluster_2B[1]

        # 3rd fold
        # UR
        vertices_3UR = [self.getVertexFromPoint(self.f_plane[0], points, 'I3')]
        if self.wrap_overlap:
            vertices_3UR.append(self.getVertexFromPoint(self.f_plane[0], points, 'I4a'))
            vertices_3UR.append(self.getVertexFromPoint(self.f_plane[0], points, 'I4b'))
        
        self.pivots["3UR"], pivot_3UR_group = self.createPivotAndCluster(self.wrap_id,
            '3UR', self.pivots['3UR'], vertices_3UR, [-45])

        # BR
        vertices_3BR = [self.getVertexFromPoint(self.f_plane[0], points, 'I5')]
        if self.wrap_overlap:
            vertices_3BR.append(self.getVertexFromPoint(self.f_plane[0], points, 'I4a'))
            vertices_3BR.append(self.getVertexFromPoint(self.f_plane[0], points, 'I4b'))
        
        self.pivots["3BR"], pivot_3BR_group = self.createPivotAndCluster(self.wrap_id,
            '3BR', self.pivots['3BR'], vertices_3BR, [180, 225, 0])
        
        # UL
        vertices_3UL = [self.getVertexFromPoint(self.f_plane[0], points, 'F3')]
        if self.wrap_overlap:
            vertices_3UL.append(self.getVertexFromPoint(self.f_plane[0], points, 'F4a'))
            vertices_3UL.append(self.getVertexFromPoint(self.f_plane[0], points, 'F4b'))
        
        self.pivots["3UL"], pivot_3UL_group = self.createPivotAndCluster(self.wrap_id,
            '3UL', self.pivots['3UL'], vertices_3UL, [45])
        
        # BL
        vertices_3BL = [self.getVertexFromPoint(self.f_plane[0], points, 'F5')]
        if self.wrap_overlap:
            vertices_3BL.append(self.getVertexFromPoint(self.f_plane[0], points, 'F4a'))
            vertices_3BL.append(self.getVertexFromPoint(self.f_plane[0], points, 'F4b'))
        
        self.pivots["3BL"], pivot_3BL_group = self.createPivotAndCluster(self.wrap_id,
            '3BL', self.pivots['3BL'], vertices_3BL, [0, 45, 180])

        # 4th fold
        # UR
        vertices_4UR = [self.getVertexFromPoint(self.f_plane[0], points, 'I2')]
        if self.wrap_overlap:
            vertices_4UR.append(self.getVertexFromPoint(self.f_plane[0], points, 'I1b'))
            vertices_4UR.append(self.getVertexFromPoint(self.f_plane[0], points, 'I7'))
        
        self.pivots["4UR"], pivot_4UR_group = self.createPivotAndCluster(self.wrap_id,
            '4UR', self.pivots['4UR'], vertices_4UR, [135])

        # BR
        vertices_4BR = [self.getVertexFromPoint(self.f_plane[0], points, 'I6')]
        if self.wrap_overlap:
            vertices_4BR.append(self.getVertexFromPoint(self.f_plane[0], points, 'I7a'))
            vertices_4BR.append(self.getVertexFromPoint(self.f_plane[0], points, 'I1'))
            vertices_4BR.append(self.getVertexFromPoint(self.f_plane[0], points, 'I7'))
        
        self.pivots["4BR"], pivot_4BR_group = self.createPivotAndCluster(self.wrap_id,
            '4BR', self.pivots['4BR'], vertices_4BR, [45])
        
        # UL
        vertices_4UL = [self.getVertexFromPoint(self.f_plane[0], points, 'F2')]
        if self.wrap_overlap:
            vertices_4UL.append(self.getVertexFromPoint(self.f_plane[0], points, 'F1b'))
            vertices_4UL.append(self.getVertexFromPoint(self.f_plane[0], points, 'F7'))
        
        self.pivots["4UL"], pivot_4UL_group = self.createPivotAndCluster(self.wrap_id,
            '4UL', self.pivots['4UL'], vertices_4UL, [225])
        
        # BL
        vertices_4BL = [self.getVertexFromPoint(self.f_plane[0], points, 'F6')]
        if self.wrap_overlap:
            vertices_4BL.append(self.getVertexFromPoint(self.f_plane[0], points, 'F7a'))
            vertices_4BL.append(self.getVertexFromPoint(self.f_plane[0], points, 'F1'))
            vertices_4BL.append(self.getVertexFromPoint(self.f_plane[0], points, 'F7'))
        
        self.pivots["4BL"], pivot_4BL_group = self.createPivotAndCluster(self.wrap_id,
            '4BL', self.pivots['4BL'], vertices_4BL, [180, 225, 180])

        # 6th fold
        # Right
        vertices_6R = [
            self.getVertexFromPoint(self.f_plane[0], points, 'I4a'),
            self.getVertexFromPoint(self.f_plane[0], points, 'I4b')
        ]
        if self.wrap_overlap:
            vertices_6R.append(self.getVertexFromPoint(self.f_plane[0], points, 'HI4'))
        
        cluster_6R, self.pivots["6R"] = self.createSimpleCluster(self.wrap_id, '6R', vertices_6R, self.pivots['6R'])
        
        # Left
        vertices_6L = [
            self.getVertexFromPoint(self.f_plane[0], points, 'F4a'),
            self.getVertexFromPoint(self.f_plane[0], points, 'F4b')
        ]
        if self.wrap_overlap:
            vertices_6L.append(self.getVertexFromPoint(self.f_plane[0], points, 'FG4'))
        
        cluster_6L, self.pivots["6L"] = self.createSimpleCluster(self.wrap_id, '6L', vertices_6L, self.pivots['6L'])
        
        # 5th fold
        # Right
        vertices_5R = [
            self.getVertexFromPoint(self.f_plane[0], points, 'I7'),
            self.getVertexFromPoint(self.f_plane[0], points, 'I1'),
            self.getVertexFromPoint(self.f_plane[0], points, 'I1a'),
            self.getVertexFromPoint(self.f_plane[0], points, 'I7a')
        ]
        if not self.wrap_overlap:
            vertices_5R.append(self.getVertexFromPoint(self.f_plane[0], points, 'I8'))
        else:
            vertices_5R.append(self.getVertexFromPoint(self.f_plane[0], points, 'I7b'))
            vertices_5R.append(self.getVertexFromPoint(self.f_plane[0], points, 'I1b'))
            vertices_5R.append(self.getVertexFromPoint(self.f_plane[0], points, 'I1c'))
        
        cluster_5R, self.pivots["5R"] = self.createSimpleCluster(self.wrap_id, '5R', vertices_5R, self.pivots['5R'])
        
        # Left
        vertices_5L = [
            self.getVertexFromPoint(self.f_plane[0], points, 'F7'),
            self.getVertexFromPoint(self.f_plane[0], points, 'F1'),
            self.getVertexFromPoint(self.f_plane[0], points, 'F1a'),
            self.getVertexFromPoint(self.f_plane[0], points, 'F7a')
        ]
        if not self.wrap_overlap:
            vertices_5L.append(self.getVertexFromPoint(self.f_plane[0], points, 'F8'))
        else:
            vertices_5L.append(self.getVertexFromPoint(self.f_plane[0], points, 'F7b'))
            vertices_5L.append(self.getVertexFromPoint(self.f_plane[0], points, 'F1b'))
            vertices_5L.append(self.getVertexFromPoint(self.f_plane[0], points, 'F1c'))
        
        cluster_5L, self.pivots["5L"] = self.createSimpleCluster(self.wrap_id, '5L', vertices_5L, self.pivots['5L'])

        # Parent to main cluster group
        mc.parent(cluster_1U[1], self.cluster_group_name)
        mc.parent(cluster_1B[1], self.cluster_group_name)
        mc.parent(cluster_2U[1], self.cluster_group_name)
        mc.parent(cluster_2B[1], self.cluster_group_name)
        mc.parent(pivot_3UR_group, self.cluster_group_name)
        mc.parent(pivot_3UL_group, self.cluster_group_name)
        mc.parent(pivot_3BR_group, self.cluster_group_name)
        mc.parent(pivot_3BL_group, self.cluster_group_name)
        mc.parent(pivot_4UR_group, self.cluster_group_name)
        mc.parent(pivot_4UL_group, self.cluster_group_name)
        mc.parent(pivot_4BR_group, self.cluster_group_name)
        mc.parent(pivot_4BL_group, self.cluster_group_name)
        mc.parent(cluster_5R[1], self.cluster_group_name)
        mc.parent(cluster_5L[1], self.cluster_group_name)
        mc.parent(cluster_6R[1], self.cluster_group_name)
        mc.parent(cluster_6L[1], self.cluster_group_name)

    @staticmethod
    def idGenerator(size=4, chars=string.ascii_uppercase + string.digits):
        """ID gen - Courtesy of a random google search"""
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def get_weighted_node(cluster_node):
        """Gets transform node weighted by the given cluster (pymel getWeightedNode)"""
        deformer_set = mc.listConnections(cluster_node, type="objectSet")
        return deformer_set[0].split(".")[0]

    def foldPaper(self, folds=17):
        """
        Wraps / unwraps gift by rotating clusters.
        folds = number of folds to perform
        """
        if folds >= 1:
            mc.setAttr(self.pivots["1B"] + ".rotateX", -90)
        if folds >= 2:
            mc.setAttr(self.pivots["2B"] + ".rotateX", -90)
        if folds >= 3:
            mc.setAttr(self.pivots["1U"] + ".rotateX", 90)
        if folds >= 4:
            mc.setAttr(self.pivots["2U"] + ".rotateX", 89.8)
        if folds >= 5:
            mc.setAttr(self.pivots["3UL"][0][0] + ".rotateX", 178)
            mc.setAttr(self.pivots["3UL"][0][0] + ".translateX", self.fold_fix)
            mc.setAttr(self.pivots["3UL"][0][0] + ".translateY", 0)
            mc.setAttr(self.pivots["3UL"][0][0] + ".translateZ", 0)
        if folds >= 6:
            mc.setAttr(self.pivots["3BL"][0][0] + ".rotateX", 178)
            mc.setAttr(self.pivots["3BL"][0][0] + ".translateX", self.fold_fix * -1)
            mc.setAttr(self.pivots["3BL"][0][0] + ".translateY", 0)
            mc.setAttr(self.pivots["3BL"][0][0] + ".translateZ", 0)
        if folds >= 7:
            mc.setAttr(self.pivots["3UR"][0][0] + ".rotateX", 178)
            mc.setAttr(self.pivots["3UR"][0][0] + ".translateX", self.fold_fix * -1)
            mc.setAttr(self.pivots["3UR"][0][0] + ".translateY", 0)
            mc.setAttr(self.pivots["3UR"][0][0] + ".translateZ", 0)
        if folds >= 8:
            mc.setAttr(self.pivots["3BR"][0][0] + ".rotateX", 178)
            mc.setAttr(self.pivots["3BR"][0][0] + ".translateX", self.fold_fix)
            mc.setAttr(self.pivots["3BR"][0][0] + ".translateY", 0)
            mc.setAttr(self.pivots["3BR"][0][0] + ".translateZ", 0)
        if folds >= 9:
            mc.setAttr(self.pivots["4UL"][0][0] + ".rotateX", 178)
        if folds >= 10:
            mc.setAttr(self.pivots["4BL"][0][0] + ".rotateX", 178)
        if folds >= 11:
            mc.setAttr(self.pivots["4UR"][0][0] + ".rotateX", 178)
        if folds >= 12:
            mc.setAttr(self.pivots["4BR"][0][0] + ".rotateX", 178)
        if folds >= 13:
                                    mc.setAttr(self.pivots["5L"] + ".rotateZ", 86)
        if folds >= 14:
            mc.setAttr(self.pivots["5R"] + ".rotateZ", -86)
        if folds >= 15:
            mc.setAttr(self.pivots["6L"] + ".rotateZ", -84)
        if folds >= 16:
            mc.setAttr(self.pivots["6R"] + ".rotateZ", 84)
        if folds == 0:
            mc.setAttr(self.pivots["1B"] + ".rotateX", 0)
            mc.setAttr(self.pivots["1B"] + ".rotateY", 0)
            mc.setAttr(self.pivots["1B"] + ".rotateZ", 0)
        if folds < 2:
            mc.setAttr(self.pivots["2B"] + ".rotateX", 0)
            mc.setAttr(self.pivots["2B"] + ".rotateY", 0)
            mc.setAttr(self.pivots["2B"] + ".rotateZ", 0)
        if folds < 3:
            mc.setAttr(self.pivots["1U"] + ".rotateX", 0)
            mc.setAttr(self.pivots["1U"] + ".rotateY", 0)
            mc.setAttr(self.pivots["1U"] + ".rotateZ", 0)
        if folds < 4:
            mc.setAttr(self.pivots["2U"] + ".rotateX", 0)
            mc.setAttr(self.pivots["2U"] + ".rotateY", 0)
            mc.setAttr(self.pivots["2U"] + ".rotateZ", 0)
        if folds < 5:
            mc.setAttr(self.pivots["3UL"][0][0] + ".rotateX", 0)
            mc.setAttr(self.pivots["3UL"][0][0] + ".rotateY", 0)
            mc.setAttr(self.pivots["3UL"][0][0] + ".rotateZ", 0)
            mc.setAttr(self.pivots["3UL"][0][0] + ".translateX", 0)
            mc.setAttr(self.pivots["3UL"][0][0] + ".translateY", 0)
            mc.setAttr(self.pivots["3UL"][0][0] + ".translateZ", 0)
        if folds < 6:
            mc.setAttr(self.pivots["3BL"][0][0] + ".rotateX", 0)
            mc.setAttr(self.pivots["3BL"][0][0] + ".rotateY", 0)
            mc.setAttr(self.pivots["3BL"][0][0] + ".rotateZ", 0)
            mc.setAttr(self.pivots["3BL"][0][0] + ".translateX", 0)
            mc.setAttr(self.pivots["3BL"][0][0] + ".translateY", 0)
            mc.setAttr(self.pivots["3BL"][0][0] + ".translateZ", 0)
        if folds < 7:
            mc.setAttr(self.pivots["3UR"][0][0] + ".rotateX", 0)
            mc.setAttr(self.pivots["3UR"][0][0] + ".rotateY", 0)
            mc.setAttr(self.pivots["3UR"][0][0] + ".rotateZ", 0)
            mc.setAttr(self.pivots["3UR"][0][0] + ".translateX", 0)
            mc.setAttr(self.pivots["3UR"][0][0] + ".translateY", 0)
            mc.setAttr(self.pivots["3UR"][0][0] + ".translateZ", 0)
        if folds < 8:
            mc.setAttr(self.pivots["3BR"][0][0] + ".rotateX", 0)
            mc.setAttr(self.pivots["3BR"][0][0] + ".rotateY", 0)
            mc.setAttr(self.pivots["3BR"][0][0] + ".rotateZ", 0)
            mc.setAttr(self.pivots["3BR"][0][0] + ".translateX", 0)
            mc.setAttr(self.pivots["3BR"][0][0] + ".translateY", 0)
            mc.setAttr(self.pivots["3BR"][0][0] + ".translateZ", 0)
        if folds < 9:
            mc.setAttr(self.pivots["4UL"][0][0] + ".rotateX", 0)
            mc.setAttr(self.pivots["4UL"][0][0] + ".rotateY", 0)
            mc.setAttr(self.pivots["4UL"][0][0] + ".rotateZ", 0)
        if folds < 10:
            mc.setAttr(self.pivots["4BL"][0][0] + ".rotateX", 0)
            mc.setAttr(self.pivots["4BL"][0][0] + ".rotateY", 0)
            mc.setAttr(self.pivots["4BL"][0][0] + ".rotateZ", 0)
        if folds < 11:
            mc.setAttr(self.pivots["4UR"][0][0] + ".rotateX", 0)
            mc.setAttr(self.pivots["4UR"][0][0] + ".rotateY", 0)
            mc.setAttr(self.pivots["4UR"][0][0] + ".rotateZ", 0)
        if folds < 12:
            mc.setAttr(self.pivots["4BR"][0][0] + ".rotateX", 0)
            mc.setAttr(self.pivots["4BR"][0][0] + ".rotateY", 0)
            mc.setAttr(self.pivots["4BR"][0][0] + ".rotateZ", 0)
        if folds < 13:
            mc.setAttr(self.pivots["5L"] + ".rotateX", 0)
            mc.setAttr(self.pivots["5L"] + ".rotateY", 0)
            mc.setAttr(self.pivots["5L"] + ".rotateZ", 0)
        if folds < 14:
            mc.setAttr(self.pivots["5R"] + ".rotateX", 0)
            mc.setAttr(self.pivots["5R"] + ".rotateY", 0)
            mc.setAttr(self.pivots["5R"] + ".rotateZ", 0)
        if folds < 15:
            mc.setAttr(self.pivots["6L"] + ".rotateX", 0)
            mc.setAttr(self.pivots["6L"] + ".rotateY", 0)
            mc.setAttr(self.pivots["6L"] + ".rotateZ", 0)
        if folds < 16:
            mc.setAttr(self.pivots["6R"] + ".rotateX", 0)
            mc.setAttr(self.pivots["6R"] + ".rotateY", 0)
            mc.setAttr(self.pivots["6R"] + ".rotateZ", 0)

    def setDrivenKeys(self, anim=0):
        """
        Connect the wrapping to the animation attribute of the control handle.
        """
        self.foldPaper(0)
        mc.setAttr(self.ctrl_handle[0] + ".animation", 0)
        mc.setDrivenKeyframe(self.pivots["1B"] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 1)
        self.foldPaper(1)
        mc.setDrivenKeyframe(self.pivots["1B"] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["2B"] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 2)
        self.foldPaper(2)
        mc.setDrivenKeyframe(self.pivots["2B"] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["1U"] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 3)
        self.foldPaper(3)
        mc.setDrivenKeyframe(self.pivots["1U"] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["2U"] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 4)
        self.foldPaper(4)
        mc.setDrivenKeyframe(self.pivots["2U"] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["3UL"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["3UL"][0][0] + ".translateX", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 4.5)
        self.foldPaper(5)
        mc.setDrivenKeyframe(self.pivots["3UL"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["3UL"][0][0] + ".translateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["3BL"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["3BL"][0][0] + ".translateX", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 5)
        self.foldPaper(6)
        mc.setDrivenKeyframe(self.pivots["3BL"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["3BL"][0][0] + ".translateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["3UR"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["3UR"][0][0] + ".translateX", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 5.5)
        self.foldPaper(7)
        mc.setDrivenKeyframe(self.pivots["3UR"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["3UR"][0][0] + ".translateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["3BR"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["3BR"][0][0] + ".translateX", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 6)
        self.foldPaper(8)
        mc.setDrivenKeyframe(self.pivots["3BR"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["3BR"][0][0] + ".translateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["4UL"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 6.5)
        self.foldPaper(9)
        mc.setDrivenKeyframe(self.pivots["4UL"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["4BL"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 7)
        self.foldPaper(10)
        mc.setDrivenKeyframe(self.pivots["4BL"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["4UR"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 7.5)
        self.foldPaper(11)
        mc.setDrivenKeyframe(self.pivots["4UR"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["4BR"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 8)
        self.foldPaper(12)
        mc.setDrivenKeyframe(self.pivots["4BR"][0][0] + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["5L"] + ".rotateZ", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 8.5)
        self.foldPaper(13)
        mc.setDrivenKeyframe(self.pivots["5L"] + ".rotateZ", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["5R"] + ".rotateZ", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 9)
        self.foldPaper(14)
        mc.setDrivenKeyframe(self.pivots["5R"] + ".rotateZ", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["6L"] + ".rotateZ", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 9.5)
        self.foldPaper(15)
        mc.setDrivenKeyframe(self.pivots["6L"] + ".rotateZ", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.pivots["6R"] + ".rotateZ", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 10)
        self.foldPaper(16)
    
        # Bbox
        bbox = mc.exactWorldBoundingBox(self.wrap_gift)
        bbox_min = [bbox[0], bbox[1], bbox[2]]
        bbox_max = [bbox[3], bbox[4], bbox[5]]
        bbox_minmax = [bbox_max[0] - bbox_min[0], bbox_max[1] - bbox_min[1], bbox_max[2] - bbox_min[2]]
    
        mc.setAttr(self.gift_group_name + ".translateY", 0)
        mc.setAttr(self.gift_group_name + ".rotateX", 0)
        mc.xform(self.gift_group_name, centerPivots=True)
    
        mc.setDrivenKeyframe(self.pivots["6R"] + ".rotateZ", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.gift_group_name + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.gift_group_name + ".translateY", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 10.5)
        mc.setAttr(self.gift_group_name + ".translateY", bbox_minmax[1]/2)
        mc.setDrivenKeyframe(self.gift_group_name + ".translateY", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 11)
        mc.setAttr(self.gift_group_name + ".rotateX", 180)
        mc.setAttr(self.gift_group_name + ".translateY", 0)
        self.tieRibbon(0)
        mc.setDrivenKeyframe(self.gift_group_name + ".rotateX", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.gift_group_name + ".translateY", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.ribbons['1U'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.ribbons['1D'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 12)
        self.tieRibbon(1)
        mc.setDrivenKeyframe(self.ribbons['1U'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.ribbons['1D'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.ribbons['2L'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.ribbons['2R'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 13)
        self.tieRibbon(2)
        mc.setDrivenKeyframe(self.ribbons['2L'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.ribbons['2R'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.ribbons['3L'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.ribbons['3R'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 14)
        self.tieRibbon(3)
        mc.setDrivenKeyframe(self.ribbons['3L'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.ribbons['3R'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.ribbons['4'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", 15)
        self.tieRibbon(4)
        mc.setDrivenKeyframe(self.ribbons['3L'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.ribbons['3R'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
        mc.setDrivenKeyframe(self.ribbons['4'][2] + ".maxValue", currentDriver=self.ctrl_handle[0] + ".animation")
    
        mc.setAttr(self.ctrl_handle[0] + ".animation", anim)

    def setAnimation(self, anim_s=None, anim_e=None):
        if anim_s is None:
            anim_s = self.animation_start
        else:
            self.animation_start = anim_s
            mc.setAttr(self.ctrl_handle[0] + ".animation_start", self.animation_start)
        
        if anim_e is None:
            anim_e = self.animation_end
        else:
            self.animation_end = anim_e
            mc.setAttr(self.ctrl_handle[0] + ".animation_end", self.animation_end)
        
        # Remove existing animation keys
        mc.cutKey(self.ctrl_handle[0], attribute="animation", clear=True)
        
        # Set new animation keys if start and end are different
        if not anim_s == anim_e:
            mc.setKeyframe(self.ctrl_handle[0], attribute="animation", value=0, time=anim_s)
            mc.setKeyframe(self.ctrl_handle[0], attribute="animation", value=15, time=anim_e)

    def createPaper(self, plane, thickness):
        """
        Creates a wrapping paper mesh which is then controlled by the
        folding plane using a wrap deformer.
        """
        paper = mc.duplicate(plane, name="wrap_paper_%s" % self.wrap_id)

        # Make hipoly
        mc.polyBevel(paper, offset=0.005, constructionHistory=0)
        mc.polySubdivideFacet(paper, divisions=1, divisionsV=1, subdMethod=0, constructionHistory=0)

        # Move pivot and translate
        mc.move(0, thickness/2, 0, paper[0] + ".rotatePivot", relative=True)
        mc.setAttr(paper[0] + ".translateY", -0.5 * thickness)
        
        # Extrude
        mc.polyExtrudeFacet(paper, translateY=(thickness * 1), constructionHistory=0)
        
        # UV mapping
        verts = mc.polyEvaluate(paper[0], face=True) - 1
        evalthis = 'polyProjection -ch 0 -type Planar -ibd on -kir -md y ' + str(paper[0]) + '.f[0:' + str(verts) +']'
        mel.eval(evalthis)  # UV planar map

        # Create wrap deformer
        mc.select(clear=True)
        mc.select(paper, plane)
        mc.CreateWrap()
        
        return paper

    @staticmethod
    def getRibbonPoints(side_w, side_h, side_d, side_a, thickness, r_thickness, r_width):
        """
        Calculate the coordinates of the nurbs curve controlling the
        extrusion of the ribbon.
                              (U)pside
                         ____/__
                        /|  /  /|
                       / |    / |
                      /__|__-/-------(B)ack side
        (L)eft side--|-- |___|__|
                     |  /    | \/
        (F)ront side-|-/-- / | /\
                     |/___/__|/  \ (R)ight side
                         /
                        (D)ownside
        """

        def cpV(vec):
            return [vec[0], vec[1], vec[2]]

        y_pos = side_h + (r_thickness / 3)
        x_pos = (side_w / 2) + (r_thickness + thickness)
        z_pos = (side_d / 2) + (r_thickness / 3)
        edg_m = thickness / 2  # edge margin
        mid_c = 0.5  # mid point coefficient
        end_m = 2 * thickness  # end point margin
        x_pos_m = thickness  # width (L and R) margin
        x_edge = (side_a / 2)  # + thickness + (r_thickness / 2)
    
        # Mid-points
        r_points = {'U': [[0, y_pos, 0], 0]}
        r_points['D'] = [[0, 0, 0], 0]
        r_points['L'] = [[0 - x_pos, side_h / 2, 0], 0]
        r_points['R'] = [[x_pos, side_h / 2, 0], 0]
        r_points['F'] = [[0, side_h / 2, z_pos], 0]
        r_points['B'] = [[0, side_h / 2, 0 - z_pos], 0]
    
        # Upper side
        r_points['UL'] = [cpV(r_points['U'][0]), 0]  
        r_points['UL'][0][0] = 0 - x_edge  
        r_points['ULmid'] = [cpV(r_points['UL'][0]), 0]
        r_points['ULmid'][0][0] *= mid_c  
        r_points['ULend'] = [cpV(r_points['UL'][0]), 0]
        r_points['ULend'][0][0] += end_m * 2  
    
        r_points['UR'] = [cpV(r_points['U'][0]), 0]
        r_points['UR'][0][0] = x_edge  
        r_points['URmid'] = [cpV(r_points['UR'][0]), 0]
        r_points['URmid'][0][0] *= mid_c  
        r_points['URend'] = [cpV(r_points['UR'][0]), 0]
        r_points['URend'][0][0] -= end_m * 2  
    
        r_points['UB'] = [cpV(r_points['U'][0]), 0]
        r_points['UB'][0][2] = r_points['B'][0][2] + edg_m  
        r_points['UBmid'] = [cpV(r_points['UB'][0]), 0]
        r_points['UBmid'][0][2] *= mid_c  
        r_points['UBend'] = [cpV(r_points['UB'][0]), 0]
        r_points['UBend'][0][2] += end_m  
    
        r_points['UF'] = [cpV(r_points['U'][0]), 0]
        r_points['UF'][0][2] = r_points['F'][0][2] - edg_m  
        r_points['UFmid'] = [cpV(r_points['UF'][0]), 0]
        r_points['UFmid'][0][2] *= mid_c  
        r_points['UFend'] = [cpV(r_points['UF'][0]), 0]
        r_points['UFend'][0][2] -= end_m  
    
        # Downside
        r_points['DL'] = [cpV(r_points['D'][0]), 0]
        r_points['DL'][0][0] = 0 - x_edge  
        r_points['DLmid'] = [cpV(r_points['DL'][0]), 0]
        r_points['DLmid'][0][0] *= mid_c  
        r_points['DLend'] = [cpV(r_points['DL'][0]), 0]
        r_points['DLend'][0][0] += end_m * 2  
    
        r_points['DR'] = [cpV(r_points['D'][0]), 0]
        r_points['DR'][0][0] = x_edge  
        r_points['DRmid'] = [cpV(r_points['DR'][0]), 0]
        r_points['DRmid'][0][0] *= mid_c  
        r_points['DRend'] = [cpV(r_points['DR'][0]), 0]
        r_points['DRend'][0][0] -= end_m * 2  

        r_points['DB'] = [cpV(r_points['D'][0]), 0]
        r_points['DB'][0][2] = r_points['B'][0][2] + edg_m  
        r_points['DBmid'] = [cpV(r_points['DB'][0]), 0]
        r_points['DBmid'][0][2] *= mid_c  
        r_points['DBend'] = [cpV(r_points['DB'][0]), 0]
        r_points['DBend'][0][2] += end_m  
        
        r_points['DF'] = [cpV(r_points['D'][0]), 0]
        r_points['DF'][0][2] = r_points['F'][0][2] - edg_m  
        r_points['DFmid'] = [cpV(r_points['DF'][0]), 0]
        r_points['DFmid'][0][2] *= mid_c  
        r_points['DFend'] = [cpV(r_points['DF'][0]), 0]
        r_points['DFend'][0][2] -= end_m  
        
        # Left side
        r_points['LU'] = [cpV(r_points['L'][0]), 0]
        r_points['LU'][0][1] = r_points['U'][0][1] - edg_m  
        r_points['LU'][0][0] = 0 - (x_edge + x_pos_m)  
        r_points['LUmid'] = [cpV(r_points['L'][0]), 0]
        r_points['LUmid'][0][1] += y_pos / 4  
        r_points['LUmid'][0][0] += (r_points['LU'][0][0] - r_points['L'][0][0]) / 2  
        r_points['LUend'] = [cpV(r_points['LU'][0]), 0]
        r_points['LUend'][0][1] -= end_m  
        r_points['LUend'][0][0] -= x_pos_m  
        
        r_points['LD'] = [cpV(r_points['L'][0]), 0]
        r_points['LD'][0][1] = r_points['D'][0][1] + edg_m  
        r_points['LD'][0][0] = 0 - (x_edge + x_pos_m)  
        r_points['LDmid'] = [cpV(r_points['L'][0]), 0]
        r_points['LDmid'][0][1] -= y_pos / 3  
        r_points['LDend'] = [cpV(r_points['LD'][0]), 0]
        r_points['LDend'][0][1] += end_m  
        r_points['LDend'][0][0] -= x_pos_m  
        
        r_points['LB'] = [cpV(r_points['L'][0]), 0]
        r_points['LB'][0][2] = r_points['B'][0][2] + edg_m  
        r_points['LBmid'] = [cpV(r_points['LB'][0]), 0]
        r_points['LBmid'][0][2] *= mid_c  
        r_points['LBend'] = [cpV(r_points['LB'][0]), 0]
        r_points['LBend'][0][2] += end_m  
        
        r_points['LF'] = [cpV(r_points['L'][0]), 0]
        r_points['LF'][0][2] = r_points['F'][0][2] - edg_m  
        r_points['LFmid'] = [cpV(r_points['LF'][0]), 0]
        r_points['LFmid'][0][2] *= mid_c  
        r_points['LFend'] = [cpV(r_points['LF'][0]), 0]
        r_points['LFend'][0][2] -= end_m  

        # Right side
        r_points['RU'] = [cpV(r_points['R'][0]), 0]
        r_points['RU'][0][1] = r_points['U'][0][1] - edg_m  
        r_points['RU'][0][0] = x_edge + x_pos_m  
        r_points['RUmid'] = [cpV(r_points['R'][0]), 0]
        r_points['RUmid'][0][1] += y_pos / 4  
        r_points['RUmid'][0][0] -= (r_points['R'][0][0] - r_points['RU'][0][0]) / 2  
        r_points['RUend'] = [cpV(r_points['RU'][0]), 0]
        r_points['RUend'][0][1] -= end_m  
        r_points['RUend'][0][0] += x_pos_m  
        
        r_points['RD'] = [cpV(r_points['R'][0]), 0]
        r_points['RD'][0][1] = r_points['D'][0][1] + edg_m  
        r_points['RD'][0][0] = x_edge + x_pos_m  
        r_points['RDmid'] = [cpV(r_points['R'][0]), 0]
        r_points['RDmid'][0][1] -= y_pos / 3  
        r_points['RDend'] = [cpV(r_points['RD'][0]), 0]
        r_points['RDend'][0][1] += end_m  
        r_points['RDend'][0][0] += x_pos_m  
        
        r_points['RB'] = [cpV(r_points['R'][0]), 0]
        r_points['RB'][0][2] = r_points['B'][0][2] + edg_m  
        r_points['RBmid'] = [cpV(r_points['RB'][0]), 0]
        r_points['RBmid'][0][2] *= mid_c  
        r_points['RBend'] = [cpV(r_points['RB'][0]), 0]
        r_points['RBend'][0][2] += end_m  
        
        r_points['RF'] = [cpV(r_points['R'][0]), 0]
        r_points['RF'][0][2] = r_points['F'][0][2] - edg_m  
        r_points['RFmid'] = [cpV(r_points['RF'][0]), 0]
        r_points['RFmid'][0][2] *= mid_c  
        r_points['RFend'] = [cpV(r_points['RF'][0]), 0]
        r_points['RFend'][0][2] -= end_m  
        
        # Back side
        r_points['BU'] = [cpV(r_points['B'][0]), 0]
        r_points['BU'][0][1] = r_points['U'][0][1] - edg_m  
        r_points['BUmid'] = [cpV(r_points['BU'][0]), 0]
        r_points['BUmid'][0][1] -= y_pos / 4  
        r_points['BUend'] = [cpV(r_points['BU'][0]), 0]
        r_points['BUend'][0][1] -= end_m  
        
        r_points['BD'] = [cpV(r_points['B'][0]), 0]
        r_points['BD'][0][1] = r_points['D'][0][1] + edg_m  
        r_points['BDmid'] = [cpV(r_points['BD'][0]), 0]
        r_points['BDmid'][0][1] += y_pos / 4  
        r_points['BDend'] = [cpV(r_points['BD'][0]), 0]
        r_points['BDend'][0][1] += end_m  
        
        r_points['BL'] = [cpV(r_points['B'][0]), 0]
        r_points['BL'][0][0] = r_points['L'][0][0] + edg_m  
        r_points['BLmid'] = [cpV(r_points['BL'][0]), 0]
        r_points['BLmid'][0][0] *= mid_c  
        r_points['BLend'] = [cpV(r_points['BL'][0]), 0]
        r_points['BLend'][0][0] += end_m  
        
        r_points['BR'] = [cpV(r_points['B'][0]), 0]
        r_points['BR'][0][0] = r_points['R'][0][0] - edg_m  
        r_points['BRmid'] = [cpV(r_points['BR'][0]), 0]
        r_points['BRmid'][0][0] *= mid_c  
        r_points['BRend'] = [cpV(r_points['BR'][0]), 0]
        r_points['BRend'][0][0] -= end_m  

        # Front side
        r_points['FU'] = [cpV(r_points['F'][0]), 0]
        r_points['FU'][0][1] = r_points['U'][0][1] - edg_m  
        r_points['FUmid'] = [cpV(r_points['FU'][0]), 0]
        r_points['FUmid'][0][1] -= y_pos / 4  
        r_points['FUend'] = [cpV(r_points['FU'][0]), 0]
        r_points['FUend'][0][1] -= end_m  
        
        r_points['FD'] = [cpV(r_points['F'][0]), 0]
        r_points['FD'][0][1] = r_points['D'][0][1] + edg_m  
        r_points['FDmid'] = [cpV(r_points['FD'][0]), 0]
        r_points['FDmid'][0][1] += y_pos / 4  
        r_points['FDend'] = [cpV(r_points['FD'][0]), 0]
        r_points['FDend'][0][1] += end_m  
        
        r_points['FL'] = [cpV(r_points['F'][0]), 0]
        r_points['FL'][0][0] = r_points['L'][0][0] + edg_m  
        r_points['FLmid'] = [cpV(r_points['FL'][0]), 0]
        r_points['FLmid'][0][0] *= mid_c  
        r_points['FLend'] = [cpV(r_points['FL'][0]), 0]
        r_points['FLend'][0][0] += end_m  
        
        r_points['FR'] = [cpV(r_points['F'][0]), 0]
        r_points['FR'][0][0] = r_points['R'][0][0] - edg_m  
        r_points['FRmid'] = [cpV(r_points['FR'][0]), 0]
        r_points['FRmid'][0][0] *= mid_c  
        r_points['FRend'] = [cpV(r_points['FR'][0]), 0]
        r_points['FRend'][0][0] -= end_m  
        
        # Bow
        loop_w = side_w / 3
        loop_h = side_w / 4
        
        # Left loop
        r_points['bow_L1'] = [cpV(r_points['U'][0]), 0]
        r_points['bow_L2'] = [cpV(r_points['U'][0]), 0]
        r_points['bow_L2'][0][0] = 0 - loop_w  
        r_points['bow_L2'][0][1] += r_thickness  
        r_points['bow_L3'] = [cpV(r_points['bow_L2'][0]), 0]
        r_points['bow_L3'][0][1] += loop_h / 2  
        r_points['bow_L3'][0][0] -= r_width / 2  
        r_points['bow_L4'] = [cpV(r_points['bow_L2'][0]), 0]
        r_points['bow_L4'][0][1] += loop_h  
        r_points['bow_L4'][0][0] += r_width * 0.25  
        r_points['bow_L5'] = [cpV(r_points['bow_L1'][0]), 0]
        r_points['bow_L5'][0][1] += r_thickness  
        r_points['bow_L5'][0][0] -= r_width * 0.85  
        r_points['bow_L6'] = [cpV(r_points['bow_L5'][0]), 0]
        r_points['bow_L6'][0][0] += r_width / 2  
        r_points['bow_L7'] = [cpV(r_points['bow_L1'][0]), 0]
        r_points['bow_L7'][0][1] += r_thickness * 0.5  
        
        # Right loop
        r_points['bow_R1'] = [cpV(r_points['U'][0]), 0]
        r_points['bow_R2'] = [cpV(r_points['U'][0]), 0]
        r_points['bow_R2'][0][0] = loop_w  
        r_points['bow_R2'][0][1] += r_thickness  
        r_points['bow_R3'] = [cpV(r_points['bow_R2'][0]), 0]
        r_points['bow_R3'][0][1] += loop_h / 2  
        r_points['bow_R3'][0][0] += r_width / 2  
        r_points['bow_R4'] = [cpV(r_points['bow_R2'][0]), 0]
        r_points['bow_R4'][0][1] += loop_h  
        r_points['bow_R4'][0][0] -= r_width * 0.25  
        r_points['bow_R5'] = [cpV(r_points['bow_R1'][0]), 0]
        r_points['bow_R5'][0][1] += r_thickness  
        r_points['bow_R5'][0][0] += r_width * 0.85  
        r_points['bow_R6'] = [cpV(r_points['bow_R5'][0]), 0]
        r_points['bow_R6'][0][0] -= r_width / 2  
        r_points['bow_R7'] = [cpV(r_points['bow_R1'][0]), 0]
        r_points['bow_R7'][0][1] += r_thickness * 0.5  
        
        # Knot
        r_points['knot_1'] = [cpV(r_points['U'][0]), 0]
        r_points['knot_1'][0][2] += r_width / 2  
        r_points['knot_2'] = [cpV(r_points['knot_1'][0]), 0]
        r_points['knot_2'][0][1] += r_thickness * 2  
        r_points['knot_3'] = [cpV(r_points['U'][0]), 0]
        r_points['knot_3'][0][1] += r_thickness * 2  
        r_points['knot_4'] = [cpV(r_points['knot_2'][0]), 0]
        r_points['knot_4'][0][2] -= r_width * 1.5  
        r_points['knot_4'][0][1] += r_width * 0.15  
        r_points['knot_5'] = [cpV(r_points['U'][0]), 0]
        r_points['knot_5'][0][2] -= r_width / 2  
        
        # Ends
        # Left end
        r_points['end_L1'] = [cpV(r_points['U'][0]), 0]
        r_points['end_L1'][0][2] += r_width / 2  
        
        return r_points

    @staticmethod
    def getRibbonWidth(r_size, side_d, side_e):
        """Calculate width of ribbon"""
        if side_d > side_e :
            smallest_side = side_e
        else:
            smallest_side = side_d

        r_width_s = smallest_side * 0.09

        if r_size == 'L':
            r_width = r_width_s * 4.0
        elif r_size == 'M':
            r_width = r_width_s * 2.5
        else:
            r_width = r_width_s

        return r_width

    def createRibbon(self, r_points, r_thickness, r_width):
        """
        Draw curves for where the ribbon goes.
        Var names: 1U = 1st iteration, upper quadrant, and so on
        Secondly, create a ribbon profile shape and extrude it
        along the curves.
        """
        # Curves
        crv_list_1U = [
            r_points['U'][0], r_points['UBmid'][0], r_points['UBend'][0], r_points['UB'][0],
            r_points['BU'][0], r_points['BUend'][0], r_points['BUmid'][0], r_points['B'][0],
            r_points['BDmid'][0], r_points['BDend'][0], r_points['BD'][0], r_points['DB'][0],
            r_points['DBend'][0], r_points['DBmid'][0], r_points['D'][0]
        ]

        crv_list_1D = [
            r_points['U'][0], r_points['UFmid'][0], r_points['UFend'][0], r_points['UF'][0],
            r_points['FU'][0], r_points['FUend'][0], r_points['FUmid'][0], r_points['F'][0],
            r_points['FDmid'][0], r_points['FDend'][0], r_points['FD'][0], r_points['DF'][0],
            r_points['DFend'][0], r_points['DFmid'][0], r_points['D'][0]
        ]

        crv_list_2L = [
            r_points['D'][0], r_points['DLmid'][0], r_points['DLend'][0], r_points['DL'][0],
            r_points['LD'][0], r_points['LDend'][0], r_points['LDmid'][0], r_points['L'][0],
            r_points['LUmid'][0], r_points['LUend'][0], r_points['LU'][0], r_points['UL'][0],
            r_points['ULend'][0], r_points['ULmid'][0], r_points['U'][0]
        ]

        crv_list_2R = [
            r_points['D'][0], r_points['DRmid'][0], r_points['DRend'][0], r_points['DR'][0],
            r_points['RD'][0], r_points['RDend'][0], r_points['RDmid'][0], r_points['R'][0],
            r_points['RUmid'][0], r_points['RUend'][0], r_points['RU'][0], r_points['UR'][0],
            r_points['URend'][0], r_points['URmid'][0], r_points['U'][0]
        ]

        crv_list_3L = [
            r_points['bow_L1'][0], r_points['bow_L2'][0], r_points['bow_L3'][0], r_points['bow_L4'][0],
            r_points['bow_L5'][0], r_points['bow_L6'][0], r_points['bow_L7'][0]
        ]

        crv_list_3R = [
            r_points['bow_R1'][0], r_points['bow_R2'][0], r_points['bow_R3'][0], r_points['bow_R4'][0],
            r_points['bow_R5'][0], r_points['bow_R6'][0]
        ]

        crv_list_4 = [
            r_points['knot_1'][0], r_points['knot_2'][0], r_points['knot_3'][0], r_points['knot_4'][0],
            r_points['knot_5'][0]
        ]

        curve_1U = mc.curve(p=crv_list_1U, n="ribbon_1U_crv_%s" % self.wrap_id)
        curve_1D = mc.curve(p=crv_list_1D, n="ribbon_1D_crv_%s" % self.wrap_id)
        curve_2L = mc.curve(p=crv_list_2L, n="ribbon_2L_crv_%s" % self.wrap_id)
        curve_2R = mc.curve(p=crv_list_2R, n="ribbon_2R_crv_%s" % self.wrap_id)
        curve_3L = mc.curve(p=crv_list_3L, n="ribbon_3L_crv_%s" % self.wrap_id)
        curve_3R = mc.curve(p=crv_list_3R, n="ribbon_3R_crv_%s" % self.wrap_id)
        curve_4 = mc.curve(p=crv_list_4, n="ribbon_4_crv_%s" % self.wrap_id)

        # Ribbon profile shape
        r_prof_1D = mc.circle(n="ribbon_1D_profile_" + self.wrap_id)
        
        # Use move command to set CV positions
        mc.move(r_width/2, r_thickness/2, 0, r_prof_1D[0] + ".cv[0]")
        mc.move(r_width/2, 0, 0, r_prof_1D[0] + ".cv[6]")
        mc.move(r_width/2, -(r_thickness/2), 0, r_prof_1D[0] + ".cv[7]")
        mc.move(0, r_thickness/2, 0, r_prof_1D[0] + ".cv[1]")
        mc.move(-(r_width/2), r_thickness/2, 0, r_prof_1D[0] + ".cv[2]")
        mc.move(-(r_width/2), 0, 0, r_prof_1D[0] + ".cv[3]")
        mc.move(-(r_width/2), -(r_thickness/2), 0, r_prof_1D[0] + ".cv[4]")
        mc.move(0, -(r_thickness/2), 0, r_prof_1D[0] + ".cv[5]")
        
        mc.xform(r_prof_1D[0], centerPivots=True)
        mc.move(r_points['U'][0][0], r_points['U'][0][1], r_points['U'][0][2], r_prof_1D[0])
        r_prof_1U = mc.instance(r_prof_1D[0], n="ribbon_1U_profile_" + self.wrap_id)
        mc.setAttr(r_prof_1U[0] + ".rotateY", 180) # Essentially flips normals
        
        r_prof_2R = mc.instance(r_prof_1D[0], n="ribbon_2R_profile_" + self.wrap_id)
        mc.setAttr(r_prof_2R[0] + ".rotateY", 90)
        mc.setAttr(r_prof_2R[0] + ".translateY", r_points['D'][0][1])
        r_prof_2L = mc.instance(r_prof_2R[0], n="ribbon_2L_profile_" + self.wrap_id)
        mc.setAttr(r_prof_2L[0] + ".rotateY", 270) # Flip normals 

        # Bow
        bow_rot = 5
        r_prof_3L = mc.instance(r_prof_1D[0], n="ribbon_3L_profile_" + self.wrap_id)
        mc.setAttr(r_prof_3L[0] + ".rotateY", 270 + bow_rot)
        mc.setAttr(r_prof_3L[0] + ".rotateX", -45)
        mc.setAttr(curve_3L + ".rotateY", 0 - bow_rot)
        
        r_prof_3R = mc.instance(r_prof_1D[0], n="ribbon_3R_profile_" + self.wrap_id)
        mc.setAttr(r_prof_3R[0] + ".rotateY", 90 - bow_rot)
        mc.setAttr(r_prof_3R[0] + ".rotateX", -45)
        mc.setAttr(curve_3R + ".rotateY", 0 + bow_rot)
        
        r_prof_4 = mc.instance(r_prof_1D[0], n="ribbon_4_profile_" + self.wrap_id)
        mc.setAttr(r_prof_4[0] + ".translateZ", r_width / 2)
        mc.setAttr(r_prof_4[0] + ".rotateX", 270)
        
        # Extrusions
        r_extrude_1U = mc.extrude(r_prof_1U[0], curve_1U, et=2, rn=True, n="ribbon_ext_1U" + self.wrap_id)
        r_extrude_1D = mc.extrude(r_prof_1D[0], curve_1D, et=2, rn=True, n="ribbon_ext_1D" + self.wrap_id)
        r_extrude_2L = mc.extrude(r_prof_2L[0], curve_2L, et=2, rn=True, n="ribbon_ext_2L" + self.wrap_id)
        r_extrude_2R = mc.extrude(r_prof_2R[0], curve_2R, et=2, rn=True, n="ribbon_ext_2R" + self.wrap_id)
        r_extrude_3L = mc.extrude(r_prof_3L[0], curve_3L, et=2, rn=True, n="ribbon_ext_3L" + self.wrap_id)
        r_extrude_3R = mc.extrude(r_prof_3R[0], curve_3R, et=2, rn=True, n="ribbon_ext_3R" + self.wrap_id)
        r_extrude_4 = mc.extrude(r_prof_4[0], curve_4, et=2, rn=True, n="ribbon_ext_4" + self.wrap_id)

        # Make ribbons taper
        mc.setAttr(r_extrude_3L[0] + ".scaleX", 0.8)
        mc.setAttr(r_extrude_3R[0] + ".scaleZ", 0.8)
        
        ribbons = {}
        
        # Helper function to get subCurve from extrude node
        def getSubCrv(extrude_node, subcurve_index=1):
            connections = mc.listConnections(extrude_node, type="subCurve")
            if connections and len(connections) > subcurve_index:
                return connections[subcurve_index]
            return None
        
        ribbons['1U'] = [curve_1U, r_extrude_1U, getSubCrv(r_extrude_1U)]
        ribbons['1D'] = [curve_1D, r_extrude_1D, getSubCrv(r_extrude_1D)]
        ribbons['2L'] = [curve_2L, r_extrude_2L, getSubCrv(r_extrude_2L)]
        ribbons['2R'] = [curve_2R, r_extrude_2R, getSubCrv(r_extrude_2R)]
        ribbons['3L'] = [curve_3L, r_extrude_3L, getSubCrv(r_extrude_3L)]
        ribbons['3R'] = [curve_3R, r_extrude_3R, getSubCrv(r_extrude_3R)]
        ribbons['4'] = [curve_4, r_extrude_4, getSubCrv(r_extrude_4)]

        # Parent to main ribbon group - curves
        mc.parent(curve_1U, self.r_curve_group_name)
        mc.parent(curve_1D, self.r_curve_group_name)
        mc.parent(curve_2L, self.r_curve_group_name)
        mc.parent(curve_2R, self.r_curve_group_name)
        mc.parent(curve_3L, self.r_curve_group_name)
        mc.parent(curve_3R, self.r_curve_group_name)
        mc.parent(curve_4, self.r_curve_group_name)
        
        # Parent extruded ribbons to group
        mc.parent(r_extrude_1U[0], self.ribbon_group_name)
        mc.parent(r_extrude_1D[0], self.ribbon_group_name)
        mc.parent(r_extrude_2L[0], self.ribbon_group_name)
        mc.parent(r_extrude_2R[0], self.ribbon_group_name)
        mc.parent(r_extrude_3L[0], self.ribbon_group_name)
        mc.parent(r_extrude_3R[0], self.ribbon_group_name)
        mc.parent(r_extrude_4[0], self.ribbon_group_name)
        
        # Parent profiles to group
        mc.parent(r_prof_1U[0], self.r_curve_group_name)
        mc.parent(r_prof_1D[0], self.r_curve_group_name)
        mc.parent(r_prof_2L[0], self.r_curve_group_name)
        mc.parent(r_prof_2R[0], self.r_curve_group_name)
        mc.parent(r_prof_3L[0], self.r_curve_group_name)
        mc.parent(r_prof_3R[0], self.r_curve_group_name)
        mc.parent(r_prof_4[0], self.r_curve_group_name)
        
        return ribbons, r_prof_1D

    def getObjectSides(self):
        """Get height, width and depth from boundingbox of just the object"""
        bbox = mc.exactWorldBoundingBox(self.wrap_gift)
        bbox_min = [bbox[0], bbox[1], bbox[2]]
        bbox_max = [bbox[3], bbox[4], bbox[5]]
        
        # Calculate dimensions
        side_a = abs(bbox_max[0] - bbox_min[0])  # width
        side_d = abs(bbox_max[1] - bbox_min[1])  # height
        side_e = abs(bbox_max[2] - bbox_min[2])  # depth
        
        return side_a, side_d, side_e
    
    def getWrapSides(self):
        """Get height, width and depth from boundingbox of the object wrapped in paper"""
        bbox_minmax = mc.polyEvaluate(self.wrap_paper[0], boundingBox=True)
        
        # Calculate dimensions
        side_w = abs(bbox_minmax[0][1] - bbox_minmax[0][0])
        side_h = abs(bbox_minmax[1][1] - bbox_minmax[1][0])
        side_d = abs(bbox_minmax[2][1] - bbox_minmax[2][0])
        
        return side_w, side_h, side_d

    def tieRibbon(self, seg):
        """
        Ties / unties the ribbon by modifying the curve extrusions.
        The process is divided into segments = seg
        """
        # Show ribbon segments based on value of seg
        if seg >= 1:
            mc.setAttr(self.ribbons['1U'][2] + ".maxValue", 1)
            mc.setAttr(self.ribbons['1D'][2] + ".maxValue", 1)
        if seg >= 2:
            mc.setAttr(self.ribbons['2L'][2] + ".maxValue", 1)
            mc.setAttr(self.ribbons['2R'][2] + ".maxValue", 1)
        if seg >= 3:
            mc.setAttr(self.ribbons['3L'][2] + ".maxValue", 1)
            mc.setAttr(self.ribbons['3R'][2] + ".maxValue", 1)
        if seg >= 4:
            mc.setAttr(self.ribbons['4'][2] + ".maxValue", 1)
    
        # Hide ribbon segments based on value of seg
        if seg == 0:
            mc.setAttr(self.ribbons['1U'][2] + ".maxValue", 0)
            mc.setAttr(self.ribbons['1D'][2] + ".maxValue", 0)
        if seg < 2:
            mc.setAttr(self.ribbons['2L'][2] + ".maxValue", 0)
            mc.setAttr(self.ribbons['2R'][2] + ".maxValue", 0)
        if seg < 3:
            mc.setAttr(self.ribbons['3L'][2] + ".maxValue", 0)
            mc.setAttr(self.ribbons['3R'][2] + ".maxValue", 0)
        if seg < 4:
            mc.setAttr(self.ribbons['4'][2] + ".maxValue", 0)

    def applyColor(self):
        """
        Set color of the wrapping paper and ribbon.
        """
        paper_shader = 'shd_paper_' + self.wrap_color.upper()
        mc.sets(self.wrap_paper[0], edit=True, forceElement=paper_shader)
        
        ribbon_shader = 'shd_ribbon_' + self.ribbon_color.upper()
        
        if isinstance(self.ribbons, dict):
            ribbon = []
            for key in self.ribbons:
                ribbon.append(self.ribbons[key][1][0])
        else:
            ribbon = self.ribbons
        
        # Apply shader to each ribbon element individually
        for r in ribbon:
            mc.sets(r, edit=True, forceElement=ribbon_shader)
    
    def newColor(self, p_color='', r_color=''):
        """
        Stores new colors and applies it to the paper and ribbon
        """
        if not p_color == 'current':
            self.wrap_color = self.setColor(p_color, 1)
        if not r_color == 'current':
            self.ribbon_color = self.setColor(r_color, 2)
        
        self.storeCtrlValues()
        self.applyColor()

    def changeRibbon(self, size='S'):
        """
        Change the ribbon size and scale the ribbon profiles accordingly
        """
        if size != self.ribbon_size:
            old_size = self.ribbon_size
            self.ribbon_size = size
            self.storeCtrlValues()
            
            mult = 1.0
            if old_size == 'S' and size == 'L':
                mult = 3.5
            if old_size == 'S' and size == 'M':
                mult = 2.5
            if old_size == 'M' and size == 'S':
                mult = 0.4
            if old_size == 'M' and size == 'L':
                mult = 1.4
            if old_size == 'L' and size == 'S':
                mult = 0.25
            if old_size == 'L' and size == 'M':
                mult = 0.625
            
            for prof in self.ribbon_prof:
                scale_x = mc.getAttr(prof + ".scaleX")
                new_scale_x = scale_x * mult
                mc.setAttr(prof + ".scaleX", new_scale_x)

    def reloadGiftWrap(self):
        self.removeGiftWrap()
        self.createGiftWrap(self.wrap_gift)

def windowUI():
    win_w = 300
    col_x_4 = win_w / 4
    
    # Create main window
    if mc.window("giftGeneratorWindow", exists=True):
        mc.deleteUI("giftGeneratorWindow")
    my_window = mc.window("giftGeneratorWindow", title="Gift Generator", rtf=True, width=win_w)
    
    # Main layout
    main_layout = mc.columnLayout(rowSpacing=10)
    
    # Wrap Gift frame
    wrap_frame = mc.frameLayout(label='Wrap Gift', borderStyle='etchedIn',
                                width=win_w, collapsable=True, collapse=False)
    
    # Wrap layout
    wrap_layout = mc.columnLayout(parent=wrap_frame)
    
    # Wrap row for size
    wrap_row_size = mc.rowLayout(numberOfColumns=4, columnWidth4=(col_x_4, col_x_4, col_x_4-5, col_x_4), parent=wrap_layout)
    mc.text(' Paper weight:', parent=wrap_row_size)
    wrap_sld_thk = mc.floatSliderGrp(minValue=0.005, maxValue=0.05, value=0.02, parent=wrap_row_size)
    mc.text('Ribbon size:', parent=wrap_row_size)
    wrap_opt_menu_r_size = mc.optionMenu(parent=wrap_row_size)
    mc.menuItem(label='Large', parent=wrap_opt_menu_r_size)
    mc.menuItem(label='Medium', parent=wrap_opt_menu_r_size)
    mc.menuItem(label='Small', parent=wrap_opt_menu_r_size)
    
    # Wrap row for color
    mc.setParent(wrap_layout)
    wrap_row_color = mc.rowLayout(numberOfColumns=4, columnWidth4=(col_x_4, col_x_4, col_x_4-5, col_x_4))
    mc.text(' Paper color:', parent=wrap_row_color)
    wrap_opt_menu_p_color = mc.optionMenu(parent=wrap_row_color)
    mc.menuItem(label='Random', parent=wrap_opt_menu_p_color)
    mc.menuItem(label='Red', parent=wrap_opt_menu_p_color)
    mc.menuItem(label='Green', parent=wrap_opt_menu_p_color)
    mc.menuItem(label='Blue', parent=wrap_opt_menu_p_color)
    mc.menuItem(label='Yellow', parent=wrap_opt_menu_p_color)
    mc.menuItem(label='Black', parent=wrap_opt_menu_p_color)
    mc.menuItem(label='White', parent=wrap_opt_menu_p_color)
    
    mc.text('Ribbon color:', parent=wrap_row_color)
    wrap_opt_menu_r_color = mc.optionMenu(parent=wrap_row_color)
    mc.menuItem(label='Random', parent=wrap_opt_menu_r_color)
    mc.menuItem(label='Red', parent=wrap_opt_menu_r_color)
    mc.menuItem(label='Green', parent=wrap_opt_menu_r_color)
    mc.menuItem(label='Blue', parent=wrap_opt_menu_r_color)
    mc.menuItem(label='Yellow', parent=wrap_opt_menu_r_color)
    
    # Separator
    mc.setParent(wrap_layout)
    mc.separator(height=10, width=win_w, style='in')
    mc.text(" Animation", font='smallBoldLabelFont')
    
    # Animation row
    wrap_row_anim = mc.rowLayout(numberOfColumns=4, columnWidth4=(col_x_4, col_x_4, col_x_4-5, col_x_4))
    mc.text('Start frame:', width=col_x_4, align='right', parent=wrap_row_anim)
    wrap_int_anim_s = mc.intField(minValue=0, width=45, value=1, parent=wrap_row_anim)
    mc.text('End frame:', width=col_x_4, align='right', parent=wrap_row_anim)
    wrap_int_anim_e = mc.intField(minValue=0, width=45, value=24, parent=wrap_row_anim)
    
    # Separator
    mc.setParent(wrap_layout)
    mc.separator(height=10, width=win_w, style='in')
    
    # Button row
    wrap_row_btn = mc.rowLayout(numberOfColumns=2, columnWidth2=(win_w/2-30, win_w/2-30))
    mc.text('', parent=wrap_row_btn)
    wrap_btn_run = mc.button(label='Wrap', width=60, parent=wrap_row_btn)
    
    # Info text
    mc.setParent(wrap_layout)
    mc.text("Wraps selected object(s), animate the whole process\n" +
            "by adjusting the connected attribute of the control handle",
            font='obliqueLabelFont', align='center', width=win_w-10)
    
    # Modify Wrap frame
    mc.setParent(main_layout)
    mod_frame = mc.frameLayout(label='Modifiy Wrap', borderStyle='etchedIn',
                              width=win_w, collapsable=True, collapse=True)
    
    # Modify layout
    mod_layout = mc.columnLayout(parent=mod_frame)
    
    # Scan buttons row
    mod_row_scan_btn = mc.rowLayout(numberOfColumns=3, columnWidth3=(15, win_w/2-15, win_w/2-10), parent=mod_layout)
    mc.text('', parent=mod_row_scan_btn)
    mod_btn_scan_sel = mc.button(label='Scan selection', width=120, parent=mod_row_scan_btn)
    mod_btn_scan_scn = mc.button(label='Scan scene', width=100, parent=mod_row_scan_btn)
    
    # Info text
    mc.setParent(mod_layout)
    mc.text("Scans for gifts that have already been wrapped",
            font='obliqueLabelFont', align='center', width=win_w)
    mc.separator(height=10, width=win_w, style='in')
    mc.text(' Result:', font='smallBoldLabelFont')
    
    # Results list
    mod_txt_list = mc.textScrollList(numberOfRows=8, allowMultiSelection=True,
                                    width=win_w-5, height=150, font='smallFixedWidthFont')
    
    # Paper weight section
    mc.text(" Paper Weight:", font='smallBoldLabelFont')
    mod_row_pweight = mc.rowLayout(numberOfColumns=2, columnWidth2=(200, 100))
    mod_sld_thk = mc.floatSliderGrp(minValue=0.005, maxValue=0.05, value=0.02, 
                                    field=True, width=180, precision=3, 
                                    columnWidth2=(50, 130), parent=mod_row_pweight)
    mod_btn_pweight = mc.button(label='Edit', width=80, parent=mod_row_pweight)
    
    # Separator
    mc.setParent(mod_layout)
    mc.separator(height=10, width=win_w, style='in')
    
    # Color header row
    mod_row_color_hdr = mc.rowLayout(numberOfColumns=3, columnWidth3=(100, 100, 80))
    mc.text(' Paper color:', font='tinyBoldLabelFont', parent=mod_row_color_hdr)
    mc.text('Ribbon color:', font='tinyBoldLabelFont', parent=mod_row_color_hdr)
    mc.text(' ', parent=mod_row_color_hdr)
    
    # Color options row
    mc.setParent(mod_layout)
    mod_row_color = mc.rowLayout(numberOfColumns=3, columnWidth3=(100, 100, 80))
    mod_opt_menu_p_color = mc.optionMenu(parent=mod_row_color)
    mc.menuItem(label='Random', parent=mod_opt_menu_p_color)
    mc.menuItem(label='Red', parent=mod_opt_menu_p_color)
    mc.menuItem(label='Green', parent=mod_opt_menu_p_color)
    mc.menuItem(label='Blue', parent=mod_opt_menu_p_color)
    mc.menuItem(label='Yellow', parent=mod_opt_menu_p_color)
    mc.menuItem(label='Black', parent=mod_opt_menu_p_color)
    mc.menuItem(label='White', parent=mod_opt_menu_p_color)
    mc.menuItem(label='Current', parent=mod_opt_menu_p_color)
    
    mod_opt_menu_r_color = mc.optionMenu(parent=mod_row_color)
    mc.menuItem(label='Random', parent=mod_opt_menu_r_color)
    mc.menuItem(label='Red', parent=mod_opt_menu_r_color)
    mc.menuItem(label='Green', parent=mod_opt_menu_r_color)
    mc.menuItem(label='Blue', parent=mod_opt_menu_r_color)
    mc.menuItem(label='Yellow', parent=mod_opt_menu_r_color)
    mc.menuItem(label='Current', parent=mod_opt_menu_r_color)
    
    mod_btn_color = mc.button(label='Edit', width=80, parent=mod_row_color)
    
    # Separator
    mc.setParent(mod_layout)
    mc.separator(height=10, width=win_w, style='in')
    mc.text(' Ribbon size:', font='tinyBoldLabelFont')
    
    # Ribbon size row
    mod_row_r_sz = mc.rowLayout(numberOfColumns=2, columnWidth2=(200, 80))
    mod_radio_r_sz = mc.radioButtonGrp(labelArray3=['Small', 'Medium', 'Large'], 
                                       numberOfRadioButtons=3, columnWidth3=(60, 60, 60), 
                                       select=3, parent=mod_row_r_sz)
    mod_btn_r_sz = mc.button(label='Edit', width=80, parent=mod_row_r_sz)
    
    # Separator
    mc.setParent(mod_layout)
    mc.separator(height=10, width=win_w, style='in')
    
    # Animation header row
    mod_row_anim_hdr = mc.rowLayout(numberOfColumns=3, columnWidth3=(100, 100, 80))
    mc.text(' Anim. start:', font='tinyBoldLabelFont', parent=mod_row_anim_hdr)
    mc.text('Anim. end:', font='tinyBoldLabelFont', parent=mod_row_anim_hdr)
    mc.text(' ', parent=mod_row_anim_hdr)
    
    # Animation fields row
    mc.setParent(mod_layout)
    mod_row_anim = mc.rowLayout(numberOfColumns=3, columnWidth3=(100, 100, 80))
    mod_int_anim_s = mc.intField(minValue=0, width=45, value=1, parent=mod_row_anim)
    mod_int_anim_e = mc.intField(minValue=0, width=45, value=24, parent=mod_row_anim)
    mod_btn_anim = mc.button(label='Edit', width=80, parent=mod_row_anim)
    
    # Set button commands
    mc.button(wrap_btn_run, edit=True, 
              command=lambda *args: runWrap(wrap_sld_thk, wrap_opt_menu_p_color,
                                           wrap_opt_menu_r_size, wrap_opt_menu_r_color, 
                                           wrap_int_anim_s, wrap_int_anim_e))
    
    mc.button(mod_btn_scan_sel, edit=True, 
              command=lambda *args: scanForWraps(mod_txt_list, True))
              
    mc.button(mod_btn_scan_scn, edit=True, 
              command=lambda *args: scanForWraps(mod_txt_list, False))
              
    mc.button(mod_btn_pweight, edit=True, 
              command=lambda *args: editPaperWeight(mod_txt_list, mod_sld_thk))
              
    mc.button(mod_btn_color, edit=True, 
              command=lambda *args: editColors(mod_txt_list, mod_opt_menu_p_color, mod_opt_menu_r_color))
              
    mc.button(mod_btn_r_sz, edit=True, 
              command=lambda *args: editRibbonSize(mod_txt_list, mod_radio_r_sz))
              
    mc.button(mod_btn_anim, edit=True, 
              command=lambda *args: editAnimation(mod_txt_list, mod_int_anim_s, mod_int_anim_e))
              
    mc.textScrollList(mod_txt_list, edit=True, 
                     selectCommand=lambda *args: deselectHeader(mod_txt_list))
    
    # Show window
    mc.showWindow(my_window)

def deselectHeader(txt_list):
    mc.textScrollList(txt_list, edit=True, deselectIndexedItem=[1, 2])

def runWrap(p_thk, p_clr, r_sz, r_clr, an_s, an_e):
    paper_thickness = mc.floatSliderGrp(p_thk, query=True, value=True)
    paper_color = mc.optionMenu(p_clr, query=True, value=True).lower()
    ribbon_size = mc.optionMenu(r_sz, query=True, value=True)[0]
    ribbon_color = mc.optionMenu(r_clr, query=True, value=True).lower()
    animation_start = mc.intField(an_s, query=True, value=True)
    animation_end = mc.intField(an_e, query=True, value=True)
    
    objects = mc.ls(selection=True)
    
    for o in objects[:32]:
        GiftWrap(
            o, 'create', ribbon_size, paper_thickness, paper_color,
            ribbon_color, animation_start, animation_end
        )

def scanForWraps(txt_list, _scan_mode, selection=None):
    global wrap_list

    _scan_mode = None # TODO: Implement `scan_mode`

    if selection is None:
        all_transforms = mc.ls(type='transform')
        p_grp = re.compile('^.*_gift_wrap_[0-9A-Z]{5}_GRP$')
        p_ctrl = re.compile('^CTRL_gift_[0-9A-Z]{5}$')

        all_groups = filter(p_grp.match, all_transforms)
        all_children = map(lambda g: mc.listRelatives(g, type='transform') or [], all_groups)
        wrap_list = list(filter(p_ctrl.match, itertools.chain.from_iterable(all_children)))

    mc.textScrollList(txt_list, edit=True, removeAll=True)
    
    # Titles
    col1_title = addPadding('Object', 1)
    col2_title = addPadding('ID', 2)
    col3_title = addPadding('P. Weight', 3)
    col4_title = addPadding('P. Color', 4)
    col5_title = addPadding('R. Color', 5)
    col6_title = addPadding('R. Size', 6)
    col7_title = addPadding('Animation', 7)
    
    if len(wrap_list) > 0:
        titles = col1_title + col2_title + col3_title + col4_title
        titles += col5_title + col6_title + col7_title
        mc.textScrollList(txt_list, edit=True, append=[titles])
        
        mc.textScrollList(txt_list, edit=True, append=[addPadding('-', 0)])
        
        for w in wrap_list:
            wrap = GiftWrap(w, 'load')
            wrap_name = addPadding(wrap.wrap_name, 1)
            wrap_id = addPadding(wrap.wrap_id, 2)
            paper_thickness = addPadding(str(wrap.wrap_thickness), 3)
            paper_color = addPadding(wrap.wrap_color, 4)
            ribbon_color = addPadding(wrap.ribbon_color, 5)
            ribbon_size = addPadding(wrap.ribbon_size, 6)
            animation = addPadding(str(wrap.animation_start) + ' - ' + str(wrap.animation_end), 7)
            
            attributes = wrap_name + wrap_id + paper_thickness
            attributes += paper_color + ribbon_color + ribbon_size
            attributes += animation
            
            mc.textScrollList(txt_list, edit=True, append=[attributes])
        
        if selection is None:
            num_items = mc.textScrollList(txt_list, query=True, numberOfItems=True) + 1
            for i in range(3, num_items):
                mc.textScrollList(txt_list, edit=True, selectIndexedItem=i)
        else:
            for s in selection:
                mc.textScrollList(txt_list, edit=True, selectIndexedItem=s+3)
    else:
        mc.textScrollList(txt_list, edit=True, append=['None found'])
        mc.textScrollList(txt_list, edit=True, append=[addPadding(' ', 0)])

def addPadding(text, column):
    """
    Add spaces to the given text in order to
    align it properly in the scroll list.
    """
    # Column length
    col_len = [0, 18, 8, 10, 10, 10, 10, 10]  # 0 to 7

    if column == 0:
        return text[:1] * ( sum(col_len) + 7)
    else:
        text = text[:col_len[column]]
        padding = col_len[column] - len(text)
        text += ' ' * (padding+1)

        return text

def editPaperWeight(txt_list, p_weight):
    selection = removeHeader(txt_list)
    
    wrap_thickness = mc.floatSliderGrp(p_weight, query=True, value=True)
    
    if selection is not None:
        for s in selection:
            edit_gift = GiftWrap(wrap_list[s], 'load')
            edit_gift.wrap_thickness = wrap_thickness
            edit_gift.reloadGiftWrap()
            wrap_list[s] = edit_gift.ctrl_handle[0]
            
        scanForWraps(txt_list, 0, selection)

def editColors(txt_list, p_color, r_color):
    selection = removeHeader(txt_list)
    
    wrap_color = mc.optionMenu(p_color, query=True, value=True).lower()
    ribbon_color = mc.optionMenu(r_color, query=True, value=True).lower()
    
    if selection is not None:
        for s in selection:
            edit_gift = GiftWrap(wrap_list[s], 'load')
            edit_gift.newColor(wrap_color, ribbon_color)
        
        scanForWraps(txt_list, 0, selection) # Refresh scroll list

def editRibbonSize(txt_list, r_size):
    selection = removeHeader(txt_list)
    
    r_size_value = mc.radioButtonGrp(r_size, query=True, select=True)
    
    if r_size_value == 1:
        ribbon_size = 'S'
    elif r_size_value == 2:
        ribbon_size = 'M'
    else:
        ribbon_size = 'L'
    
    if selection is not None:
        for s in selection:
            edit_gift = GiftWrap(wrap_list[s], 'load')
            edit_gift.changeRibbon(ribbon_size)
        
        scanForWraps(txt_list, 0, selection)

def editAnimation(txt_list, anim_s, anim_e):
    selection = removeHeader(txt_list)
    
    animation_start = mc.intField(anim_s, query=True, value=True)
    animation_end = mc.intField(anim_e, query=True, value=True)
    
    if selection is not None:
        for s in selection:
            edit_gift = GiftWrap(wrap_list[s], 'load')
            
            edit_gift.setAnimation(animation_start, animation_end)
        
        scanForWraps(txt_list, 0, selection) # Refresh scroll list

def removeHeader(txt_list):
    """
    Remove header from the selection so that it
    corresponds to the wrap_list.
    """
    hdr_rows = 2  # Number of header rows
    
    items = mc.textScrollList(txt_list, query=True, selectIndexedItem=True)
    
    if not items:
        return None
    else:
        gifts = [((hdr_rows + 1) * -1) + item for item in items]
        return gifts

def createShaders():
    """
    These shaders are used for coloring the generated geometry
    """
    # Ribbon Materials
    # Green Material
    rg_name = 'ribbon_GREEN'
    if not mc.objExists("mat_" + rg_name):
        mat_ribbon_green = mc.shadingNode("blinn", asShader=True, name="mat_" + rg_name)
        mc.setAttr(mat_ribbon_green + ".color", 0.1, 0.6, 0.1, type="double3")
        mc.setAttr(mat_ribbon_green + ".eccentricity", 0.6)
        mc.setAttr(mat_ribbon_green + ".specularRollOff", 0.7)
    else:
        mat_ribbon_green = "mat_" + rg_name
        
    # Green Shader
    if not mc.objExists("shd_" + rg_name):
        shd_ribbon_green = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name="shd_" + rg_name)
        # Connect material to shader
        mc.connectAttr(mat_ribbon_green + ".outColor", shd_ribbon_green + ".surfaceShader")

    # Red Material
    rr_name = 'ribbon_RED'
    if not mc.objExists("mat_" + rr_name):
        mat_ribbon_red = mc.shadingNode("blinn", asShader=True, name="mat_" + rr_name)
        mc.setAttr(mat_ribbon_red + ".color", 0.6, 0.1, 0.1, type="double3")
        mc.setAttr(mat_ribbon_red + ".eccentricity", 0.6)
        mc.setAttr(mat_ribbon_red + ".specularRollOff", 0.7)
    else:
        mat_ribbon_red = "mat_" + rr_name
        
    # Red Shader
    if not mc.objExists("shd_" + rr_name):
        shd_ribbon_red = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name="shd_" + rr_name)
        # Connect material to shader
        mc.connectAttr(mat_ribbon_red + ".outColor", shd_ribbon_red + ".surfaceShader")

    # Blue Material
    rb_name = 'ribbon_BLUE'
    if not mc.objExists("mat_" + rb_name):
        mat_ribbon_blue = mc.shadingNode("blinn", asShader=True, name="mat_" + rb_name)
        mc.setAttr(mat_ribbon_blue + ".color", 0.1, 0.1, 0.6, type="double3")
        mc.setAttr(mat_ribbon_blue + ".eccentricity", 0.6)
        mc.setAttr(mat_ribbon_blue + ".specularRollOff", 0.7)
    else:
        mat_ribbon_blue = "mat_" + rb_name
        
    # Blue Shader
    if not mc.objExists("shd_" + rb_name):
        shd_ribbon_blue = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name="shd_" + rb_name)
        # Connect material to shader
        mc.connectAttr(mat_ribbon_blue + ".outColor", shd_ribbon_blue + ".surfaceShader")

    # Yellow Material
    ry_name = 'ribbon_YELLOW'
    if not mc.objExists("mat_" + ry_name):
        mat_ribbon_yellow = mc.shadingNode("blinn", asShader=True, name="mat_" + ry_name)
        mc.setAttr(mat_ribbon_yellow + ".color", 0.8, 0.7, 0.1, type="double3")
        mc.setAttr(mat_ribbon_yellow + ".eccentricity", 0.6)
        mc.setAttr(mat_ribbon_yellow + ".specularRollOff", 0.7)
    else:
        mat_ribbon_yellow = "mat_" + ry_name
        
    # Yellow Shader
    if not mc.objExists("shd_" + ry_name):
        shd_ribbon_yellow = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name="shd_" + ry_name)
        # Connect material to shader
        mc.connectAttr(mat_ribbon_yellow + ".outColor", shd_ribbon_yellow + ".surfaceShader")

    # Paper Materials
    # Green Material
    pg_name = 'paper_GREEN'
    if not mc.objExists("mat_" + pg_name):
        mat_paper_green = mc.shadingNode("lambert", asShader=True, name="mat_" + pg_name)
        mc.setAttr(mat_paper_green + ".color", 0.2, 0.6, 0.2, type="double3")
        mc.setAttr(mat_paper_green + ".diffuse", 1)
    else:
        mat_paper_green = "mat_" + pg_name
        
    # Green Shader
    if not mc.objExists("shd_" + pg_name):
        shd_paper_green = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name="shd_" + pg_name)
        # Connect material to shader
        mc.connectAttr(mat_paper_green + ".outColor", shd_paper_green + ".surfaceShader")

    # Red Material
    pr_name = 'paper_RED'
    if not mc.objExists("mat_" + pr_name):
        mat_paper_red = mc.shadingNode("lambert", asShader=True, name="mat_" + pr_name)
        mc.setAttr(mat_paper_red + ".color", 0.8, 0.3, 0.3, type="double3")
        mc.setAttr(mat_paper_red + ".diffuse", 1)
    else:
        mat_paper_red = "mat_" + pr_name
        
    # Red Shader
    if not mc.objExists("shd_" + pr_name):
        shd_paper_red = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name="shd_" + pr_name)
        # Connect material to shader
        mc.connectAttr(mat_paper_red + ".outColor", shd_paper_red + ".surfaceShader")

    # Blue Material
    pb_name = 'paper_BLUE'
    if not mc.objExists("mat_" + pb_name):
        mat_paper_blue = mc.shadingNode("lambert", asShader=True, name="mat_" + pb_name)
        mc.setAttr(mat_paper_blue + ".color", 0.3, 0.3, 0.8, type="double3")
        mc.setAttr(mat_paper_blue + ".diffuse", 1)
    else:
        mat_paper_blue = "mat_" + pb_name
        
    # Blue Shader
    if not mc.objExists("shd_" + pb_name):
        shd_paper_blue = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name="shd_" + pb_name)
        # Connect material to shader
        mc.connectAttr(mat_paper_blue + ".outColor", shd_paper_blue + ".surfaceShader")

    # Yellow Material
    py_name = 'paper_YELLOW'
    if not mc.objExists("mat_" + py_name):
        mat_paper_yellow = mc.shadingNode("lambert", asShader=True, name="mat_" + py_name)
        mc.setAttr(mat_paper_yellow + ".color", 0.8, 0.75, 0.3, type="double3")
        mc.setAttr(mat_paper_yellow + ".diffuse", 1)
    else:
        mat_paper_yellow = "mat_" + py_name
        
    # Yellow Shader
    if not mc.objExists("shd_" + py_name):
        shd_paper_yellow = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name="shd_" + py_name)
        # Connect material to shader
        mc.connectAttr(mat_paper_yellow + ".outColor", shd_paper_yellow + ".surfaceShader")

    # White Material
    pw_name = 'paper_WHITE'
    if not mc.objExists("mat_" + pw_name):
        mat_paper_white = mc.shadingNode("lambert", asShader=True, name="mat_" + pw_name)
        mc.setAttr(mat_paper_white + ".color", 0.98, 0.98, 0.98, type="double3")
        mc.setAttr(mat_paper_white + ".diffuse", 1)
    else:
        mat_paper_white = "mat_" + pw_name
        
    # White Shader
    if not mc.objExists("shd_" + pw_name):
        shd_paper_white = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name="shd_" + pw_name)
        # Connect material to shader
        mc.connectAttr(mat_paper_white + ".outColor", shd_paper_white + ".surfaceShader")

    # Black Material
    pbl_name = 'paper_BLACK'
    if not mc.objExists("mat_" + pbl_name):
        mat_paper_black = mc.shadingNode("lambert", asShader=True, name="mat_" + pbl_name)
        mc.setAttr(mat_paper_black + ".color", 0.1, 0.1, 0.1, type="double3")
        mc.setAttr(mat_paper_black + ".diffuse", 1)
    else:
        mat_paper_black = "mat_" + pbl_name
        
    # Black Shader
    if not mc.objExists("shd_" + pbl_name):
        shd_paper_black = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name="shd_" + pbl_name)
        # Connect material to shader
        mc.connectAttr(mat_paper_black + ".outColor", shd_paper_black + ".surfaceShader")

createShaders()
windowUI()
