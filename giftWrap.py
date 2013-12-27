# -*- coding: iso-8859-15 -*-
"""
Gift Wrap Script, Fredrik Juréen 2013
"""
import pymel.core as pm
import maya.cmds as mc
import math as math
import pymel.core.datatypes as dt
import maya.mel as mel
import string
import random

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
        if  not pm.objExists(name):
            raise ValueError('Node "%s" does not exist' % (name,))

        self.wrap_name = name # Node name

        if mode == 'create':
            self.wrap_id = self.idGenerator(size=5) # Unique ID used for naming
            if thickness < 0.02 : thickness = 0.02
            self.wrap_thickness = thickness # Paper density in maya units
            self.ribbon_thickness = thickness # Ribbon
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
        pm.select(None) # Deselect
        self.main_group = pm.group(n="%s_gift_wrap_%s_GRP" % (self.wrap_name, self.wrap_id))
        pm.select(None)
        self.ribbon_group = pm.group(n="ribbon_%s_GRP" % (self.wrap_id,))
        pm.select(None)
        self.gift_group = pm.group(n="gift_%s_GRP" % (self.wrap_id),)
        pm.select(None)
        self.fold_group = pm.group(n="fold_%s_GRP" % (self.wrap_id),)
        pm.select(None)
        self.obj_group = pm.group(n="obj_%s_GRP" % (self.wrap_id),)
        pm.select(None)
        self.cluster_group = pm.group(n="cluster_%s_GRP" % (self.wrap_id),)
        pm.inheritTransform(self.cluster_group, off=True) # Clusters need to stay where they are
        pm.select(None)
        self.r_curve_group = pm.group(n="ribbon_crv_%s_GRP" % (self.wrap_id),)
        pm.inheritTransform(self.r_curve_group, off=True) # Ribbon curves need to stay where they are

        if not obj:
            # Get object to be gift wrapped
            self.wrap_gift = pm.PyNode(self.wrap_name)

            # Move gift into position
            self.moveGift()

        side_a, side_d, side_e = self.getObjectSides() # bounding box
        self.fold_fix = side_d / 113 # value used to slightly offset the x value of some of the fold clusters that act up

        # parent all groups to ctrl handle
        self.ctrl_handle = self.createControlHandle(side_a*1.4)
        self.storeCtrlValues() # Store values in the CTRL handle for future reference
        pm.parent(self.ctrl_handle[0], self.main_group)
        pm.parent([self.fold_group, self.obj_group], self.gift_group)
        pm.parent([self.gift_group, self.cluster_group, self.ribbon_group, self.r_curve_group], self.ctrl_handle[0])
        pm.parent(self.wrap_gift, self.obj_group)

        self.cluster_group.visibility.set(0)
        self.r_curve_group.visibility.set(0)

        # get folding pattern, create folding plane
        self.folding_pattern = self.getFoldingPattern(side_a, side_d, side_e, self.wrap_thickness)
        self.f_plane, self.folding_pattern = self.createFoldingPlane(self.folding_pattern)
        self.f_plane[0].visibility.set(0)
        pm.parent(self.f_plane, self.fold_group)

        # create paper mesh and folding clusters
        self.wrap_paper = self.createPaper(self.f_plane, self.wrap_thickness)
        self.wrap_paper[0].visibility.set(1)
        self.folding_pivots =  self.getFoldingPivots(self.folding_pattern)
        self.createClusters(self.folding_pattern, self.folding_pivots)

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

        self.ctrl_handle[0].animation.set(15)

    def removeGiftWrap(self):
        """
        Unparents object to be wrapped, resets rotate/translate,
        deletes everything else.
        """
        pm.parent(self.wrap_gift, w=True) # Unparent object
        pm.move(0, self.wrap_thickness, 0, self.wrap_gift, rpr=True)
        self.wrap_gift.rotate.set(0,0,0)
        pm.delete(self.main_group) # Remove everything else

    def loadGiftWrap(self):
        self.ctrl_handle = [pm.PyNode(self.wrap_name)]
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

        self.wrap_gift = pm.PyNode(obj_name)
        self.main_group = pm.PyNode(main_grp_name)
        self.wrap_paper = [pm.PyNode(paper_name)]

        self.ribbons = pm.listRelatives(self.ctrl_handle, ad=True, ap=False, typ="nurbsSurface")

        ribbon_prof = pm.listRelatives(self.ctrl_handle, ad=True, ap=False, typ="nurbsCurve")
        ribbon_prof = ribbon_prof[-1]
        self.ribbon_prof = pm.listRelatives(ribbon_prof, ap=True)

        self.ini_r = self.main_group.rotate.get()
        self.ini_t = self.main_group.translate.get()

    def storeCtrlValues(self):
        self.ctrl_handle[0].wrap_name.set(self.wrap_name)
        self.ctrl_handle[0].wrap_id.set(self.wrap_id)
        self.ctrl_handle[0].wrap_thickness.set(self.wrap_thickness)
        self.ctrl_handle[0].wrap_color.set(self.wrap_color)
        self.ctrl_handle[0].ribbon_size.set(self.ribbon_size)
        self.ctrl_handle[0].ribbon_color.set(self.ribbon_color)
        self.ctrl_handle[0].animation_start.set(self.animation_start)
        self.ctrl_handle[0].animation_end.set(self.animation_end)

    def retrieveCtrlValues(self):
        self.wrap_name = self.ctrl_handle[0].wrap_name.get()
        self.wrap_id = self.ctrl_handle[0].wrap_id.get()
        self.wrap_thickness = self.ctrl_handle[0].wrap_thickness.get()
        self.wrap_color = self.ctrl_handle[0].wrap_color.get()
        self.ribbon_size = self.ctrl_handle[0].ribbon_size.get()
        self.ribbon_color = self.ctrl_handle[0].ribbon_color.get()
        self.animation_start = self.ctrl_handle[0].animation_start.get()
        self.animation_end = self.ctrl_handle[0].animation_end.get()

    def moveGift(self):
        """
        Move object to be wrapped(the gift) to the origin.
        Before wrapping we want to position the gift:
         > The largest sides facing down/up along the y-axis
         > The smallest sides pointing to the left/right along the x-axis
        """
        # Store initial transform values
        self.ini_r = self.wrap_gift.getRotation(space='object')
        self.ini_t = self.wrap_gift.getTranslation(space='object')
        # Store initial pivot values
        self.ini_sp = self.wrap_gift.getScalePivot()
        self.ini_rp = self.wrap_gift.getRotatePivot()
        # Center pivot
        self.wrap_gift.centerPivots()
        # Reset rotation
        self.wrap_gift.setRotation([0,0,0], space='object')

        pm.move(0, 0, 0, self.wrap_gift, rpr=True)

        # Get bounding box dimensions
        bbox_minmax = self.wrap_gift.boundingBoxMax.get() - self.wrap_gift.boundingBoxMin.get()
        self.bbox_height = bbox_minmax[1]
        self.bbox_depth = bbox_minmax[2]
        self.bbox_width = bbox_minmax[0]

        # Sort sides by area
        side_area = [
            ('dw', self.bbox_depth * self.bbox_width),
            ('dh', self.bbox_depth * self.bbox_height),
            ('wh', self.bbox_width * self.bbox_height)
        ]

        side_area.sort(key = lambda sArea: sArea[1])

        # Positions object, largest side facing down(Y), pivot centered to bottom
        gift_new_pivot = []
        gift_add_rot = []

        if side_area[2][0] == 'dw':
            gift_new_pivot = [0, self.bbox_height / -2, 0]
            self.wrap_gift.setScalePivot(gift_new_pivot)
            self.wrap_gift.setRotatePivot(gift_new_pivot)
            pm.move(0, self.wrap_thickness, 0, self.wrap_gift, rpr=True)

        elif side_area[2][0] == 'dh':
            gift_new_pivot = [self.bbox_width / -2, 0, 0]
            self.wrap_gift.setScalePivot(gift_new_pivot)
            self.wrap_gift.setRotatePivot(gift_new_pivot)
            pm.move(0, self.wrap_thickness, 0, self.wrap_gift, rpr=True)
            self.wrap_gift.setRotation([0, 0, 90], space='object')

        elif side_area[2][0] == 'wh':
            gift_new_pivot = [0, 0, self.bbox_depth/2]
            self.wrap_gift.setScalePivot(gift_new_pivot)
            self.wrap_gift.setRotatePivot(gift_new_pivot)
            pm.move(0, self.wrap_thickness, 0, self.wrap_gift, rpr=True)
            self.wrap_gift.setRotation([90, 0, 0], space='object')

        pm.makeIdentity(self.wrap_gift, a=True)

        # Rotates object, smallest side pointing left/right(X)

        if  side_area[2][0] == 'dw' and side_area[0][0] == 'wh':
            gift_add_rot = self.wrap_gift.getRotation(space='object')
            gift_add_rot[1] += 90
            self.wrap_gift.setRotation(gift_add_rot, space='object')

        elif  side_area[2][0] == 'dh' and side_area[0][0] == 'wh':
            gift_add_rot = self.wrap_gift.getRotation(space='object')
            gift_add_rot[1] += 90
            self.wrap_gift.setRotation(gift_add_rot, space='object')

        elif  side_area[2][0] == 'wh' and side_area[0][0] == 'dw':
            gift_add_rot = self.wrap_gift.getRotation(space='object')
            gift_add_rot[1] += 90
            self.wrap_gift.setRotation(gift_add_rot, space='object')

    def moveBack(self):
        """
        Moves the object back to its initial position
        """
        self.main_group.translate.set(self.ini_t)
        self.main_group.rotate.set(self.ini_r)

    def createControlHandle(self, radius):
        ctrl = pm.circle(r=radius, n="CTRL_gift_" + self.wrap_id)
        pm.addAttr(longName="animation", k=True)
        pm.addAttr(longName="wrap_name", dt='string', hidden=True, k=False)
        pm.addAttr(longName="wrap_id", dt='string', hidden=True, k=False)
        pm.addAttr(longName="wrap_thickness", at='float', hidden=True, k=False)
        pm.addAttr(longName="wrap_color", dt='string', hidden=True, k=False)
        pm.addAttr(longName="ribbon_size", dt='string', hidden=True, k=False)
        pm.addAttr(longName="ribbon_color", dt='string', hidden=True, k=False)
        pm.addAttr(longName="animation_start", hidden=True, k=False)
        pm.addAttr(longName="animation_end", hidden=True, k=False)
        ctrl[0].rotate.set(90,0,0)
        pm.makeIdentity(ctrl, a=True)
        return ctrl

    def setColor(self, color, type=1):
        c_list = ['green', 'red', 'blue', 'yellow']
        if type == 1 : c_list += ['white', 'black']
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
        if gft_side_e < (2 * gft_side_b):
            self.wrap_overlap = True;
        else:
            self.wrap_overlap = False;

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
        # x = F
        gift_fold_points = {'F1' : [dt.Vector(x_f, y_gft, z_1),0]}
        gift_fold_points['F2'] = [dt.Vector(x_f, y_gft, z_2),0]
        gift_fold_points['F3'] = [dt.Vector(x_f, y_gft, z_3),0]
        gift_fold_points['F4'] = [dt.Vector(x_f, y_gft, 0.0),0]
        gift_fold_points['F5'] = [dt.Vector(x_f, y_gft, z_5),0]
        gift_fold_points['F6'] = [dt.Vector(x_f, y_gft, z_6),0]
        gift_fold_points['F7'] = [dt.Vector(x_f, y_gft, z_7),0]
        gift_fold_points['F8'] = [dt.Vector(x_f, y_gft, z_8),0]
        # x = G
        gift_fold_points['G1'] = [dt.Vector(x_g, y_gft, z_1),0]
        gift_fold_points['G2'] = [dt.Vector(x_g, y_gft, z_2),0]
        gift_fold_points['G3'] = [dt.Vector(x_g, y_gft, z_3),0]
        gift_fold_points['G4'] = [dt.Vector(x_g, y_gft, 0.0),0]
        gift_fold_points['G5'] = [dt.Vector(x_g, y_gft, z_5),0]
        gift_fold_points['G6'] = [dt.Vector(x_g, y_gft, z_6),0]
        gift_fold_points['G7'] = [dt.Vector(x_g, y_gft, z_7),0]
        gift_fold_points['G8'] = [dt.Vector(x_g, y_gft, z_8),0]
        # x = H
        gift_fold_points['H1'] = [dt.Vector(x_h, y_gft, z_1),0]
        gift_fold_points['H2'] = [dt.Vector(x_h, y_gft, z_2),0]
        gift_fold_points['H3'] = [dt.Vector(x_h, y_gft, z_3),0]
        gift_fold_points['H4'] = [dt.Vector(x_h, y_gft, 0.0),0]
        gift_fold_points['H5'] = [dt.Vector(x_h, y_gft, z_5),0]
        gift_fold_points['H6'] = [dt.Vector(x_h, y_gft, z_6),0]
        gift_fold_points['H7'] = [dt.Vector(x_h, y_gft, z_7),0]
        gift_fold_points['H8'] = [dt.Vector(x_h, y_gft, z_8),0]
        # x = I
        gift_fold_points['I1'] = [dt.Vector(x_i, y_gft, z_1),0]
        gift_fold_points['I2'] = [dt.Vector(x_i, y_gft, z_2),0]
        gift_fold_points['I3'] = [dt.Vector(x_i, y_gft, z_3),0]
        gift_fold_points['I4'] = [dt.Vector(x_i, y_gft, 0.0),0]
        gift_fold_points['I5'] = [dt.Vector(x_i, y_gft, z_5),0]
        gift_fold_points['I6'] = [dt.Vector(x_i, y_gft, z_6),0]
        gift_fold_points['I7'] = [dt.Vector(x_i, y_gft, z_7),0]
        gift_fold_points['I8'] = [dt.Vector(x_i, y_gft, z_8),0]

        # calculate diagonal folds F4a, F4b, I4a, I4b
        gift_fold_points['I4a'] = [dt.Vector(x_i, y_gft, z_3),0]
        gift_fold_points['I4a'][0].z += gft_side_b
        gift_fold_points['I4b'] = [dt.Vector(x_i, y_gft, z_5),0]
        gift_fold_points['I4b'][0].z -= gft_side_b

        gift_fold_points['F4a'] = [dt.Vector(x_f, y_gft, z_3),0]
        gift_fold_points['F4a'][0].z += gft_side_b
        gift_fold_points['F4b'] = [dt.Vector(x_f, y_gft, z_5),0]
        gift_fold_points['F4b'][0].z -= gft_side_b

        # calculate intersecting points HI4, FG4
        if self.wrap_overlap:
            gift_fold_points['HI4'] = [dt.Vector(x_h, y_gft, 0.0),0]
            gift_fold_points['HI4'][0].x += gft_side_e / 2
            gift_fold_points['FG4'] = [dt.Vector(x_g, y_gft, 0.0),0]
            gift_fold_points['FG4'][0].x -= gft_side_e / 2

        # calculate diagonal folds F1a, I1a
        if not self.wrap_overlap:
            gift_fold_points['I1a'] = [dt.Vector(x_i, y_gft, z_2),0]
            gift_fold_points['I1a'][0].z -= gft_side_b
            gift_fold_points['F1a'] = [dt.Vector(x_f, y_gft, z_2),0]
            gift_fold_points['F1a'][0].z -= gft_side_b
        else:
            gift_fold_points['I1a'] = [dt.Vector(x_i, y_gft, z_1),0]
            gift_fold_points['I1a'][0].z += gft_side_b - gft_side_c
            gift_fold_points['I1a'][0].x -= gft_side_b - gft_side_c
            gift_fold_points['F1a'] = [dt.Vector(x_f, y_gft, z_1),0]
            gift_fold_points['F1a'][0].z += gft_side_b - gft_side_c
            gift_fold_points['F1a'][0].x += gft_side_b - gft_side_c

        # calculate diagonal folds F1b, I1b
        if self.wrap_overlap:
            gift_fold_points['I1b'] = [dt.Vector(x_i, y_gft, z_1),0]
            gift_fold_points['I1b'][0].z += (gft_side_b - gft_side_c) * 2
            gift_fold_points['F1b'] = [dt.Vector(x_f, y_gft, z_1),0]
            gift_fold_points['F1b'][0].z += (gft_side_b - gft_side_c) * 2

        # calculate diagonal folds F1c, I1c
        if self.wrap_overlap:
            gift_fold_points['I1c'] = [dt.Vector(x_i, y_gft, z_1),0]
            gift_fold_points['I1c'][0].x -= (gft_side_b - gft_side_c) * 2
            gift_fold_points['F1c'] = [dt.Vector(x_f, y_gft, z_1),0]
            gift_fold_points['F1c'][0].x += (gft_side_b - gft_side_c) * 2

        # calculate diagonal folds F7a, I7a
        if not self.wrap_overlap:
            gift_fold_points['I7a'] = [dt.Vector(x_i, y_gft, z_6),0]
            gift_fold_points['I7a'][0].z += gft_side_b
            gift_fold_points['F7a'] = [dt.Vector(x_f, y_gft, z_6),0]
            gift_fold_points['F7a'][0].z += gft_side_b
        else:
            gift_fold_points['I7a'] = [dt.Vector(x_i, y_gft, z_7),0]
            gift_fold_points['I7a'][0].z -= gft_side_b - gft_side_c
            gift_fold_points['F7a'] = [dt.Vector(x_f, y_gft, z_7),0]
            gift_fold_points['F7a'][0].z -= gft_side_b - gft_side_c

        # calculate diagonal folds F7b, I7b
        if self.wrap_overlap:
            gift_fold_points['I7b'] = [dt.Vector(x_i, y_gft, z_7),0]
            gift_fold_points['I7b'][0].x -= gft_side_b - gft_side_c
            gift_fold_points['F7b'] = [dt.Vector(x_f, y_gft, z_7),0]
            gift_fold_points['F7b'][0].x += gft_side_b - gft_side_c

        return gift_fold_points

    def createFoldingPlane(self, wrap_points):
        """
        Create polyplane that will fold up and serve as a wrap deformer
        """
        plane_name = "folding_plane_%s" % (self.wrap_id,)

        # Creates a basic polyplane
        wrap_fold_pln = pm.polyPlane(n=plane_name, sx=3, sy=6, ch=0)

        # Moves vertices to align them with folding pattern,
        wrap_fold_pln[0].vtx[0].setPosition(wrap_points['F8'][0])
        wrap_fold_pln[0].vtx[1].setPosition(wrap_points['G8'][0])
        wrap_fold_pln[0].vtx[2].setPosition(wrap_points['H8'][0])
        wrap_fold_pln[0].vtx[3].setPosition(wrap_points['I8'][0])
        wrap_fold_pln[0].vtx[4].setPosition(wrap_points['F7'][0])
        wrap_fold_pln[0].vtx[5].setPosition(wrap_points['G7'][0])
        wrap_fold_pln[0].vtx[6].setPosition(wrap_points['H7'][0])
        wrap_fold_pln[0].vtx[7].setPosition(wrap_points['I7'][0])
        wrap_fold_pln[0].vtx[8].setPosition(wrap_points['F6'][0])
        wrap_fold_pln[0].vtx[9].setPosition(wrap_points['G6'][0])
        wrap_fold_pln[0].vtx[10].setPosition(wrap_points['H6'][0])
        wrap_fold_pln[0].vtx[11].setPosition(wrap_points['I6'][0])
        wrap_fold_pln[0].vtx[12].setPosition(wrap_points['F5'][0])
        wrap_fold_pln[0].vtx[13].setPosition(wrap_points['G5'][0])
        wrap_fold_pln[0].vtx[14].setPosition(wrap_points['H5'][0])
        wrap_fold_pln[0].vtx[15].setPosition(wrap_points['I5'][0])
        wrap_fold_pln[0].vtx[16].setPosition(wrap_points['F3'][0])
        wrap_fold_pln[0].vtx[17].setPosition(wrap_points['G3'][0])
        wrap_fold_pln[0].vtx[18].setPosition(wrap_points['H3'][0])
        wrap_fold_pln[0].vtx[19].setPosition(wrap_points['I3'][0])
        wrap_fold_pln[0].vtx[20].setPosition(wrap_points['F2'][0])
        wrap_fold_pln[0].vtx[21].setPosition(wrap_points['G2'][0])
        wrap_fold_pln[0].vtx[22].setPosition(wrap_points['H2'][0])
        wrap_fold_pln[0].vtx[23].setPosition(wrap_points['I2'][0])
        wrap_fold_pln[0].vtx[24].setPosition(wrap_points['F1'][0])
        wrap_fold_pln[0].vtx[25].setPosition(wrap_points['G1'][0])
        wrap_fold_pln[0].vtx[26].setPosition(wrap_points['H1'][0])
        wrap_fold_pln[0].vtx[27].setPosition(wrap_points['I1'][0])

        # Models mid right diagonal folds
        if not self.wrap_overlap:
            temp_face = wrap_fold_pln[0].f[11]
            pm.polySubdivideFacet(temp_face, duv=1, dvv=3, sbm=1, ch=0)
            wrap_fold_pln[0].vtx[31].setPosition(wrap_points['H3'][0])
            wrap_fold_pln[0].vtx[30].setPosition(wrap_points['H5'][0])
            wrap_fold_pln[0].vtx[29].setPosition(wrap_points['I4a'][0])
            wrap_fold_pln[0].vtx[28].setPosition(wrap_points['I4b'][0])
            pm.polyMergeVertex(wrap_fold_pln[0].vtx[14:31], ch=0)
        else:
            temp_face = wrap_fold_pln[0].f[11]
            pm.polySubdivideFacet(temp_face, duv=2, dvv=3, sbm=1, ch=0)
            wrap_fold_pln[0].vtx[35].setPosition(wrap_points['HI4'][0])
            wrap_fold_pln[0].vtx[34].setPosition(wrap_points['HI4'][0])
            wrap_fold_pln[0].vtx[33].setPosition(wrap_points['H5'][0])
            wrap_fold_pln[0].vtx[32].setPosition(wrap_points['H3'][0])
            wrap_fold_pln[0].vtx[31].setPosition(wrap_points['H5'][0])
            wrap_fold_pln[0].vtx[30].setPosition(wrap_points['I4b'][0])
            wrap_fold_pln[0].vtx[29].setPosition(wrap_points['I4a'][0])
            wrap_fold_pln[0].vtx[28].setPosition(wrap_points['H3'][0])
            pm.polyMergeVertex(wrap_fold_pln[0].vtx[14:35], ch=0)

        # Models mid left diagonal folds
        if not self.wrap_overlap:
            temp_face = wrap_fold_pln[0].f[9]
            pm.polySubdivideFacet(temp_face, duv=1, dvv=3, sbm=1, ch=0)
            wrap_fold_pln[0].vtx[31].setPosition(wrap_points['G3'][0])
            wrap_fold_pln[0].vtx[30].setPosition(wrap_points['G5'][0])
            wrap_fold_pln[0].vtx[33].setPosition(wrap_points['F4a'][0])
            wrap_fold_pln[0].vtx[32].setPosition(wrap_points['F4b'][0])
            pm.polyMergeVertex(wrap_fold_pln[0].vtx[12:33], ch=0)
        else:
            temp_face = wrap_fold_pln[0].f[9]
            pm.polySubdivideFacet(temp_face, duv=2, dvv=3, sbm=1, ch=0)
            wrap_fold_pln[0].vtx[38].setPosition(wrap_points['FG4'][0])
            wrap_fold_pln[0].vtx[37].setPosition(wrap_points['FG4'][0])
            wrap_fold_pln[0].vtx[36].setPosition(wrap_points['G5'][0])
            wrap_fold_pln[0].vtx[35].setPosition(wrap_points['F4b'][0])
            wrap_fold_pln[0].vtx[34].setPosition(wrap_points['F4a'][0])
            wrap_fold_pln[0].vtx[33].setPosition(wrap_points['G3'][0])
            wrap_fold_pln[0].vtx[32].setPosition(wrap_points['G5'][0])
            wrap_fold_pln[0].vtx[31].setPosition(wrap_points['G3'][0])
            pm.polyMergeVertex(wrap_fold_pln[0].vtx[12:38], ch=0)

        # Models top right diagonal folds
        if not self.wrap_overlap:
            temp_face = wrap_fold_pln[0].f[17]
            pm.polySubdivideFacet(temp_face, duv=1, dvv=2, sbm=1, ch=0)
            wrap_fold_pln[0].vtx[33].setPosition(wrap_points['H2'][0])
            wrap_fold_pln[0].vtx[32].setPosition(wrap_points['I1a'][0])
            pm.polyMergeVertex(wrap_fold_pln[0].vtx[22:33], ch=0)
        else:
            temp_face = wrap_fold_pln[0].f[16]
            pm.polySubdivideFacet(temp_face, duv=2, dvv=2, sbm=1, ch=0)
            wrap_fold_pln[0].vtx[38].setPosition(wrap_points['I1a'][0])
            wrap_fold_pln[0].vtx[37].setPosition(wrap_points['H2'][0])
            wrap_fold_pln[0].vtx[35].setPosition(wrap_points['I1b'][0])
            wrap_fold_pln[0].vtx[34].setPosition(wrap_points['I1'][0])
            pm.polyMergeVertex(wrap_fold_pln[0].vtx[22:38], ch=0)
            pm.polyDelEdge(wrap_fold_pln[0].e[62], ch=0, cv=1)

        # Models top left diagonal folds
        if not self.wrap_overlap:
            temp_face = wrap_fold_pln[0].f[15]
            pm.polySubdivideFacet(temp_face, duv=1, dvv=2, sbm=1, ch=0)
            wrap_fold_pln[0].vtx[33].setPosition(wrap_points['G2'][0])
            wrap_fold_pln[0].vtx[34].setPosition(wrap_points['F1a'][0])
            pm.polyMergeVertex(wrap_fold_pln[0].vtx[21:33], ch=0)
        else:
            temp_face = wrap_fold_pln[0].f[14]
            pm.polySubdivideFacet(temp_face, duv=2, dvv=2, sbm=1, ch=0)
            wrap_fold_pln[0].vtx[40].setPosition(wrap_points['F1a'][0])
            wrap_fold_pln[0].vtx[39].setPosition(wrap_points['G2'][0])
            wrap_fold_pln[0].vtx[36].setPosition(wrap_points['F1'][0])
            wrap_fold_pln[0].vtx[38].setPosition(wrap_points['F1b'][0])
            pm.polyMergeVertex(wrap_fold_pln[0].vtx[20:40], ch=0)
            pm.polyDelEdge(wrap_fold_pln[0].e[65], ch=0, cv=1)

        # Models bottom right diagonal folds
        if not self.wrap_overlap:
            temp_face = wrap_fold_pln[0].f[5]
            pm.polySubdivideFacet(temp_face, duv=1, dvv=2, sbm=1, ch=0)
            wrap_fold_pln[0].vtx[35].setPosition(wrap_points['H6'][0])
            wrap_fold_pln[0].vtx[34].setPosition(wrap_points['I7a'][0])
            pm.polyMergeVertex(wrap_fold_pln[0].vtx[10:35], ch=0)
        else:
            temp_face = [wrap_fold_pln[0].f[2], wrap_fold_pln[0].f[5]]
            pm.polySubdivideFacet(temp_face, duv=2, dvv=1, sbm=1, ch=0)
            wrap_fold_pln[0].vtx[40].setPosition(wrap_points['I7b'][0])
            wrap_fold_pln[0].vtx[39].setPosition(wrap_points['I7b'][0])
            wrap_fold_pln[0].vtx[7].setPosition(wrap_points['I7a'][0])
            wrap_fold_pln[0].vtx[6].setPosition(wrap_points['H6'][0])
            temp_vertex = [wrap_fold_pln[0].vtx[2:3]]
            temp_vertex.append(wrap_fold_pln[0].vtx[6:7])
            temp_vertex.append(wrap_fold_pln[0].vtx[10:11])
            temp_vertex.append(wrap_fold_pln[0].vtx[38:40])
            pm.polyMergeVertex(temp_vertex, ch=0)
            pm.polyDelEdge(wrap_fold_pln[0].e[67], ch=0, cv=1)

        # Models bottom left diagonal folds
        if not self.wrap_overlap:
            temp_face = wrap_fold_pln[0].f[3]
            pm.polySubdivideFacet(temp_face, duv=1, dvv=2, sbm=1, ch=0)
            wrap_fold_pln[0].vtx[35].setPosition(wrap_points['G6'][0])
            wrap_fold_pln[0].vtx[36].setPosition(wrap_points['F7a'][0])
            pm.polyMergeVertex(wrap_fold_pln[0].vtx[9:35], ch=0)
        else:
            temp_face = [wrap_fold_pln[0].f[0], wrap_fold_pln[0].f[3]]
            pm.polySubdivideFacet(temp_face, duv=2, dvv=1, sbm=1, ch=0)
            wrap_fold_pln[0].vtx[40].setPosition(wrap_points['F7b'][0])
            wrap_fold_pln[0].vtx[39].setPosition(wrap_points['F7b'][0])
            wrap_fold_pln[0].vtx[4].setPosition(wrap_points['F7a'][0])
            wrap_fold_pln[0].vtx[5].setPosition(wrap_points['G6'][0])
            temp_vertex = [wrap_fold_pln[0].vtx[0:1]]
            temp_vertex.append(wrap_fold_pln[0].vtx[4:5])
            temp_vertex.append(wrap_fold_pln[0].vtx[8:9])
            temp_vertex.append(wrap_fold_pln[0].vtx[38:40])
            pm.polyMergeVertex(temp_vertex, ch=0)
            pm.polyDelEdge(wrap_fold_pln[0].e[67], ch=0, cv=1)

        # Model top diagonal fold points F1c, I1c
        if self.wrap_overlap:
            temp_face = [wrap_fold_pln[0].f[15], wrap_fold_pln[0].f[25]]
            pm.polySubdivideFacet(temp_face, duv=1, dvv=2, sbm=1, ch=0)
            wrap_fold_pln[0].vtx[41].setPosition(wrap_points['I1c'][0])
            wrap_fold_pln[0].vtx[40].setPosition(wrap_points['I1a'][0])
            wrap_fold_pln[0].vtx[39].setPosition(wrap_points['F1c'][0])
            wrap_fold_pln[0].vtx[38].setPosition(wrap_points['F1a'][0])
            pm.polyMergeVertex(wrap_fold_pln[0].vtx[33:41], ch=0)

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

    def getFoldingPivots(self, points):
        """
        Get pivots for the clusters controlling the folding.
        Returns them as a dict.
        Var names: 1U = 1st fold, upper quadrant, and so on
        """
        # 1st fold
        wrap_pivots = {'1U' : (points['I3'][0] + points['F3'][0]) / 2}
        wrap_pivots['1B'] = (points['I5'][0] + points['F5'][0]) / 2

        # 2nd fold
        wrap_pivots['2U'] = wrap_pivots['1U'] + 0 # add zero to copy not ref
        wrap_pivots['2U'].y += (points['F2'][0].z - points['F3'][0].z) * -1

        wrap_pivots['2B'] = wrap_pivots['2U'] + 0
        wrap_pivots['2B'].z *= -1

        # 3rd fold
        wrap_pivots['3UR'] = points['H3'][0] + 0
        temp = (points['I3'][0].x - points['H3'][0].x)/2
        wrap_pivots['3UR'].x += temp
        wrap_pivots['3UR'].z += temp
        wrap_pivots['3BR'] = points['H5'][0] + 0
        wrap_pivots['3BR'].x += temp
        wrap_pivots['3BR'].z -= temp
        wrap_pivots['3UL'] = points['G3'][0] + 0
        wrap_pivots['3UL'].x -= temp
        wrap_pivots['3UL'].z += temp
        wrap_pivots['3BL'] = points['G5'][0] + 0
        wrap_pivots['3BL'].x -= temp
        wrap_pivots['3BL'].z -= temp

        # 4th fold
        wrap_pivots['4UR'] = wrap_pivots['3UR'] + 0
        temp = wrap_pivots['2U'].y
        wrap_pivots['4UR'].y = temp
        wrap_pivots['4BR'] = wrap_pivots['3BR'] + 0
        wrap_pivots['4BR'].y = temp
        wrap_pivots['4UL'] = wrap_pivots['3UL'] + 0
        wrap_pivots['4UL'].y = temp
        wrap_pivots['4BL'] = wrap_pivots['3BL'] + 0
        wrap_pivots['4BL'].y = temp

        # Last two folds
        wrap_pivots['5R'] = points['H4'][0] + 0
        wrap_pivots['5R'].y = temp
        wrap_pivots['5L'] = points['G4'][0] + 0
        wrap_pivots['5L'].y = temp

        wrap_pivots['6R'] = points['H4'][0] + 0
        wrap_pivots['6L'] = points['G4'][0] + 0

        return wrap_pivots

    def createClusters(self, points, pivots):
        """
        Create clusters used for folding the plane.
        """
        # Create lists of rows of vertices to select
        vertices_x1 = [self.f_plane[0].vtx[points['F1'][1]]]
        vertices_x1.append(self.f_plane[0].vtx[points['G1'][1]])
        vertices_x1.append(self.f_plane[0].vtx[points['H1'][1]])
        vertices_x1.append(self.f_plane[0].vtx[points['I1'][1]])

        vertices_x2 = [self.f_plane[0].vtx[points['F2'][1]]]
        vertices_x2.append(self.f_plane[0].vtx[points['G2'][1]])
        vertices_x2.append(self.f_plane[0].vtx[points['H2'][1]])
        vertices_x2.append(self.f_plane[0].vtx[points['I2'][1]])

        vertices_x3 = [self.f_plane[0].vtx[points['F3'][1]]]
        vertices_x3.append(self.f_plane[0].vtx[points['G3'][1]])
        vertices_x3.append(self.f_plane[0].vtx[points['H3'][1]])
        vertices_x3.append(self.f_plane[0].vtx[points['I3'][1]])

        vertices_x5 = [self.f_plane[0].vtx[points['F5'][1]]]
        vertices_x5.append(self.f_plane[0].vtx[points['G5'][1]])
        vertices_x5.append(self.f_plane[0].vtx[points['H5'][1]])
        vertices_x5.append(self.f_plane[0].vtx[points['I5'][1]])

        vertices_x6 = [self.f_plane[0].vtx[points['F6'][1]]]
        vertices_x6.append(self.f_plane[0].vtx[points['G6'][1]])
        vertices_x6.append(self.f_plane[0].vtx[points['H6'][1]])
        vertices_x6.append(self.f_plane[0].vtx[points['I6'][1]])

        vertices_x7 = [self.f_plane[0].vtx[points['F7'][1]]]
        vertices_x7.append(self.f_plane[0].vtx[points['G7'][1]])
        vertices_x7.append(self.f_plane[0].vtx[points['H7'][1]])
        vertices_x7.append(self.f_plane[0].vtx[points['I7'][1]])

        if not self.wrap_overlap:
            vertices_x8 = [self.f_plane[0].vtx[points['F8'][1]]]
            vertices_x8.append(self.f_plane[0].vtx[points['G8'][1]])
            vertices_x8.append(self.f_plane[0].vtx[points['H8'][1]])
            vertices_x8.append(self.f_plane[0].vtx[points['I8'][1]])

        pm.select(None) # Deselect all

        # 1st fold
        # Upper
        vertices_1U = vertices_x1 + vertices_x2
        vertices_1U.append(self.f_plane[0].vtx[points['F1a'][1]])
        vertices_1U.append(self.f_plane[0].vtx[points['I1a'][1]])

        if self.wrap_overlap:
            vertices_1U.append(self.f_plane[0].vtx[points['F1b'][1]])
            vertices_1U.append(self.f_plane[0].vtx[points['I1b'][1]])
            vertices_1U.append(self.f_plane[0].vtx[points['F1c'][1]])
            vertices_1U.append(self.f_plane[0].vtx[points['I1c'][1]])

        pm.select(vertices_1U)
        self.cluster_1U = pm.cluster(n="gift_%s_cluster_1U" % (self.wrap_id,))
        self.cluster_1U[1].setRotatePivot(pivots['1U'])
        self.pivot_1U = pm.PyNode(self.cluster_1U[0].getWeightedNode())

        # Lower
        vertices_1B = vertices_x6 + vertices_x7
        if not self.wrap_overlap:
            vertices_1B += vertices_x8

        vertices_1B.append(self.f_plane[0].vtx[points['F7a'][1]])
        vertices_1B.append(self.f_plane[0].vtx[points['I7a'][1]])

        if self.wrap_overlap:
            vertices_1B.append(self.f_plane[0].vtx[points['F7b'][1]])
            vertices_1B.append(self.f_plane[0].vtx[points['I7b'][1]])

        pm.select(vertices_1B)
        self.cluster_1B = pm.cluster(n="gift_%s_cluster_1B" % (self.wrap_id,))
        self.cluster_1B[1].setRotatePivot(pivots['1B'])
        self.pivot_1B = pm.PyNode(self.cluster_1B[0].getWeightedNode())

        # 2nd fold
        # Upper
        vertices_2U = vertices_x1
        vertices_2U.append(self.f_plane[0].vtx[points['F1a'][1]])
        vertices_2U.append(self.f_plane[0].vtx[points['I1a'][1]])

        if self.wrap_overlap:
            vertices_2U.append(self.f_plane[0].vtx[points['F1b'][1]])
            vertices_2U.append(self.f_plane[0].vtx[points['I1b'][1]])
            vertices_2U.append(self.f_plane[0].vtx[points['F1c'][1]])
            vertices_2U.append(self.f_plane[0].vtx[points['I1c'][1]])

        pm.select(vertices_2U)
        self.cluster_2U = pm.cluster(n="gift_%s_cluster_2U" % (self.wrap_id,))
        self.cluster_2U[1].setRotatePivot(pivots['2U'])
        self.pivot_2U = pm.PyNode(self.cluster_2U[0].getWeightedNode())
        # Lower
        vertices_2B = vertices_x7
        if not self.wrap_overlap:
            vertices_2B += vertices_x8

        vertices_2B.append(self.f_plane[0].vtx[points['F7a'][1]])
        vertices_2B.append(self.f_plane[0].vtx[points['I7a'][1]])

        if self.wrap_overlap:
            vertices_2B.append(self.f_plane[0].vtx[points['F7b'][1]])
            vertices_2B.append(self.f_plane[0].vtx[points['I7b'][1]])

        pm.select(vertices_2B)
        self.cluster_2B = pm.cluster(n="gift_%s_cluster_2B" % (self.wrap_id,))
        self.cluster_2B[1].setRotatePivot(pivots['2B'])
        self.pivot_2B = pm.PyNode(self.cluster_2B[0].getWeightedNode())

        # 3rd fold
        # UR
        # Create custom weighted node,(a locator) as pivot
        self.pivot_3UR = [pm.spaceLocator(p=pivots['3UR'], n="gift_%s_pivot_3UR" % (self.wrap_id,)),None]
        self.pivot_3UR[1] = self.pivot_3UR[0].getShape()
        pm.select(self.pivot_3UR[0])
        self.pivot_3UR_group = pm.group(n="GRP_gift_%s_pivot_3UR" % (self.wrap_id,))
        self.pivot_3UR_group.rotateY.set(-45)
        self.pivot_3UR[0].centerPivots()
        # UR cluster
        vertices_3UR = [self.f_plane[0].vtx[points['I3'][1]]]
        if self.wrap_overlap:
            vertices_3UR.append(self.f_plane[0].vtx[points['I4a'][1]])
            vertices_3UR.append(self.f_plane[0].vtx[points['I4b'][1]])
        pm.select(vertices_3UR)
        self.cluster_3UR = pm.cluster(n="gift_%s_cluster_3UR" % (self.wrap_id,))
        pm.parent(self.cluster_3UR[1], self.pivot_3UR[0])
        self.cluster_3UR_pivot = pm.PyNode(self.cluster_3UR[0].getWeightedNode())

        # BR
        # Create custom weighted node,(a locator) as pivot
        self.pivot_3BR = [pm.spaceLocator(p=pivots['3BR'], n="gift_%s_pivot_3BR" % (self.wrap_id,)),None]
        self.pivot_3BR[1] = self.pivot_3BR[0].getShape()
        pm.select(self.pivot_3BR[0])
        self.pivot_3BR_group = pm.group(n="GRP_gift_%s_pivot_3BR" % (self.wrap_id,))
        self.pivot_3BR_group.rotate.set(180,225,0)
        self.pivot_3BR[0].centerPivots()
        # BR cluster
        vertices_3BR = [self.f_plane[0].vtx[points['I5'][1]]]
        if self.wrap_overlap:
            vertices_3BR.append(self.f_plane[0].vtx[points['I4a'][1]])
            vertices_3BR.append(self.f_plane[0].vtx[points['I4b'][1]])
        pm.select(vertices_3BR)
        self.cluster_3BR = pm.cluster(n="gift_%s_cluster_3BR" % (self.wrap_id,))
        pm.parent(self.cluster_3BR[1], self.pivot_3BR[0])

        # UL
        # Create custom weighted node,(a locator) as pivot
        self.pivot_3UL = [pm.spaceLocator(p=pivots['3UL'], n="gift_%s_pivot_3UL" % (self.wrap_id,)),None]
        self.pivot_3UL[1] = self.pivot_3UL[0].getShape()
        pm.select(self.pivot_3UL[0])
        self.pivot_3UL_group = pm.group(n="GRP_gift_%s_pivot_3UL" % (self.wrap_id,))
        self.pivot_3UL_group.rotateY.set(45)
        self.pivot_3UL[0].centerPivots()
        # UL cluster
        vertices_3UL = [self.f_plane[0].vtx[points['F3'][1]]]
        if self.wrap_overlap:
            vertices_3UL.append(self.f_plane[0].vtx[points['F4a'][1]])
            vertices_3UL.append(self.f_plane[0].vtx[points['F4b'][1]])
        pm.select(vertices_3UL)
        self.cluster_3UL = pm.cluster(n="gift_%s_cluster_3UL" % (self.wrap_id,))
        pm.parent(self.cluster_3UL[1], self.pivot_3UL[0])

        # BL
        # Create custom weighted node,(a locator) as pivot
        self.pivot_3BL = [pm.spaceLocator(p=pivots['3BL'], n="gift_%s_pivot_3BL" % (self.wrap_id,)),None]
        self.pivot_3BL[1] = self.pivot_3BL[0].getShape()
        pm.select(self.pivot_3BL[0])
        self.pivot_3BL_group = pm.group(n="GRP_gift_%s_pivot_3BL" % (self.wrap_id,))
        self.pivot_3BL_group.rotate.set(0,45,180)
        self.pivot_3BL[0].centerPivots()
        # BL cluster
        vertices_3BL = [self.f_plane[0].vtx[points['F5'][1]]]
        if self.wrap_overlap:
            vertices_3BL.append(self.f_plane[0].vtx[points['F4a'][1]])
            vertices_3BL.append(self.f_plane[0].vtx[points['F4b'][1]])
        pm.select(vertices_3BL)
        self.cluster_3BL = pm.cluster(n="gift_%s_cluster_3BL" % (self.wrap_id,))
        pm.parent(self.cluster_3BL[1], self.pivot_3BL[0])

        # 4th fold
        # UR
        # Create custom weighted node,(a locator) as pivot
        self.pivot_4UR = [pm.spaceLocator(p=pivots['4UR'], n="gift_%s_pivot_4UR" % (self.wrap_id,)),None]
        self.pivot_4UR[1] = self.pivot_4UR[0].getShape()
        pm.select(self.pivot_4UR[0])
        self.pivot_4UR_group = pm.group(n="GRP_gift_%s_pivot_4UR" % (self.wrap_id,))
        self.pivot_4UR_group.rotateY.set(135)
        self.pivot_4UR[0].centerPivots()
        # UR cluster
        vertices_4UR = [self.f_plane[0].vtx[points['I2'][1]]]
        if self.wrap_overlap:
            vertices_4UR.append(self.f_plane[0].vtx[points['I1b'][1]])
            vertices_4UR.append(self.f_plane[0].vtx[points['I7'][1]])
        pm.select(vertices_4UR)
        self.cluster_4UR = pm.cluster(n="gift_%s_cluster_4UR" % (self.wrap_id,))
        pm.parent(self.cluster_4UR[1], self.pivot_4UR[0])
        self.cluster_4UR_pivot = pm.PyNode(self.cluster_4UR[0].getWeightedNode())

        # BR
        # Create custom weighted node,(a locator) as pivot
        self.pivot_4BR = [pm.spaceLocator(p=pivots['4BR'], n="gift_%s_pivot_4BR" % (self.wrap_id,)),None]
        self.pivot_4BR[1] = self.pivot_4BR[0].getShape()
        pm.select(self.pivot_4BR[0])
        self.pivot_4BR_group = pm.group(n="GRP_gift_%s_pivot_4BR" % (self.wrap_id,))
        self.pivot_4BR_group.rotateY.set(45)
        self.pivot_4BR[0].centerPivots()
        # BR cluster
        vertices_4BR = [self.f_plane[0].vtx[points['I6'][1]]]
        if self.wrap_overlap:
            vertices_4BR.append(self.f_plane[0].vtx[points['I7a'][1]])
            vertices_4BR.append(self.f_plane[0].vtx[points['I1'][1]])
            vertices_4BR.append(self.f_plane[0].vtx[points['I7'][1]])

        pm.select(vertices_4BR)
        self.cluster_4BR = pm.cluster(n="gift_%s_cluster_4BR" % (self.wrap_id,))
        pm.parent(self.cluster_4BR[1], self.pivot_4BR[0])

        # UL
        # Create custom weighted node,(a locator) as pivot
        self.pivot_4UL = [pm.spaceLocator(p=pivots['4UL'], n="gift_%s_pivot_4UL" % (self.wrap_id,)),None]
        self.pivot_4UL[1] = self.pivot_4UL[0].getShape()
        pm.select(self.pivot_4UL[0])
        self.pivot_4UL_group = pm.group(n="GRP_gift_%s_pivot_4UL" % (self.wrap_id,))
        self.pivot_4UL_group.rotateY.set(225)
        self.pivot_4UL[0].centerPivots()
        # UL cluster
        vertices_4UL = [self.f_plane[0].vtx[points['F2'][1]]]
        if self.wrap_overlap:
            vertices_4UL.append(self.f_plane[0].vtx[points['F1b'][1]])
            vertices_4UL.append(self.f_plane[0].vtx[points['F7'][1]])
        pm.select(vertices_4UL)
        self.cluster_4UL = pm.cluster(n="gift_%s_cluster_4UL" % (self.wrap_id,))
        pm.parent(self.cluster_4UL[1], self.pivot_4UL[0])

        # BL
        # Create custom weighted node,(a locator) as pivot
        self.pivot_4BL = [pm.spaceLocator(p=pivots['4BL'], n="gift_%s_pivot_4BL" % (self.wrap_id,)),None]
        self.pivot_4BL[1] = self.pivot_4BL[0].getShape()
        pm.select(self.pivot_4BL[0])
        self.pivot_4BL_group = pm.group(n="GRP_gift_%s_pivot_4BL" % (self.wrap_id,))
        self.pivot_4BL_group.rotate.set(180,225,180)
        self.pivot_4BL[0].centerPivots()
        # BL cluster
        vertices_4BL = [self.f_plane[0].vtx[points['F6'][1]]]
        if self.wrap_overlap:
            vertices_4BL.append(self.f_plane[0].vtx[points['F7a'][1]])
            vertices_4BL.append(self.f_plane[0].vtx[points['F1'][1]])
            vertices_4BL.append(self.f_plane[0].vtx[points['F7'][1]])

        pm.select(vertices_4BL)
        self.cluster_4BL = pm.cluster(n="gift_%s_cluster_4BL" % (self.wrap_id,))
        pm.parent(self.cluster_4BL[1], self.pivot_4BL[0])

        # 6th fold
        # Right
        vertices_6R = [self.f_plane[0].vtx[points['I4a'][1]], self.f_plane[0].vtx[points['I4b'][1]]]
        if self.wrap_overlap:
            vertices_6R.append(self.f_plane[0].vtx[points['HI4'][1]])
        pm.select(vertices_6R)
        self.cluster_6R = pm.cluster(n="gift_%s_cluster_6R" % (self.wrap_id,))
        self.cluster_6R[1].setRotatePivot(pivots['6R'])
        self.pivot_6R = pm.PyNode(self.cluster_6R[0].getWeightedNode())
        # Left
        vertices_6L = [self.f_plane[0].vtx[points['F4a'][1]], self.f_plane[0].vtx[points['F4b'][1]]]
        if self.wrap_overlap:
            vertices_6L.append(self.f_plane[0].vtx[points['FG4'][1]])
        pm.select(vertices_6L)
        self.cluster_6L = pm.cluster(n="gift_%s_cluster_6L" % (self.wrap_id,))
        self.cluster_6L[1].setRotatePivot(pivots['6L'])
        self.pivot_6L = pm.PyNode(self.cluster_6L[0].getWeightedNode())

        # 6th fold
        # Right
        vertices_5R = [self.f_plane[0].vtx[points['I7'][1]]]
        vertices_5R.append(self.f_plane[0].vtx[points['I1'][1]])
        vertices_5R.append(self.f_plane[0].vtx[points['I1a'][1]])
        vertices_5R.append(self.f_plane[0].vtx[points['I7a'][1]])
        if not self.wrap_overlap:
            vertices_5R.append(self.f_plane[0].vtx[points['I8'][1]])
        else:
            vertices_5R.append(self.f_plane[0].vtx[points['I7b'][1]])
            vertices_5R.append(self.f_plane[0].vtx[points['I1b'][1]])
            vertices_5R.append(self.f_plane[0].vtx[points['I1c'][1]])

        pm.select(vertices_5R)
        self.cluster_5R = pm.cluster(n="gift_%s_cluster_5R" % (self.wrap_id,))
        self.cluster_5R[1].setRotatePivot(pivots['5R'])
        self.pivot_5R = pm.PyNode(self.cluster_5R[0].getWeightedNode())
        # Left
        vertices_5L = [self.f_plane[0].vtx[points['F7'][1]]]
        vertices_5L.append(self.f_plane[0].vtx[points['F1'][1]])
        vertices_5L.append(self.f_plane[0].vtx[points['F1a'][1]])
        vertices_5L.append(self.f_plane[0].vtx[points['F7a'][1]])
        if not self.wrap_overlap:
            vertices_5L.append(self.f_plane[0].vtx[points['F8'][1]])
        else:
            vertices_5L.append(self.f_plane[0].vtx[points['F7b'][1]])
            vertices_5L.append(self.f_plane[0].vtx[points['F1b'][1]])
            vertices_5L.append(self.f_plane[0].vtx[points['F1c'][1]])
        pm.select(vertices_5L)
        self.cluster_5L = pm.cluster(n="gift_%s_cluster_5L" % (self.wrap_id,))
        self.cluster_5L[1].setRotatePivot(pivots['5L'])
        self.pivot_5L = pm.PyNode(self.cluster_5L[0].getWeightedNode())

        # Parent to main cluster group
        pm.parent(self.cluster_1U[1], self.cluster_group)
        pm.parent(self.cluster_1B[1], self.cluster_group)
        pm.parent(self.cluster_2U[1], self.cluster_group)
        pm.parent(self.cluster_2B[1], self.cluster_group)
        pm.parent(self.pivot_3UR_group, self.cluster_group)
        pm.parent(self.pivot_3UL_group, self.cluster_group)
        pm.parent(self.pivot_3BR_group, self.cluster_group)
        pm.parent(self.pivot_3BL_group, self.cluster_group)
        pm.parent(self.pivot_4UR_group, self.cluster_group)
        pm.parent(self.pivot_4UL_group, self.cluster_group)
        pm.parent(self.pivot_4BR_group, self.cluster_group)
        pm.parent(self.pivot_4BL_group, self.cluster_group)
        pm.parent(self.cluster_5R[1], self.cluster_group)
        pm.parent(self.cluster_5L[1], self.cluster_group)
        pm.parent(self.cluster_6R[1], self.cluster_group)
        pm.parent(self.cluster_6L[1], self.cluster_group)

    def idGenerator(self, size=4, chars=string.ascii_uppercase + string.digits):
        "ID gen - Courtesy of a random google search"
        return ''.join(random.choice(chars) for x in range(size))

    def foldPaper(self, folds=17):
        """
        Wraps / unwraps gift by rotating clusters.
        folds = number of folds to perform
        """
        if folds >= 1:
            self.pivot_1B.rotateX.set(-90)
        if folds >= 2:
            self.pivot_2B.rotateX.set(-90)
        if folds >= 3:
            self.pivot_1U.rotateX.set(90)
        if folds >= 4:
            self.pivot_2U.rotateX.set(89.8)
        if folds >= 5:
            self.pivot_3UL[0].rotateX.set(178)
            self.pivot_3UL[0].translate.set(self.fold_fix,0,0) # fix
        if folds >= 6:
            self.pivot_3BL[0].rotateX.set(178)
            self.pivot_3BL[0].translate.set(self.fold_fix*-1,0,0)
        if folds >= 7:
            self.pivot_3UR[0].rotateX.set(178)
            self.pivot_3UR[0].translate.set(self.fold_fix*-1,0,0)
        if folds >= 8:
            self.pivot_3BR[0].rotateX.set(178)
            self.pivot_3BR[0].translate.set(self.fold_fix,0,0)
        if folds >= 9:
            self.pivot_4UL[0].rotateX.set(178)
        if folds >= 10:
            self.pivot_4BL[0].rotateX.set(178)
        if folds >= 11:
            self.pivot_4UR[0].rotateX.set(178)
        if folds >= 12:
            self.pivot_4BR[0].rotateX.set(178)
        if folds >= 13:
            self.pivot_5L.rotateZ.set(86)
        if folds >= 14:
            self.pivot_5R.rotateZ.set(-86)
        if folds >= 15:
            self.pivot_6L.rotateZ.set(-84)
        if folds >= 16:
            self.pivot_6R.rotateZ.set(84)

        if folds == 0:
            self.pivot_1B.rotate.set(0,0,0)
        if folds < 2:
            self.pivot_2B.rotate.set(0,0,0)
        if folds < 3:
            self.pivot_1U.rotate.set(0,0,0)
        if folds < 4:
            self.pivot_2U.rotate.set(0,0,0)
        if folds < 5:
            self.pivot_3UL[0].rotate.set(0,0,0)
            self.pivot_3UL[0].translate.set(0,0,0)
        if folds < 6:
            self.pivot_3BL[0].rotate.set(0,0,0)
            self.pivot_3BL[0].translate.set(0,0,0)
        if folds < 7:
            self.pivot_3UR[0].rotate.set(0,0,0)
        if folds < 8:
            self.pivot_3BR[0].rotate.set(0,0,0)
        if folds < 9:
            self.pivot_4UL[0].rotate.set(0,0,0)
        if folds < 10:
            self.pivot_4BL[0].rotate.set(0,0,0)
        if folds < 11:
            self.pivot_4UR[0].rotate.set(0,0,0)
        if folds < 12:
            self.pivot_4BR[0].rotate.set(0,0,0)
        if folds < 13:
            self.pivot_5L.rotate.set(0,0,0)
        if folds < 14:
            self.pivot_5R.rotate.set(0,0,0)
        if folds < 15:
            self.pivot_6L.rotate.set(0,0,0)
        if folds < 16:
            self.pivot_6R.rotate.set(0,0,0)

    def setDrivenKeys(self, anim=0):
        """
        Connect the wrapping to the animation attribute of the control handle.
        """
        self.foldPaper(0)
        self.ctrl_handle[0].animation.set(0)
        pm.setDrivenKeyframe(self.pivot_1B.rotateX, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(1)
        self.foldPaper(1)
        pm.setDrivenKeyframe(self.pivot_1B.rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_2B.rotateX, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(2)
        self.foldPaper(2)
        pm.setDrivenKeyframe(self.pivot_2B.rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_1U.rotateX, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(3)
        self.foldPaper(3)
        pm.setDrivenKeyframe(self.pivot_1U.rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_2U.rotateX, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(4)
        self.foldPaper(4)
        pm.setDrivenKeyframe(self.pivot_2U.rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_3UL[0].rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_3UL[0].translateX, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(4.5)
        self.foldPaper(5)
        pm.setDrivenKeyframe(self.pivot_3UL[0].rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_3UL[0].translateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_3BL[0].rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_3BL[0].translateX, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(5)
        self.foldPaper(6)
        pm.setDrivenKeyframe(self.pivot_3BL[0].rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_3BL[0].translateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_3UR[0].rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_3UR[0].translateX, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(5.5)
        self.foldPaper(7)
        pm.setDrivenKeyframe(self.pivot_3UR[0].rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_3UR[0].translateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_3BR[0].rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_3BR[0].translateX, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(6)
        self.foldPaper(8)
        pm.setDrivenKeyframe(self.pivot_3BR[0].rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_3BR[0].translateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_4UL[0].rotateX, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(6.5)
        self.foldPaper(9)
        pm.setDrivenKeyframe(self.pivot_4UL[0].rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_4BL[0].rotateX, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(7)
        self.foldPaper(10)
        pm.setDrivenKeyframe(self.pivot_4BL[0].rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_4UR[0].rotateX, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(7.5)
        self.foldPaper(11)
        pm.setDrivenKeyframe(self.pivot_4UR[0].rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_4BR[0].rotateX, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(8)
        self.foldPaper(12)
        pm.setDrivenKeyframe(self.pivot_4BR[0].rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_5L.rotateZ, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(8.5)
        self.foldPaper(13)
        pm.setDrivenKeyframe(self.pivot_5L.rotateZ, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_5R.rotateZ, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(9)
        self.foldPaper(14)
        pm.setDrivenKeyframe(self.pivot_5R.rotateZ, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_6L.rotateZ, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(9.5)
        self.foldPaper(15)
        pm.setDrivenKeyframe(self.pivot_6L.rotateZ, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.pivot_6R.rotateZ, cd=self.ctrl_handle[0].animation)


        self.ctrl_handle[0].animation.set(10)
        self.foldPaper(16)

        bbox_minmax = self.wrap_gift.boundingBoxMax.get() - self.wrap_gift.boundingBoxMin.get()

        self.gift_group.translateY.set(0)
        self.gift_group.rotateX.set(0)
        self.gift_group.centerPivots()

        pm.setDrivenKeyframe(self.pivot_6R.rotateZ, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.gift_group.rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.gift_group.translateY, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(10.5)
        self.gift_group.translateY.set(bbox_minmax[1]/2)
        pm.setDrivenKeyframe(self.gift_group.translateY, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(11)
        self.gift_group.rotateX.set(180)
        self.gift_group.translateY.set(0)
        self.tieRibbon(0)
        pm.setDrivenKeyframe(self.gift_group.rotateX, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.gift_group.translateY, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.ribbons['1U'][2].maxValue, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.ribbons['1D'][2].maxValue, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(12)
        self.tieRibbon(1)
        pm.setDrivenKeyframe(self.ribbons['1U'][2].maxValue, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.ribbons['1D'][2].maxValue, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.ribbons['2L'][2].maxValue, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.ribbons['2R'][2].maxValue, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(13)
        self.tieRibbon(2)
        pm.setDrivenKeyframe(self.ribbons['2L'][2].maxValue, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.ribbons['2R'][2].maxValue, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.ribbons['3L'][2].maxValue, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.ribbons['3R'][2].maxValue, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(14)
        self.tieRibbon(3)
        pm.setDrivenKeyframe(self.ribbons['3L'][2].maxValue, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.ribbons['3R'][2].maxValue, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.ribbons['4'][2].maxValue, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(15)
        self.tieRibbon(4)
        pm.setDrivenKeyframe(self.ribbons['3L'][2].maxValue, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.ribbons['3R'][2].maxValue, cd=self.ctrl_handle[0].animation)
        pm.setDrivenKeyframe(self.ribbons['4'][2].maxValue, cd=self.ctrl_handle[0].animation)

        self.ctrl_handle[0].animation.set(anim)

    def setAnimation(self, anim_s=None, anim_e=None):
        if anim_s is None:
            anim_s = self.animation_start
        else:
            self.animation_start = anim_s
            self.ctrl_handle[0].animation_start.set(self.animation_start)
        if anim_e is None :
            anim_e = self.animation_end
        else:
            self.animation_end = anim_e
            self.ctrl_handle[0].animation_end.set(self.animation_end)

        pm.cutKey(self.ctrl_handle[0], at='animation', cl=True)

        if not anim_s == anim_e:
            pm.setKeyframe(self.ctrl_handle[0], at='animation', v=0,
                           t=anim_s)
            pm.setKeyframe(self.ctrl_handle[0], at='animation', v=15,
                           t=anim_e)

    def createPaper(self, plane, thickness):
        """
        Creates a wrapping paper mesh which is then controlled by the
        folding plane using a wrap deformer.
        """
        paper = pm.duplicate(plane, name="wrap_paper_%s" % self.wrap_id)
        # Make hipoly
        pm.polyBevel(paper, o=0.005, ch=0)
        pm.polySubdivideFacet(paper, dv=1, dvv=1, sbm=0, ch=0, m=1)
        #pm.polySmooth(paper, mth=0, dv=1, ch=0, kt=False)
        paper[0].rotatePivot.translate.set(0,thickness/2,0)
        paper[0].translateY.set(thickness/2)
        pm.polyExtrudeFacet(paper, translateY=(thickness * -1), ch=0)
        verts = pm.polyEvaluate(paper[0], f=True) - 1
        evalthis = 'polyProjection -ch 0 -type Planar -ibd on -kir  -md y ' + str(paper[0]) + '.f[0:' + str(verts) +']'

        mel.eval(evalthis) # UV planar map

        # Create wrap deformer
        pm.select(None)
        pm.select(paper, plane)
        mc.CreateWrap() # And in pymel?
        return paper

    def getRibbonPoints(self, side_w, side_h, side_d, side_a, thickness, r_thickness, r_width):
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
        # x, y, z from origin
        y_pos = side_h + (r_thickness / 3)
        x_pos = (side_w / 2) + (r_thickness + thickness)
        z_pos = (side_d / 2) + (r_thickness / 3)
        edg_m = thickness / 2 # edge margin
        mid_c = 0.5 # mid point coefficient
        end_m = 2 * thickness # end point margin
        x_pos_m = thickness # width (L and R) margin
        x_edge = (side_a / 2) #+ thickness + (r_thickness / 2)


        # Mid points
        r_points = {'U' : [dt.Vector(0, y_pos, 0), 0]}
        r_points['D'] = [dt.Vector(0, 0, 0), 0]
        r_points['L'] = [dt.Vector(0 - x_pos, side_h / 2, 0), 0]
        r_points['R'] = [dt.Vector(x_pos, side_h / 2, 0), 0]
        r_points['F'] = [dt.Vector(0, side_d / 2, z_pos), 0]
        r_points['B'] = [dt.Vector(0, side_d / 2, 0 - z_pos), 0]

        # Upper side
        r_points['UL'] = [r_points['U'][0] + 0, 0] # Copy not reference
        r_points['UL'][0].x = 0 - x_edge
        r_points['ULmid'] = [r_points['UL'][0] + 0, 0]
        r_points['ULmid'][0].x *= mid_c
        r_points['ULend'] = [r_points['UL'][0] + 0, 0]
        r_points['ULend'][0].x += end_m * 2

        r_points['UR'] = [r_points['U'][0] + 0, 0]
        r_points['UR'][0].x = x_edge
        r_points['URmid'] = [r_points['UR'][0] + 0, 0]
        r_points['URmid'][0].x *= mid_c
        r_points['URend'] = [r_points['UR'][0] + 0, 0]
        r_points['URend'][0].x -= end_m * 2

        r_points['UB'] = [r_points['U'][0] + 0, 0]
        r_points['UB'][0].z = r_points['B'][0].z + edg_m
        r_points['UBmid'] = [r_points['UB'][0] + 0, 0]
        r_points['UBmid'][0].z *= mid_c
        r_points['UBend'] = [r_points['UB'][0] + 0, 0]
        r_points['UBend'][0].z += end_m

        r_points['UF'] = [r_points['U'][0] + 0, 0]
        r_points['UF'][0].z = r_points['F'][0].z - edg_m
        r_points['UFmid'] = [r_points['UF'][0] + 0, 0]
        r_points['UFmid'][0].z *= mid_c
        r_points['UFend'] = [r_points['UF'][0] + 0, 0]
        r_points['UFend'][0].z -= end_m

        # Downside
        r_points['DL'] = [r_points['D'][0] + 0, 0]
        r_points['DL'][0].x = 0 - x_edge
        r_points['DLmid'] = [r_points['DL'][0] + 0, 0]
        r_points['DLmid'][0].x *= mid_c
        r_points['DLend'] = [r_points['DL'][0] + 0, 0]
        r_points['DLend'][0].x += end_m * 2

        r_points['DR'] = [r_points['D'][0] + 0, 0]
        r_points['DR'][0].x = x_edge
        r_points['DRmid'] = [r_points['DR'][0] + 0, 0]
        r_points['DRmid'][0].x *= mid_c
        r_points['DRend'] = [r_points['DR'][0] + 0, 0]
        r_points['DRend'][0].x -= end_m * 2

        r_points['DB'] = [r_points['D'][0] + 0, 0]
        r_points['DB'][0].z = r_points['B'][0].z + edg_m
        r_points['DBmid'] = [r_points['DB'][0] + 0, 0]
        r_points['DBmid'][0].z *= mid_c
        r_points['DBend'] = [r_points['DB'][0] + 0, 0]
        r_points['DBend'][0].z += end_m

        r_points['DF'] = [r_points['D'][0] + 0, 0]
        r_points['DF'][0].z = r_points['F'][0].z - edg_m
        r_points['DFmid'] = [r_points['DF'][0] + 0, 0]
        r_points['DFmid'][0].z *= mid_c
        r_points['DFend'] = [r_points['DF'][0] + 0, 0]
        r_points['DFend'][0].z -= end_m

        # Left side
        r_points['LU'] = [r_points['L'][0] + 0, 0]
        r_points['LU'][0].y = r_points['U'][0].y - edg_m
        r_points['LU'][0].x = 0 - (x_edge + x_pos_m)
        r_points['LUmid'] = [r_points['L'][0] + 0, 0]
        r_points['LUmid'][0].y += y_pos / 4
        r_points['LUmid'][0].x += (r_points['LU'][0].x  - r_points['L'][0].x) / 2
        r_points['LUend'] = [r_points['LU'][0] + 0, 0]
        r_points['LUend'][0].y -= end_m
        r_points['LUend'][0].x -= x_pos_m

        r_points['LD'] = [r_points['L'][0] + 0, 0]
        r_points['LD'][0].y = r_points['D'][0].y + edg_m
        r_points['LD'][0].x = 0 - (x_edge + x_pos_m)
        r_points['LDmid'] = [r_points['L'][0] + 0, 0]
        r_points['LDmid'][0].y -= y_pos / 3
        r_points['LDend'] = [r_points['LD'][0] + 0, 0]
        r_points['LDend'][0].y += end_m
        r_points['LDend'][0].x -= x_pos_m

        r_points['LB'] = [r_points['L'][0] + 0, 0]
        r_points['LB'][0].z = r_points['B'][0].z + edg_m
        r_points['LBmid'] = [r_points['LB'][0] + 0, 0]
        r_points['LBmid'][0].z *= mid_c
        r_points['LBend'] = [r_points['LB'][0] + 0, 0]
        r_points['LBend'][0].z += end_m

        r_points['LF'] = [r_points['L'][0] + 0, 0]
        r_points['LF'][0].z = r_points['F'][0].z - edg_m
        r_points['LFmid'] = [r_points['LF'][0] + 0, 0]
        r_points['LFmid'][0].z *= mid_c
        r_points['LFend'] = [r_points['LF'][0] + 0, 0]
        r_points['LFend'][0].z -= end_m

        # Right side
        r_points['RU'] = [r_points['R'][0] + 0, 0]
        r_points['RU'][0].y = r_points['U'][0].y - edg_m
        r_points['RU'][0].x = x_edge + x_pos_m
        r_points['RUmid'] = [r_points['R'][0] + 0, 0]
        r_points['RUmid'][0].y += y_pos / 4
        r_points['RUmid'][0].x -= (r_points['R'][0].x  - r_points['RU'][0].x) / 2
        r_points['RUend'] = [r_points['RU'][0] + 0, 0]
        r_points['RUend'][0].y -= end_m
        r_points['RUend'][0].x += x_pos_m

        r_points['RD'] = [r_points['R'][0] + 0, 0]
        r_points['RD'][0].y = r_points['D'][0].y + edg_m
        r_points['RD'][0].x = x_edge + x_pos_m
        r_points['RDmid'] = [r_points['R'][0] + 0, 0]
        r_points['RDmid'][0].y -= y_pos / 3
        r_points['RDend'] = [r_points['RD'][0] + 0, 0]
        r_points['RDend'][0].y += end_m
        r_points['RDend'][0].x += x_pos_m

        r_points['RB'] = [r_points['R'][0] + 0, 0]
        r_points['RB'][0].z = r_points['B'][0].z + edg_m
        r_points['RBmid'] = [r_points['RB'][0] + 0, 0]
        r_points['RBmid'][0].z *= mid_c
        r_points['RBend'] = [r_points['RB'][0] + 0, 0]
        r_points['RBend'][0].z += end_m

        r_points['RF'] = [r_points['R'][0] + 0, 0]
        r_points['RF'][0].z = r_points['F'][0].z - edg_m
        r_points['RFmid'] = [r_points['RF'][0] + 0, 0]
        r_points['RFmid'][0].z *= mid_c
        r_points['RFend'] = [r_points['RF'][0] + 0, 0]
        r_points['RFend'][0].z -= end_m

        # Back side
        r_points['BU'] = [r_points['B'][0] + 0, 0]
        r_points['BU'][0].y = r_points['U'][0].y - edg_m
        r_points['BUmid'] = [r_points['BU'][0] + 0, 0]
        r_points['BUmid'][0].y -= y_pos / 4
        r_points['BUend'] = [r_points['BU'][0] + 0, 0]
        r_points['BUend'][0].y -= end_m

        r_points['BD'] = [r_points['B'][0] + 0, 0]
        r_points['BD'][0].y = r_points['D'][0].y + edg_m
        r_points['BDmid'] = [r_points['BD'][0] + 0, 0]
        r_points['BDmid'][0].y += y_pos / 4
        r_points['BDend'] = [r_points['BD'][0] + 0, 0]
        r_points['BDend'][0].y += end_m

        r_points['BL'] = [r_points['B'][0] + 0, 0]
        r_points['BL'][0].x = r_points['L'][0].x + edg_m
        r_points['BLmid'] = [r_points['BL'][0] + 0, 0]
        r_points['BLmid'][0].x *= mid_c
        r_points['BLend'] = [r_points['BL'][0] + 0, 0]
        r_points['BLend'][0].x += end_m

        r_points['BR'] = [r_points['B'][0] + 0, 0]
        r_points['BR'][0].x = r_points['R'][0].x - edg_m
        r_points['BRmid'] = [r_points['BR'][0] + 0, 0]
        r_points['BRmid'][0].x *= mid_c
        r_points['BRend'] = [r_points['BR'][0] + 0, 0]
        r_points['BRend'][0].x -= end_m

        # Front side
        r_points['FU'] = [r_points['F'][0] + 0, 0]
        r_points['FU'][0].y = r_points['U'][0].y - edg_m
        r_points['FUmid'] = [r_points['FU'][0] + 0, 0]
        r_points['FUmid'][0].y -= y_pos / 4
        r_points['FUend'] = [r_points['FU'][0] + 0, 0]
        r_points['FUend'][0].y -= end_m

        r_points['FD'] = [r_points['F'][0] + 0, 0]
        r_points['FD'][0].y = r_points['D'][0].y + edg_m
        r_points['FDmid'] = [r_points['FD'][0] + 0, 0]
        r_points['FDmid'][0].y += y_pos / 4
        r_points['FDend'] = [r_points['FD'][0] + 0, 0]
        r_points['FDend'][0].y += end_m

        r_points['FL'] = [r_points['F'][0] + 0, 0]
        r_points['FL'][0].x = r_points['L'][0].x + edg_m
        r_points['FLmid'] = [r_points['FL'][0] + 0, 0]
        r_points['FLmid'][0].x *= mid_c
        r_points['FLend'] = [r_points['FL'][0] + 0, 0]
        r_points['FLend'][0].x += end_m

        r_points['FR'] = [r_points['F'][0] + 0, 0]
        r_points['FR'][0].x = r_points['R'][0].y - edg_m
        r_points['FRmid'] = [r_points['FR'][0] + 0, 0]
        r_points['FRmid'][0].x *= mid_c
        r_points['FRend'] = [r_points['FR'][0] + 0, 0]
        r_points['FRend'][0].x -= end_m

        # Bow

        loop_w = side_w / 3
        loop_h = side_w / 4

        # Left loop
        r_points['bow_L1'] = [r_points['U'][0] + 0, 0]
        r_points['bow_L2'] = [r_points['U'][0] + 0, 0]
        r_points['bow_L2'][0].x = 0 - loop_w
        r_points['bow_L2'][0].y += r_thickness
        r_points['bow_L3'] = [r_points['bow_L2'][0] + 0, 0]
        r_points['bow_L3'][0].y += loop_h / 2
        r_points['bow_L3'][0].x -= r_width / 2
        r_points['bow_L4'] = [r_points['bow_L2'][0] + 0, 0]
        r_points['bow_L4'][0].y += loop_h
        r_points['bow_L4'][0].x += r_width * 0.25
        r_points['bow_L5'] = [r_points['bow_L1'][0] + 0, 0]
        r_points['bow_L5'][0].y += r_thickness
        r_points['bow_L5'][0].x -= r_width * 0.85
        r_points['bow_L6'] = [r_points['bow_L5'][0] + 0, 0]
        r_points['bow_L6'][0].x += r_width / 2
        r_points['bow_L7'] = [r_points['bow_L1'][0] + 0, 0]
        r_points['bow_L7'][0].y += r_thickness * 0.5

        # Right loop
        r_points['bow_R1'] = [r_points['U'][0] + 0, 0]
        r_points['bow_R2'] = [r_points['U'][0] + 0, 0]
        r_points['bow_R2'][0].x = loop_w
        r_points['bow_R2'][0].y += r_thickness
        r_points['bow_R3'] = [r_points['bow_R2'][0] + 0, 0]
        r_points['bow_R3'][0].y += loop_h / 2
        r_points['bow_R3'][0].x += r_width / 2
        r_points['bow_R4'] = [r_points['bow_R2'][0] + 0, 0]
        r_points['bow_R4'][0].y += loop_h
        r_points['bow_R4'][0].x -= r_width * 0.25
        r_points['bow_R5'] = [r_points['bow_R1'][0] + 0, 0]
        r_points['bow_R5'][0].y += r_thickness
        r_points['bow_R5'][0].x += r_width * 0.85
        r_points['bow_R6'] = [r_points['bow_R5'][0] + 0, 0]
        r_points['bow_R6'][0].x -= r_width / 2
        r_points['bow_R7'] = [r_points['bow_R1'][0] + 0, 0]
        r_points['bow_R7'][0].y += r_thickness * 0.5

        # Knot
        r_points['knot_1'] = [r_points['U'][0] + 0, 0]
        r_points['knot_1'][0].z += r_width / 2
        r_points['knot_2'] = [r_points['knot_1'][0] + 0, 0]
        r_points['knot_2'][0].y += r_thickness * 2
        r_points['knot_3'] = [r_points['U'][0] + 0, 0]
        r_points['knot_3'][0].y += r_thickness * 2
        r_points['knot_4'] = [r_points['knot_2'][0] + 0, 0]
        r_points['knot_4'][0].z -= r_width*1.5
        r_points['knot_4'][0].y += r_width*0.15
        r_points['knot_5'] = [r_points['U'][0] + 0, 0]
        r_points['knot_5'][0].z -= r_width / 2

        # Ends
        # Left end
        r_points['end_L1'] = [r_points['U'][0] + 0, 0]
        r_points['end_L1'][0].z += r_width / 2

        return r_points

    def getRibbonWidth(self, r_size, side_d, side_e):
        """Calcuclate width of ribbon"""
        if side_d > side_e :
            smallest_side = side_e
        else:
            smallest_side = side_d

        r_width_s = smallest_side * 0.09

        if r_size == 'L':
            r_width = r_width_s * 4.0
        if r_size == 'M':
            r_width = r_width_s * 2.5
        if r_size == 'S':
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
        crv_list_1U = [r_points['U'][0]]
        crv_list_1U.append(r_points['UBmid'][0])
        crv_list_1U.append(r_points['UBend'][0])
        crv_list_1U.append(r_points['UB'][0])
        crv_list_1U.append(r_points['BU'][0])
        crv_list_1U.append(r_points['BUend'][0])
        crv_list_1U.append(r_points['BUmid'][0])
        crv_list_1U.append(r_points['B'][0])
        crv_list_1U.append(r_points['BDmid'][0])
        crv_list_1U.append(r_points['BDend'][0])
        crv_list_1U.append(r_points['BD'][0])
        crv_list_1U.append(r_points['DB'][0])
        crv_list_1U.append(r_points['DBend'][0])
        crv_list_1U.append(r_points['DBmid'][0])
        crv_list_1U.append(r_points['D'][0])

        crv_list_1D = [r_points['U'][0]]
        crv_list_1D.append(r_points['UFmid'][0])
        crv_list_1D.append(r_points['UFend'][0])
        crv_list_1D.append(r_points['UF'][0])
        crv_list_1D.append(r_points['FU'][0])
        crv_list_1D.append(r_points['FUend'][0])
        crv_list_1D.append(r_points['FUmid'][0])
        crv_list_1D.append(r_points['F'][0])
        crv_list_1D.append(r_points['FDmid'][0])
        crv_list_1D.append(r_points['FDend'][0])
        crv_list_1D.append(r_points['FD'][0])
        crv_list_1D.append(r_points['DF'][0])
        crv_list_1D.append(r_points['DFend'][0])
        crv_list_1D.append(r_points['DFmid'][0])
        crv_list_1D.append(r_points['D'][0])

        crv_list_2L = [r_points['D'][0]]
        crv_list_2L.append(r_points['DLmid'][0])
        crv_list_2L.append(r_points['DLend'][0])
        crv_list_2L.append(r_points['DL'][0])
        crv_list_2L.append(r_points['LD'][0])
        crv_list_2L.append(r_points['LDend'][0])
        crv_list_2L.append(r_points['LDmid'][0])
        crv_list_2L.append(r_points['L'][0])
        crv_list_2L.append(r_points['LUmid'][0])
        crv_list_2L.append(r_points['LUend'][0])
        crv_list_2L.append(r_points['LU'][0])
        crv_list_2L.append(r_points['UL'][0])
        crv_list_2L.append(r_points['ULend'][0])
        crv_list_2L.append(r_points['ULmid'][0])
        crv_list_2L.append(r_points['U'][0])

        crv_list_2R = [r_points['D'][0]]
        crv_list_2R.append(r_points['DRmid'][0])
        crv_list_2R.append(r_points['DRend'][0])
        crv_list_2R.append(r_points['DR'][0])
        crv_list_2R.append(r_points['RD'][0])
        crv_list_2R.append(r_points['RDend'][0])
        crv_list_2R.append(r_points['RDmid'][0])
        crv_list_2R.append(r_points['R'][0])
        crv_list_2R.append(r_points['RUmid'][0])
        crv_list_2R.append(r_points['RUend'][0])
        crv_list_2R.append(r_points['RU'][0])
        crv_list_2R.append(r_points['UR'][0])
        crv_list_2R.append(r_points['URend'][0])
        crv_list_2R.append(r_points['URmid'][0])
        crv_list_2R.append(r_points['U'][0])
    
        crv_list_3L = [r_points['bow_L1'][0]]
        crv_list_3L.append(r_points['bow_L2'][0])
        crv_list_3L.append(r_points['bow_L3'][0])
        crv_list_3L.append(r_points['bow_L4'][0])
        crv_list_3L.append(r_points['bow_L5'][0])
        crv_list_3L.append(r_points['bow_L6'][0])
        crv_list_3L.append(r_points['bow_L7'][0])

        crv_list_3R = [r_points['bow_R1'][0]]
        crv_list_3R.append(r_points['bow_R2'][0])
        crv_list_3R.append(r_points['bow_R3'][0])
        crv_list_3R.append(r_points['bow_R4'][0])
        crv_list_3R.append(r_points['bow_R5'][0])
        crv_list_3R.append(r_points['bow_R6'][0])

        crv_list_4 = [r_points['knot_1'][0]]
        crv_list_4.append(r_points['knot_2'][0])
        crv_list_4.append(r_points['knot_3'][0])
        crv_list_4.append(r_points['knot_4'][0])
        crv_list_4.append(r_points['knot_5'][0])

        curve_1U = pm.curve(p=crv_list_1U, n="ribbon_1U_crv_%s" % (self.wrap_id,))
        curve_1D = pm.curve(p=crv_list_1D, n="ribbon_1D_crv_%s" % (self.wrap_id,))
        curve_2L = pm.curve(p=crv_list_2L, n="ribbon_2L_crv_%s" % (self.wrap_id,))
        curve_2R = pm.curve(p=crv_list_2R, n="ribbon_2R_crv_%s" % (self.wrap_id,))
        curve_3L = pm.curve(p=crv_list_3L, n="ribbon_3L_crv_%s" % (self.wrap_id,))
        curve_3R = pm.curve(p=crv_list_3R, n="ribbon_3R_crv_%s" % (self.wrap_id,))
        curve_4 = pm.curve(p=crv_list_4, n="ribbon_4_crv_%s" % (self.wrap_id,))

        curves = [curve_1U, curve_1D]

        # Ribbon profile shape
        r_prof_1 = pm.circle(n="ribbon_1_profile_" + self.wrap_id)
        r_prof_1[0].cv[0].setPosition([r_width/2,r_thickness/2,0])
        r_prof_1[0].cv[6].setPosition([r_width/2,0,0])
        r_prof_1[0].cv[7].setPosition([r_width/2,0-(r_thickness/2),0])
        r_prof_1[0].cv[1].setPosition([0,r_thickness/2,0])
        r_prof_1[0].cv[2].setPosition([0-(r_width/2),r_thickness/2,0])
        r_prof_1[0].cv[3].setPosition([0-(r_width/2),0,0])
        r_prof_1[0].cv[4].setPosition([0-(r_width/2),0-(r_thickness/2),0])
        r_prof_1[0].cv[5].setPosition([0,0-(r_thickness/2),0])
        r_prof_1[0].centerPivots()
        r_prof_1[0].translate.set(r_points['U'][0])

        r_prof_2 = pm.instance(r_prof_1[0], n="ribbon_2_profile_" + self.wrap_id)
        r_prof_2[0].rotateY.set(90)
        r_prof_2[0].translateY.set(r_points['D'][0].y)

        # Bow
        bow_rot = 10
        r_prof_3L = pm.instance(r_prof_1[0], n="ribbon_3L_profile_" + self.wrap_id)
        r_prof_3L[0].rotateY.set(90 + bow_rot)
        curve_3L.rotateY.set(0 - bow_rot)

        r_prof_3R = pm.instance(r_prof_1[0], n="ribbon_3R_profile_" + self.wrap_id)
        r_prof_3R[0].rotateY.set(90 - bow_rot)
        curve_3R.rotateY.set(0 + bow_rot)

        r_prof_4 = pm.instance(r_prof_1[0], n="ribbon_4_profile_" + self.wrap_id)
        r_prof_4[0].translateZ.set(r_width / 2)

        r_extrude_1U = pm.extrude(r_prof_1[0], curve_1U, et=2, rn=True, n="ribbon_ext_1U" + self.wrap_id)
        r_extrude_1D = pm.extrude(r_prof_1[0], curve_1D, et=2, rn=True, n="ribbon_ext_1D" + self.wrap_id)
        r_extrude_2L = pm.extrude(r_prof_2[0], curve_2L, et=2, rn=True, n="ribbon_ext_2L" + self.wrap_id)
        r_extrude_2R = pm.extrude(r_prof_2[0], curve_2R, et=2, rn=True, n="ribbon_ext_2R" + self.wrap_id)
        r_extrude_3L = pm.extrude(r_prof_3L[0], curve_3L, et=2, rn=True, n="ribbon_ext_3L" + self.wrap_id)
        r_extrude_3R = pm.extrude(r_prof_3R[0], curve_3R, et=2, rn=True, n="ribbon_ext_3R" + self.wrap_id)
        r_extrude_4 = pm.extrude(r_prof_4[0], curve_4, et=2, rn=True, n="ribbon_ext_4" + self.wrap_id)

        # Make ribbons taper
        r_extrude_3L[1].scale.set(0.8)
        r_extrude_3R[1].scale.set(0.8)
        r_extrude_4[1].scale.set(0.3)

        ribbons = {'1U' : [curve_1U, r_extrude_1U, pm.listConnections(r_extrude_1U, type="subCurve")[1]]}
        ribbons['1D'] = [curve_1D, r_extrude_1D, pm.listConnections(r_extrude_1D, type="subCurve")[1]]
        ribbons['2L'] = [curve_2L, r_extrude_2L, pm.listConnections(r_extrude_2L, type="subCurve")[1]]
        ribbons['2R'] = [curve_2R, r_extrude_2R, pm.listConnections(r_extrude_2R, type="subCurve")[1]]
        ribbons['3L'] = [curve_3L, r_extrude_3L, pm.listConnections(r_extrude_3L, type="subCurve")[1]]
        ribbons['3R'] = [curve_3R, r_extrude_3R, pm.listConnections(r_extrude_3R, type="subCurve")[1]]
        ribbons['4'] = [curve_4, r_extrude_4, pm.listConnections(r_extrude_4, type="subCurve")[1]]

        # Parent to main ribbon group
        pm.parent(curve_1U, self.r_curve_group)
        pm.parent(curve_1D, self.r_curve_group)
        pm.parent(curve_2L, self.r_curve_group)
        pm.parent(curve_2R, self.r_curve_group)
        pm.parent(curve_3L, self.r_curve_group)
        pm.parent(curve_3R, self.r_curve_group)
        pm.parent(curve_4, self.r_curve_group)
        pm.parent(r_extrude_1U[0], self.ribbon_group)
        pm.parent(r_extrude_1D[0], self.ribbon_group)
        pm.parent(r_extrude_2L[0], self.ribbon_group)
        pm.parent(r_extrude_2R[0], self.ribbon_group)
        pm.parent(r_extrude_3L[0], self.ribbon_group)
        pm.parent(r_extrude_3R[0], self.ribbon_group)
        pm.parent(r_extrude_4[0], self.ribbon_group)
        pm.parent(r_prof_1[0], self.r_curve_group)
        pm.parent(r_prof_2[0], self.r_curve_group)
        pm.parent(r_prof_3L[0], self.r_curve_group)
        pm.parent(r_prof_3R[0], self.r_curve_group)
        pm.parent(r_prof_4[0], self.r_curve_group)
        
        return ribbons, r_prof_1;

    def getObjectSides(self):
        """Get height, width and depth from boundingbox of just the object"""
        bbox_minmax = self.wrap_gift.boundingBoxMax.get() - self.wrap_gift.boundingBoxMin.get()

        side_a = abs(bbox_minmax[0]) # width
        side_d = abs(bbox_minmax[1]) # height
        side_e = abs(bbox_minmax[2]) # depth

        return side_a, side_d, side_e

    def getWrapSides(self):
        """Get height, width and depth from boundingbox of the object wrapped in paper"""
        bbox_minmax = pm.polyEvaluate(self.wrap_paper[0], b=True)

        side_w = abs(bbox_minmax[0][1] - bbox_minmax[0][0])
        side_h = abs(bbox_minmax[1][1] - bbox_minmax[1][0])
        side_d = abs(bbox_minmax[2][1] - bbox_minmax[2][0])

        return side_w, side_h, side_d

    def tieRibbon(self, seg):
        """
        Ties / unties the ribbon by modifying the curve extrusions.
        The process is divided into segments = seg
        """
        if seg >= 1:
            self.ribbons['1U'][2].maxValue.set(1)
            self.ribbons['1D'][2].maxValue.set(1)
        if seg >= 2:
            self.ribbons['2L'][2].maxValue.set(1)
            self.ribbons['2R'][2].maxValue.set(1)
        if seg >= 3:
            self.ribbons['3L'][2].maxValue.set(1)
            self.ribbons['3R'][2].maxValue.set(1)
        if seg >= 4:
            self.ribbons['4'][2].maxValue.set(1)

        if seg == 0:
            self.ribbons['1U'][2].maxValue.set(0)
            self.ribbons['1D'][2].maxValue.set(0)
        if seg < 2:
            self.ribbons['2L'][2].maxValue.set(0)
            self.ribbons['2R'][2].maxValue.set(0)
        if seg < 3:
            self.ribbons['3L'][2].maxValue.set(0)
            self.ribbons['3R'][2].maxValue.set(0)
        if seg < 4:
            self.ribbons['4'][2].maxValue.set(0)

    def applyColor(self, color=None):
        """
        Set color of the wrapping paper and ribbon.
        """
        paper_shader = 'shd_paper_' + self.wrap_color.upper()
        pm.sets(paper_shader, edit=True, forceElement=self.wrap_paper[0])

        ribbon_shader = 'shd_ribbon_' + self.ribbon_color.upper()

        if type(self.ribbons) is dict:
            ribbon = []
            for key in self.ribbons:
                ribbon.append(self.ribbons[key][1][0])
        else:
            ribbon = self.ribbons
        pm.sets(ribbon_shader, edit=True, forceElement=ribbon)

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
        if size != self.ribbon_size:
            old_size = self.ribbon_size
            self.ribbon_size = size
            self.storeCtrlValues()

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
                scale = prof.scale.get()
                scale.x *= mult
                prof.scale.set(scale)

    def reloadGiftWrap(self):
        self.removeGiftWrap()
        self.createGiftWrap(self.wrap_gift)

def windowUI():
    win_w = 300
    col_1_w = 100
    col_2_w = 35
    col_3_w = win_w - (col_1_w + col_2_w)-25
    colx4 = win_w / 4
    
    my_window = pm.window(t="Gift Generator", rtf=True, w=win_w)
    main_layout = pm.columnLayout(rs=10)
    with main_layout:
        wrap_frame = pm.frameLayout(l='Wrap Gift', bs='etchedIn',
                                    w=win_w,
                                    cll=True, cl=False)
        with wrap_frame:
            wrap_layout = pm.columnLayout()
            with wrap_layout:
                wrap_row_size = pm.rowLayout(nc=4, cw4=(colx4,colx4,colx4-5,colx4))
                with wrap_row_size:
                    pm.text(' Paper weight:')
                    wrap_sld_thk = pm.floatSliderGrp(min=0.005, max=0.05, value=0.02)

                    pm.text('Ribbon size:')
                    wrap_opt_menu_r_size = pm.optionMenu()
                    with wrap_opt_menu_r_size:
                        pm.menuItem( label='Large' )
                        pm.menuItem( label='Medium' )
                        pm.menuItem( label='Small' )                        

                wrap_row_color = pm.rowLayout(nc=4, cw4=(colx4,colx4,colx4-5,colx4))
                with wrap_row_color:
                    pm.text(' Paper color:')
                    wrap_opt_menu_p_color = pm.optionMenu()
                    with wrap_opt_menu_p_color:
                        pm.menuItem( label='Random' )
                        pm.menuItem( label='Red' )
                        pm.menuItem( label='Green' )
                        pm.menuItem( label='Blue' )
                        pm.menuItem( label='Yellow' )
                        pm.menuItem( label='Black' )
                        pm.menuItem( label='White' )
                    pm.text('Ribbon color:')
                    wrap_opt_menu_r_color = pm.optionMenu()
                    with wrap_opt_menu_r_color:
                        pm.menuItem( label='Random' )
                        pm.menuItem( label='Red' )
                        pm.menuItem( label='Green' )
                        pm.menuItem( label='Blue' )
                        pm.menuItem( label='Yellow' )
                pm.separator(h=10, w=win_w, style='in')
                pm.text(" Animation", font='smallBoldLabelFont')
                wrap_row_anim = pm.rowLayout(nc=4, cw4=(colx4,colx4,colx4-5,colx4))
                with wrap_row_anim:
                    pm.text('Start frame:', w=colx4, align='right')
                    wrap_int_anim_s = pm.intField(min=0, w=45, v=1)
                    pm.text('End frame:', w=colx4, align='right')
                    wrap_int_anim_e = pm.intField(min=0, w=45, v=24)
                pm.separator(h=10, w=win_w, style='in')

                wrap_row_btn = pm.rowLayout(nc=2, cw2=(win_w /2 - 30, win_w /2 - 30))
                with wrap_row_btn:
                    pm.text('')
                    wrap_btn_run = pm.button(l='Wrap', w=60)
                pm.text("Wraps selected object(s), animate the whole process\n" +
                        "by adjusting the connected attribute of the control handle",
                        font='obliqueLabelFont', align='center', width=win_w-10)

        mod_frame = pm.frameLayout(l='Modifiy Wrap', bs='etchedIn',
                                   w=win_w,
                                   cll=True, cl=True)
        with mod_frame:
            mod_layout = pm.columnLayout()
            with mod_layout:
                mod_row_scan_btn = pm.rowLayout(nc=3, cw3=(15, win_w /2 -15, win_w /2 - 10))
                with mod_row_scan_btn:
                    pm.text('')
                    mod_btn_scan_sel = pm.button(l='Scan selection', w=120)
                    mod_btn_scan_scn = pm.button(l='Scan scene', w=100)
                pm.text("Scans for gifts that have already been wrapped",
                        font='obliqueLabelFont', align='center', width=win_w)
                pm.separator(h=10, w=win_w, style='in')
                pm.text(' Result:', font='smallBoldLabelFont')

                mod_txt_list = pm.textScrollList(numberOfRows=8, allowMultiSelection=True,
                                                 width=win_w-5, height=150, font='smallFixedWidthFont')
                pm.text(" Paper Weight:", font='smallBoldLabelFont')
                mod_row_pweight = pm.rowLayout(nc=2, cw2=(200, 100))
                with mod_row_pweight:
                    mod_sld_thk = pm.floatSliderGrp(min=0.005, max=0.05, value=0.02, f=True, w=180, pre=3, cw2=(50,130))
                    mod_btn_pweight = pm.button(l='Edit', w=80)
                pm.separator(h=10, w=win_w, style='in')
                mod_row_color_hdr = pm.rowLayout(nc=3, cw3=(100,100,80))
                with mod_row_color_hdr:
                    pm.text(' Paper color:', font='tinyBoldLabelFont')
                    pm.text('Ribbon color:', font='tinyBoldLabelFont')
                    pm.text(' ')
                mod_row_color = pm.rowLayout(nc=3, cw3=(100,100,80))
                with mod_row_color:
                    mod_opt_menu_p_color = pm.optionMenu()
                    with mod_opt_menu_p_color:
                        pm.menuItem( label='Random' )
                        pm.menuItem( label='Red' )
                        pm.menuItem( label='Green' )
                        pm.menuItem( label='Blue' )
                        pm.menuItem( label='Yellow' )
                        pm.menuItem( label='Black' )
                        pm.menuItem( label='White' )
                        pm.menuItem( label='Current' )
                    mod_opt_menu_r_color = pm.optionMenu()
                    with mod_opt_menu_r_color:
                        pm.menuItem( label='Random' )
                        pm.menuItem( label='Red' )
                        pm.menuItem( label='Green' )
                        pm.menuItem( label='Blue' )
                        pm.menuItem( label='Yellow' )
                        pm.menuItem( label='Current' )
                    mod_btn_color = pm.button(l='Edit', w=80)
                pm.separator(h=10, w=win_w, style='in')
                pm.text(' Ribbon size:', font='tinyBoldLabelFont')
                mod_row_r_sz = pm.rowLayout(nc=2, cw2=(200,80))
                with mod_row_r_sz:
                    mod_radio_r_sz =pm.radioButtonGrp(labelArray3=['Small', 'Medium', 'Large'], numberOfRadioButtons=3, cw3=(60,60,60), sl=3)
                    mod_btn_r_sz = pm.button(l='Edit', w=80)
                pm.separator(h=10, w=win_w, style='in')
                mod_row_anim_hdr = pm.rowLayout(nc=3, cw3=(100,100,80))
                with mod_row_anim_hdr:
                    pm.text(' Anim. start:', font='tinyBoldLabelFont')
                    pm.text('Anim. end:', font='tinyBoldLabelFont')
                    pm.text(' ')
                mod_row_anim = pm.rowLayout(nc=3, cw3=(100,100,80))
                with mod_row_anim:
                    mod_int_anim_s = pm.intField(min=0, w=45, v=1)
                    mod_int_anim_e = pm.intField(min=0, w=45, v=24)
                    mod_btn_anim = pm.button(l='Edit', w=80)

    wrap_btn_run.setCommand(pm.Callback(runWrap, wrap_sld_thk, wrap_opt_menu_p_color,
                            wrap_opt_menu_r_size, wrap_opt_menu_r_color, wrap_int_anim_s,
                            wrap_int_anim_e))
    mod_btn_scan_sel.setCommand(pm.Callback(scanForWraps, mod_txt_list, True))
    mod_btn_scan_scn.setCommand(pm.Callback(scanForWraps, mod_txt_list, False))
    mod_btn_pweight.setCommand(pm.Callback(editPaperWeight, mod_txt_list, mod_sld_thk))
    mod_btn_color.setCommand(pm.Callback(editColors, mod_txt_list, mod_opt_menu_p_color, mod_opt_menu_r_color))
    mod_btn_r_sz.setCommand(pm.Callback(editRibbonSize, mod_txt_list, mod_radio_r_sz))
    mod_btn_anim.setCommand(pm.Callback(editAnimation, mod_txt_list, mod_int_anim_s, mod_int_anim_e))
    mod_txt_list.selectCommand(pm.Callback(deselectHeader, mod_txt_list))

    my_window.show()

def deselectHeader(txt_list):
    txt_list.deselectIndexedItem([1,2])

def runWrap(p_thk, p_clr, r_sz, r_clr, an_s, an_e):
    paper_thickness = p_thk.getValue()
    paper_color = p_clr.getValue().lower()
    ribbon_size = r_sz.getValue()[0]
    ribbon_color = r_clr.getValue().lower()
    animation_start = an_s.getValue()
    animation_end = an_e.getValue()

    objects = pm.selected()
    for o in objects[:32]:
        gift = GiftWrap(o, 'create', ribbon_size, paper_thickness, paper_color, ribbon_color, animation_start, animation_end)

def scanForWraps(txt_list, scan_mode, selection=None):
    global wrap_list
    if selection is None:
        wrap_list = pm.ls(regex='^.*_gift_wrap_[0-9A-Z]{5}_GRP\|CTRL_gift_[0-9A-Z]{5}$',
                          type='transform', sl=scan_mode)

    txt_list.removeAll()

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
        titles += col5_title + col6_title +col7_title
        txt_list.append(titles)
        txt_list.append(addPadding('-',0))
        for w in wrap_list:
            wrap = GiftWrap(w,'load')

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
            txt_list.append(attributes)

        if selection is None:
            num_items = txt_list.getNumberOfItems()+1
            for i in range(3, num_items):
                pm.textScrollList(txt_list, selectIndexedItem=i, edit=True)
        else:
            for s in selection:
                pm.textScrollList(txt_list, selectIndexedItem=s+3, edit=True)
    else:
        txt_list.append('None found')
        txt_list.append(addPadding(' ',0))

def addPadding(text, column):
    """
    Add spaces to the given text in order to
    align it properly in the scroll list.
    """
    # Column length
    col_len = [0] # 0
    col_len.append(18) # 1
    col_len.append(8)
    col_len.append(10)
    col_len.append(10)
    col_len.append(10)
    col_len.append(10)
    col_len.append(10) # 7

    if column == 0:
        return text[:1] * ( sum(col_len) + 7)
    else:
        text = text[:col_len[column]]
        padding = col_len[column] - len(text)
        text += ' ' * (padding+1)

        return text

def editPaperWeight(txt_list, p_weight):
    selection = removeHeader(txt_list)
    wrap_thickness = p_weight.getValue()
    if selection is not None:
        for s in selection:
            edit_gift = GiftWrap(wrap_list[s], 'load')
            edit_gift.wrap_thickness = wrap_thickness
            edit_gift.reloadGiftWrap()
            wrap_list[s] = edit_gift.ctrl_handle[0] # Replace the old gift
        scanForWraps(txt_list, 0, selection) # Refresh scroll list

def editColors(txt_list, p_color, r_color):
 
    selection = removeHeader(txt_list)
    wrap_color = p_color.getValue().lower()
    ribbon_color = r_color.getValue().lower()
    if selection is not None:
        for s in selection:
            edit_gift = GiftWrap(wrap_list[s], 'load')
            edit_gift.newColor(wrap_color, ribbon_color)
        scanForWraps(txt_list, 0, selection) # Refresh scroll list

def editRibbonSize(txt_list, r_size):
    selection = removeHeader(txt_list)
    r_size = r_size.getSelect()
    if r_size == 1:
        ribbon_size = 'S'
    elif r_size == 2:
        ribbon_size = 'M'
    elif r_size == 3:
        ribbon_size = 'L'

    if selection is not None:
        for s in selection:
            edit_gift = GiftWrap(wrap_list[s], 'load')
            edit_gift.changeRibbon(ribbon_size)
        scanForWraps(txt_list, 0, selection) # Refresh scroll list

def editAnimation(txt_list, anim_s, anim_e):
    selection = removeHeader(txt_list)
    animation_start = anim_s.getValue()
    animation_end = anim_e.getValue()

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
    hdr_rows = 2 # Number of header rows
    
    items = txt_list.getSelectIndexedItem()
    if items == []:
        return None
    else:
        gifts = [( (hdr_rows + 1) * -1 ) + item for item in items]
        return gifts


def createShaders():
    """
    These shaders are used for coloring the generated geometry
    """
    # Ribbon Materials
    # Green Material
    rg_name = 'ribbon_GREEN'
    if not pm.objExists("mat_" + rg_name):
        mat_ribbon_green = pm.shadingNode("blinn", asShader=True, name ="mat_" + rg_name)
        mat_ribbon_green.color.set([0.1,0.6,0.1])
        mat_ribbon_green.eccentricity.set(0.6)
        mat_ribbon_green.specularRollOff.set(0.7)
    # Green Shader
    if not pm.objExists("shd_" + rg_name):
        shd_ribbon_green = pm.sets( renderable=True, noSurfaceShader=True, empty=True, name="shd_" + rg_name)
        # Connect material to shader
        mat_ribbon_green.outColor >> shd_ribbon_green.surfaceShader

    # Red Material
    rr_name = 'ribbon_RED'
    if not pm.objExists("mat_" + rr_name):
        mat_ribbon_red = pm.shadingNode("blinn", asShader=True, name ="mat_" + rr_name)
        mat_ribbon_red.color.set([0.6,0.1,0.1])
        mat_ribbon_red.eccentricity.set(0.6)
        mat_ribbon_red.specularRollOff.set(0.7)
    # Red Shader
    if not pm.objExists("shd_" + rr_name):
        shd_ribbon_red = pm.sets( renderable=True, noSurfaceShader=True, empty=True, name="shd_" + rr_name)
        # Connect material to shader
        mat_ribbon_red.outColor >> shd_ribbon_red.surfaceShader

    # Blue Material
    rb_name = 'ribbon_BLUE'
    if not pm.objExists("mat_" + rb_name):
        mat_ribbon_blue = pm.shadingNode("blinn", asShader=True, name ="mat_" + rb_name)
        mat_ribbon_blue.color.set([0.1,0.1,0.6])
        mat_ribbon_blue.eccentricity.set(0.6)
        mat_ribbon_blue.specularRollOff.set(0.7)
    # Green Shader
    if not pm.objExists("shd_" + rb_name):
        shd_ribbon_blue = pm.sets( renderable=True, noSurfaceShader=True, empty=True, name="shd_" + rb_name)
        # Connect material to shader
        mat_ribbon_blue.outColor >> shd_ribbon_blue.surfaceShader

    # Yellow Material
    ry_name = 'ribbon_YELLOW'
    if not pm.objExists("mat_" + ry_name):
        mat_ribbon_yellow = pm.shadingNode("blinn", asShader=True, name ="mat_" + ry_name)
        mat_ribbon_yellow.color.set([0.8,0.7,0.1])
        mat_ribbon_yellow.eccentricity.set(0.6)
        mat_ribbon_yellow.specularRollOff.set(0.7)
    # Green Shader
    if not pm.objExists("shd_" + ry_name):
        shd_ribbon_yellow = pm.sets( renderable=True, noSurfaceShader=True, empty=True, name="shd_" + ry_name)
        # Connect material to shader
        mat_ribbon_yellow.outColor >> shd_ribbon_yellow.surfaceShader

    # Paper Materials
    # Green Material
    pg_name = 'paper_GREEN'
    if not pm.objExists("mat_" + pg_name):
        mat_paper_green = pm.shadingNode("lambert", asShader=True, name ="mat_" + pg_name)
        mat_paper_green.color.set([0.2,0.6,0.2])
        mat_paper_green.diffuse.set(1)
    # Green Shader
    if not pm.objExists("shd_" + pg_name):
        shd_paper_green = pm.sets( renderable=True, noSurfaceShader=True, empty=True, name="shd_" + pg_name)
        # Connect material to shader
        mat_paper_green.outColor >> shd_paper_green.surfaceShader

    # Red Material
    pr_name = 'paper_RED'
    if not pm.objExists("mat_" + pr_name):
        mat_paper_red = pm.shadingNode("lambert", asShader=True, name ="mat_" + pr_name)
        mat_paper_red.color.set([0.8,0.3,0.3])
        mat_paper_red.diffuse.set(1)
    # Red Shader
    if not pm.objExists("shd_" + pr_name):
        shd_paper_red = pm.sets( renderable=True, noSurfaceShader=True, empty=True, name="shd_" + pr_name)
        # Connect material to shader
        mat_paper_red.outColor >> shd_paper_red.surfaceShader

    # Blue Material
    pb_name = 'paper_BLUE'
    if not pm.objExists("mat_" + pb_name):
        mat_paper_blue = pm.shadingNode("lambert", asShader=True, name ="mat_" + pb_name)
        mat_paper_blue.color.set([0.3,0.3,0.8])
        mat_paper_blue.diffuse.set(1)
    # Green Shader
    if not pm.objExists("shd_" + pb_name):
        shd_paper_blue = pm.sets( renderable=True, noSurfaceShader=True, empty=True, name="shd_" + pb_name)
        # Connect material to shader
        mat_paper_blue.outColor >> shd_paper_blue.surfaceShader

    # Yellow Material
    py_name = 'paper_YELLOW'
    if not pm.objExists("mat_" + py_name):
        mat_paper_yellow = pm.shadingNode("lambert", asShader=True, name ="mat_" + py_name)
        mat_paper_yellow.color.set([0.8,0.75,0.3])
        mat_paper_yellow.diffuse.set(1)
    # Yellow Shader
    if not pm.objExists("shd_" + py_name):
        shd_paper_yellow = pm.sets( renderable=True, noSurfaceShader=True, empty=True, name="shd_" + py_name)
        # Connect material to shader
        mat_paper_yellow.outColor >> shd_paper_yellow.surfaceShader

    # White Material
    pw_name = 'paper_WHITE'
    if not pm.objExists("mat_" + pw_name):
        mat_paper_white = pm.shadingNode("lambert", asShader=True, name ="mat_" + pw_name)
        mat_paper_white.color.set([0.98,0.98,0.98])
        mat_paper_white.diffuse.set(1)
    # White Shader
    if not pm.objExists("shd_" + pw_name):
        shd_paper_white = pm.sets( renderable=True, noSurfaceShader=True, empty=True, name="shd_" + pw_name)
        # Connect material to shader
        mat_paper_white.outColor >> shd_paper_white.surfaceShader

    # Black Material
    pbl_name = 'paper_BLACK'
    if not pm.objExists("mat_" + pbl_name):
        mat_paper_black = pm.shadingNode("lambert", asShader=True, name ="mat_" + pbl_name)
        mat_paper_black.color.set([0.1,0.1,0.1])
        mat_paper_black.diffuse.set(1)
    # Black Shader
    if not pm.objExists("shd_" + pbl_name):
        shd_paper_black = pm.sets( renderable=True, noSurfaceShader=True, empty=True, name="shd_" + pbl_name)
        # Connect material to shader
        mat_paper_black.outColor >> shd_paper_black.surfaceShader

createShaders()
windowUI()
