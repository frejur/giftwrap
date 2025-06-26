from collections import namedtuple
from ...utils.custom_types.vec import Vec
from math import sqrt

class FoldingPattern:
    def __init__(self, side_a, side_d, side_e, paper_thickness):
        """
        Calculates the coordinates for all wrapping folds.

        Args:
            side_a: The `width` of the object  (See diagram)
            side_d: The `height` of the object (See diagram)
            side_e: The `depth` of the object  (See diagram)
            paper_thickness: The thickness of the paper.
        Notes:
            See the diagram at the bottom of this file for more details.
        """
        # y-axis
        y_gft = paper_thickness / 2

        # calculate sides
        side_a += paper_thickness
        side_d += paper_thickness
        gft_side_b = side_d * 0.6
        gft_side_c = side_e / 2 + y_gft
        side_e += paper_thickness  # needs to be run last

        # Store length of flaps
        self.flap_length = gft_side_b

        # check if folds will overlap
        self.folds_overlap = side_e < (2 * gft_side_b)

        # calculate side f
        if not self.folds_overlap:
            gft_side_f = gft_side_c - gft_side_b
        else:
            gft_side_f = gft_side_b - gft_side_c

        # x-axis
        x_h = (side_a / 2)
        x_i = x_h + gft_side_b
        x_g = x_h * -1
        x_f = x_i * -1

        # y-axis
        z_5 = (side_e / 2)
        z_6 = z_5 + side_d
        z_7 = z_6 + gft_side_c
        z_3 = z_5 * -1
        z_2 = z_6 * -1

        # calculate z-1 axis
        if not self.folds_overlap:
            z_1 = z_7 * -1
        else:
            z_1 = z_2 - gft_side_b

        # calculate z-8 axis
        if not self.folds_overlap:
            z_8 = z_7 + gft_side_f
        else:
            z_8 = z_7

        # Coordinates in world space
        self.gift_fold_points = {
            'F1': Vec(x_f, y_gft, z_1), 'F2': Vec(x_f, y_gft, z_2),
            'F3': Vec(x_f, y_gft, z_3),
            'F4': Vec(x_f + gft_side_b - gft_side_c, y_gft, 0.0),
            'F5': Vec(x_f, y_gft, z_5),
            'F6': Vec(x_f, y_gft, z_6),
            'F7': Vec(x_f, y_gft, z_7), 'F8': Vec(x_f, y_gft, z_8),
            'G1': Vec(x_g, y_gft, z_1),
            'G2': Vec(x_g, y_gft, z_2), 'G3': Vec(x_g, y_gft, z_3),
            'G4': Vec(x_g, y_gft, 0.0),
            'G5': Vec(x_g, y_gft, z_5), 'G6': Vec(x_g, y_gft, z_6),
            'G7': Vec(x_g, y_gft, z_7),
            'G8': Vec(x_g, y_gft, z_8),
            'H1': Vec(x_h, y_gft, z_1), 'H2': Vec(x_h, y_gft, z_2),
            'H3': Vec(x_h, y_gft, z_3),
            'H4': Vec(x_h, y_gft, 0.0), 'H5': Vec(x_h, y_gft, z_5),
            'H6': Vec(x_h, y_gft, z_6),
            'H7': Vec(x_h, y_gft, z_7), 'H8': Vec(x_h, y_gft, z_8),
            'I1': Vec(x_i, y_gft, z_1),
            'I2': Vec(x_i, y_gft, z_2), 'I3': Vec(x_i, y_gft, z_3),
            'I4': Vec(x_i - gft_side_b + gft_side_c, y_gft, 0.0),
            'I5': Vec(x_i, y_gft, z_5), 'I6': Vec(x_i, y_gft, z_6),
            'I7': Vec(x_i, y_gft, z_7),
            'I8': Vec(x_i, y_gft, z_8), 'I4a':Vec(x_i, y_gft, z_3)
        }

        # Diagonal folds -------------------------------------------------------

        # Calculate diagonal folds F4a, F4b, I4a, I4b
        self.gift_fold_points['I4a'].z += gft_side_b
        self.gift_fold_points['I4b'] = Vec(x_i, y_gft, z_5)
        self.gift_fold_points['I4b'].z -= gft_side_b

        self.gift_fold_points['F4a'] = Vec(x_f, y_gft, z_3)
        self.gift_fold_points['F4a'].z += gft_side_b
        self.gift_fold_points['F4b'] = Vec(x_f, y_gft, z_5)
        self.gift_fold_points['F4b'].z -= gft_side_b

        # Calculate intersecting points HI4, FG4
        if self.folds_overlap:
            self.gift_fold_points['HI4'] = Vec(x_h, y_gft, 0.0)
            self.gift_fold_points['HI4'].x += side_e / 2
            self.gift_fold_points['FG4'] = Vec(x_g, y_gft, 0.0)
            self.gift_fold_points['FG4'].x -= side_e / 2

        # Calculate diagonal folds F1a, I1a
        if not self.folds_overlap:
            self.gift_fold_points['I1a'] = Vec(x_i, y_gft, z_2)
            self.gift_fold_points['I1a'].z -= gft_side_b
            self.gift_fold_points['F1a'] = Vec(x_f, y_gft, z_2)
            self.gift_fold_points['F1a'].z -= gft_side_b
        else:
            self.gift_fold_points['I1a'] = Vec(x_i, y_gft, z_1)
            self.gift_fold_points['I1a'].z += gft_side_b - gft_side_c
            self.gift_fold_points['I1a'].x -= gft_side_b - gft_side_c
            self.gift_fold_points['F1a'] = Vec(x_f, y_gft, z_1)
            self.gift_fold_points['F1a'].z += gft_side_b - gft_side_c
            self.gift_fold_points['F1a'].x += gft_side_b - gft_side_c

        # Calculate diagonal folds F1b, I1b
        if self.folds_overlap:
            self.gift_fold_points['I1b'] = Vec(x_i, y_gft, z_1)
            self.gift_fold_points['I1b'].z += (gft_side_b - gft_side_c) * 2
            self.gift_fold_points['F1b'] = Vec(x_f, y_gft, z_1)
            self.gift_fold_points['F1b'].z += (gft_side_b - gft_side_c) * 2

        # Calculate diagonal folds F1c, I1c
        if self.folds_overlap:
            self.gift_fold_points['I1c'] = Vec(x_i, y_gft, z_1)
            self.gift_fold_points['I1c'].x -= (gft_side_b - gft_side_c) * 2
            self.gift_fold_points['F1c'] = Vec(x_f, y_gft, z_1)
            self.gift_fold_points['F1c'].x += (gft_side_b - gft_side_c) * 2

        # Calculate diagonal folds F7a, I7a
        if not self.folds_overlap:
            self.gift_fold_points['I7a'] = Vec(x_i, y_gft, z_6)
            self.gift_fold_points['I7a'].z += gft_side_b
            self.gift_fold_points['F7a'] = Vec(x_f, y_gft, z_6)
            self.gift_fold_points['F7a'].z += gft_side_b
        else:
            self.gift_fold_points['I7a'] = Vec(x_i, y_gft, z_7)
            self.gift_fold_points['I7a'].x -= gft_side_b - gft_side_c
            self.gift_fold_points['F7a'] = Vec(x_f, y_gft, z_7)
            self.gift_fold_points['F7a'].x += gft_side_b - gft_side_c

        # Calculate diagonal folds F7b, I7b
        if self.folds_overlap:
            self.gift_fold_points['I7b'] = Vec(x_i, y_gft, z_7)
            self.gift_fold_points['I7b'].z -= gft_side_b - gft_side_c
            self.gift_fold_points['F7b'] = Vec(x_f, y_gft, z_7)
            self.gift_fold_points['F7b'].z -= gft_side_b - gft_side_c

        # Padding folds --------------------------------------------------------
        thk = paper_thickness    # shorthand
                                 #     :.
                                 #     | ''.
                                 # leg |    /'.
        leg = thk * sqrt(2)      #     |  /thk '..
                                 #     |/_________:.
                                 #         leg

        # Calculate padding folds F3x, F4xu, F4xus, F4xds, F4xd, F5x
        self.gift_fold_points['F3x'] = Vec(x_g - leg, y_gft, z_3)
        self.gift_fold_points['F4xu'] = Vec(x_g - thk - leg, y_gft, z_3 + thk)
        self.gift_fold_points['F4xus'] = Vec(x_f, y_gft, z_3 + thk + leg)
        self.gift_fold_points['F4xds'] = Vec(x_f, y_gft, z_5 - thk - leg)
        self.gift_fold_points['F4xu'] = Vec(x_g - thk - leg, y_gft, z_5 - thk)
        self.gift_fold_points['F5x'] = Vec(x_g - leg, y_gft, z_5)

        # Calculate padding folds F4x, F4y, F4z
        if self.folds_overlap:
            temp_x = x_g + side_e / 2
            self.gift_fold_points['F4x'] = Vec(temp_x - leg, y_gft, 0.0)
            self.gift_fold_points['F4y'] = Vec(temp_x - leg/2, y_gft, -leg/2)
            self.gift_fold_points['F4z'] = Vec(temp_x - leg/2, y_gft, leg/2)

        # Calculate padding folds F4u, F4d, F4us, F4ds
        self.gift_fold_points['F4u'] = Vec(x_g - thk, y_gft, z_3 + thk)
        self.gift_fold_points['F4d'] = Vec(x_g - thk, y_gft, z_5 - thk)
        self.gift_fold_points['F4us'] = Vec(x_f, y_gft, z_3 + thk)
        self.gift_fold_points['F4ds'] = Vec(x_f, y_gft, z_5 - thk)

        # Calculate padding folds I4u, I4d, I4us, I4ds
        self.gift_fold_points['I4u'] = Vec(x_h + thk, y_gft, z_3 + thk)
        self.gift_fold_points['I4d'] = Vec(x_h + thk, y_gft, z_5 - thk)
        self.gift_fold_points['I4us'] = Vec(x_i, y_gft, z_3 + thk)
        self.gift_fold_points['I4ds'] = Vec(x_i, y_gft, z_5 - thk)

        # Calculate padding folds I3x, I4xu, I4xus, I4xds, I4xd, I5x
        self.gift_fold_points['I3x'] = Vec(x_h + leg, y_gft, z_3)
        self.gift_fold_points['I4xu'] = Vec(x_h + thk - leg, y_gft, z_3 + thk)
        self.gift_fold_points['I4xus'] = Vec(x_i, y_gft, z_3 + thk + leg)
        self.gift_fold_points['I4xds'] = Vec(x_i, y_gft, z_5 - thk - leg)
        self.gift_fold_points['I4xu'] = Vec(x_i + thk - leg, y_gft, z_5 - thk)
        self.gift_fold_points['I5x'] = Vec(x_i + leg, y_gft, z_5)

        # Calculate padding folds I4x, I4y, I4z
        if self.folds_overlap:
            temp_x = x_h - side_e / 2
            self.gift_fold_points['I4x'] = Vec(temp_x + leg, y_gft, 0.0)
            self.gift_fold_points['I4y'] = Vec(temp_x + leg/2, y_gft, -leg/2)
            self.gift_fold_points['I4z'] = Vec(temp_x + leg/2, y_gft, leg/2)

        # Calculate padding folds F1u, F1d, F1s, I1u, I1d, I1u
        self.gift_fold_points['F1u'] = Vec(x_g - thk, y_gft, z_1)
        self.gift_fold_points['F1d'] = Vec(x_g - thk, y_gft, z_2 - thk)
        self.gift_fold_points['F1s'] = Vec(x_f, y_gft, z_2 - thk)
        self.gift_fold_points['I1u'] = Vec(x_h + thk, y_gft, z_1)
        self.gift_fold_points['I1d'] = Vec(x_h + thk, y_gft, z_2 - thk)
        self.gift_fold_points['I1s'] = Vec(x_i, y_gft, z_2 - thk)

        # Calculate padding folds F1x, F1xd, F1xm, F1xs
        self.gift_fold_points['F1x'] = Vec(x_g + leg, y_gft, z_2)
        self.gift_fold_points['F1xd'] = Vec(x_g + leg, y_gft, z_2 - thk)
        if self.folds_overlap:
            temp_x = x_f + gft_side_b - gft_side_c
            temp_z = z_1 + gft_side_b - gft_side_c
            self.gift_fold_points['F1xm'] = Vec(temp_x, y_gft, temp_z)
            self.gift_fold_points['F1xm'].x -= leg/2
            self.gift_fold_points['F1xm'].z += leg/2

        if self.folds_overlap:
            self.gift_fold_points['F1xs'] = Vec(x_f, y_gft, z_1 - leg)
        else:
            temp_z = z_1 + gft_side_b - gft_side_c
            self.gift_fold_points['F1xs'] = Vec(x_f, y_gft, temp_z)


        # Calculate padding folds F7u, F7s, F7d, F7m, F8d
        self.gift_fold_points['F7u'] = Vec(x_g - thk, y_gft, z_6 + thk)
        self.gift_fold_points['F7s'] = Vec(x_f, y_gft, z_6 + thk)
        if not self.folds_overlap:
            self.gift_fold_points['F7m'] = Vec(x_g - thk, y_gft, z_7)
            self.gift_fold_points['F8d'] = Vec(x_g - thk, y_gft, z_8)
        else:
            self.gift_fold_points['F7d'] = Vec(x_g - thk, y_gft, z_7)

        # Calculate padding folds I7u, I7s, I7d, I7m, I8d
        self.gift_fold_points['I7u'] = Vec(x_h + thk, y_gft, z_6 + thk)
        self.gift_fold_points['I7s'] = Vec(x_i, y_gft, z_6 + thk)
        if not self.folds_overlap:
            self.gift_fold_points['I7m'] = Vec(x_h + thk, y_gft, z_7)
            self.gift_fold_points['I8d'] = Vec(x_h + thk, y_gft, z_8)
        else:
            self.gift_fold_points['I7d'] = Vec(x_h + thk, y_gft, z_7)


    def point(self, point_id):
        return self.gift_fold_points[point_id]

    def hasOverlappingFolds(self):
        return self.folds_overlap

    def getFlapLength(self):
        return self.flap_length

"""
 FOLDING PATTERN DIAGRAM

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
        7_ |%_ _ |_ _ _ _ _ _ _ _|_ _ %|  __,
           |     |               |     |    |-- F (Only present when no overlap)
        8_ |_____|_______________|_____|  __|
                         :
                                 <= B =>
                         :
|                                                    |
v                        :                           v
BL quadrant <--          :             --> BR quadrant

            RIGHT HAND SIDE DIAGONAL FOLDS:
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
  |FI4/HG4-> %    |      :    |            +  |
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

                    PADDING FOLDS
      (The 'flaps' are extended / padded by the
       paper thickness before they are folded,
       in order to avoid self-intersections)
 
    Overlapping folds    :              No overlap
                         :
  Upper                  :    Upper                   Lower
     u                   :       u
  . -|- - - - - - .  1   :    . -|- - - - - - .   1   .- x - - - - - -.    
  :  |   .       .:      :    :  |            :       :.   \          :
  :  |     .   .  xs     :    :  |            :       :  u___xu________ s
  :  |       .   /:      :    :  |           .:       :  | .   \      :
  :  |     .  xm  :      :    :  |         .  xs      :  |   .   \    :
  :  |   .   /   .:      :    :  |       .   /:       :  |     .   \  :
  :  | .   /      :      :    :  |     .   /  :       :  |       .   \:
  :  d___xd________ s    :    :  |   .   /    :       :  |         .  xs
  :.   /          :      :    :  | .   /      :       :  |           .:
  ' -x  - - - - - '      :    :  d____xd_______ s     :  |            :
                         :    :.   /          :       :  |            :
                         :    ' - x - - - - - -       :- m - - - - - -:   7
                         :                            :  |            :
                         :    Mid                     :  |            :
  Mid                    :    .- x - - - - - -.       ' -|- - - - - - '   8
  .- x - - - - - - .     :    :.   \          :          d
  :.   \           :     :    :  u___xu________ us
  :  u___xu_________ us  :    :  | .   \      :
  :  | .   \       :     :    :  |   .   \    :
  :  |   .   \   . : xus :    :  |     .   \  :
  :  |     .   y   /     :    :  |       .   \:
  :  |       .   x :     :    :  |         .  xus
  :  |     .   z   \ xds :    :  |           .:
  :  |   .   /   . :     :    :  |            :
  :  | .   /       :     :    :  |            :   4
  :  d___xd_________ ds  :    :  |            :
  :.    /          :     :    :  |           .:
  ' - x - - - - -  '     :    :  |         .  :
                         :    :  |       .   .xds
  Lower                  :    :  |     .   /  :
  .- x - - - - - - - .   :    :  |   .   /    :
  :.   \             :   :    :  | .   /      :
  :  u___xu_________  _ s:    :  d___xd________ ds
  :  | .   \         :   :    :.   /          :
  :  |   .   \   .   :   :    '- x - - - - - -'
  :  |     .   \     :   :
  :  |       .   \   :   :
  '- | - - - - - - \-' 7 :
     d              xd   :
                         :
                         
                    OTHER POINTS
    (Vertices that are not part of a fold but are
      still present to ensure proper topology)
                         :
                         :
           F     G       :       H     I
           |     |               |     |
                         :
        2_ : . . : . . . . . . . : . . :
           :    'o_______________o'    :  <-- G2o    &    H2o   
           :     :       :       :     :  
           :     o_______________o     :  <-- G3o    &    H3o
        3_ : . .' .. . . . . . .. '. . :
           : .' .'               :. '. :
           :' .' :       :       : '. ':
           :.'   :               :   '.:
-  -  - 4- : . . : . . . . . . . : . . :
           :.    :               :    .:
           :.'.  :       :       :  .'.:
        5_ : '.'.: . . . . . . . :.'.' :
           :   '.o_______________o.'   :  <-- G5o    &    H5o   
           :     :       :       :     :  
           :     o_______________o     :  <-- G6o    &    H6o
        6_ : . .': . . . . . . . :'. . :
        
                         :
"""
