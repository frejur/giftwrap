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
        self.paper_thickness = paper_thickness

        # y-axis
        y_gft = paper_thickness / 2

        # Calculate sides
        self.sides = {'A': side_a + paper_thickness,
                      'D': side_d + paper_thickness,
                      'C': side_e / 2 + y_gft,
                      'B': (side_d + paper_thickness) * 0.6,
                      'E': side_e + paper_thickness}

        # Store length of flaps
        self.flap_length = self.sides['B']

        # check if folds will overlap
        self.folds_overlap = self.sides['E'] < (2 * self.sides['B'])

        # calculate side f
        if not self.folds_overlap:
            self.sides['F'] = self.sides['C'] - self.sides['B']
        else:
            self.sides['F'] = self.sides['B'] - self.sides['C']

        bc_diff = self.sides['B'] - self.sides['C']

        # x-axis
        x_h = (self.sides['A'] / 2)
        x_i = x_h + self.sides['B']
        x_g = x_h * -1
        x_f = x_i * -1

        # y-axis
        z_5 = (self.sides['E'] / 2)
        z_6 = z_5 + self.sides['D']
        z_7 = z_6 + self.sides['C']
        z_3 = z_5 * -1
        z_2 = z_6 * -1

        # calculate z-1 axis
        if not self.folds_overlap:
            z_1 = z_7 * -1
        else:
            z_1 = z_2 - self.sides['B']

        # calculate z-8 axis
        if not self.folds_overlap:
            z_8 = z_7 + self.sides['F']
        else:
            z_8 = z_7

        # Coordinates in world space
        self.gift_fold_points = {
            'F1': Vec(x_f, y_gft, z_1), 'F2': Vec(x_f, y_gft, z_2),
            'F3': Vec(x_f, y_gft, z_3),
            'F4': Vec(x_f + bc_diff, y_gft, 0.0),
            'F5': Vec(x_f, y_gft, z_5),
            'F6': Vec(x_f, y_gft, z_6),
            'F7': Vec(x_f, y_gft, z_7), 'F8': Vec(x_f, y_gft, z_8),
            'G1': Vec(x_g, y_gft, z_1),
            'G2': Vec(x_g, y_gft, z_2), 'G3': Vec(x_g, y_gft, z_3),
            'G4': Vec(x_g, y_gft, 0.0),
            'G5': Vec(x_g, y_gft, z_5), 'G6': Vec(x_g, y_gft, z_6),
            'G7': Vec(x_g - paper_thickness, y_gft, z_7),
            'G8': Vec(x_g - paper_thickness, y_gft, z_8),
            'H1': Vec(x_h, y_gft, z_1), 'H2': Vec(x_h, y_gft, z_2),
            'H3': Vec(x_h, y_gft, z_3),
            'H4': Vec(x_h, y_gft, 0.0), 'H5': Vec(x_h, y_gft, z_5),
            'H6': Vec(x_h, y_gft, z_6),
            'H7': Vec(x_h + paper_thickness, y_gft, z_7),
            'H8': Vec(x_h + paper_thickness, y_gft, z_8),
            'I1': Vec(x_i, y_gft, z_1),
            'I2': Vec(x_i, y_gft, z_2), 'I3': Vec(x_i, y_gft, z_3),
            'I4': Vec(x_i - self.sides['B'] + self.sides['C'], y_gft, 0.0),
            'I5': Vec(x_i, y_gft, z_5), 'I6': Vec(x_i, y_gft, z_6),
            'I7': Vec(x_i, y_gft, z_7),
            'I8': Vec(x_i, y_gft, z_8), 'I4a':Vec(x_i, y_gft, z_3)
        }

        # Diagonal folds -------------------------------------------------------

        # Calculate diagonal fold points F4a, F4b, I4a, I4b
        self.gift_fold_points['I4a'].z += self.sides['B']
        self.gift_fold_points['I4b'] = Vec(x_i, y_gft, z_5)
        self.gift_fold_points['I4b'].z -= self.sides['B']

        self.gift_fold_points['F4a'] = Vec(x_f, y_gft, z_3)
        self.gift_fold_points['F4a'].z += self.sides['B']
        self.gift_fold_points['F4b'] = Vec(x_f, y_gft, z_5)
        self.gift_fold_points['F4b'].z -= self.sides['B']

        # Calculate intersecting points HI4, FG4
        if self.folds_overlap:
            self.gift_fold_points['HI4'] = Vec(x_h, y_gft, 0.0)
            self.gift_fold_points['HI4'].x += self.sides['E'] / 2
            self.gift_fold_points['FG4'] = Vec(x_g, y_gft, 0.0)
            self.gift_fold_points['FG4'].x -= self.sides['E'] / 2

        # Calculate diagonal fold points F1a, I1a
        if not self.folds_overlap:
            self.gift_fold_points['I1a'] = Vec(x_i, y_gft, z_2)
            self.gift_fold_points['I1a'].z -= self.sides['B']
            self.gift_fold_points['F1a'] = Vec(x_f, y_gft, z_2)
            self.gift_fold_points['F1a'].z -= self.sides['B']
        else:
            self.gift_fold_points['I1a'] = Vec(x_i, y_gft, z_1)
            self.gift_fold_points['I1a'].z += bc_diff
            self.gift_fold_points['I1a'].x -= bc_diff
            self.gift_fold_points['F1a'] = Vec(x_f, y_gft, z_1)
            self.gift_fold_points['F1a'].z += bc_diff
            self.gift_fold_points['F1a'].x += bc_diff

        # Calculate diagonal fold points F1b, I1b
        if self.folds_overlap:
            self.gift_fold_points['I1b'] = Vec(x_i, y_gft, z_1)
            self.gift_fold_points['I1b'].z += bc_diff * 2
            self.gift_fold_points['F1b'] = Vec(x_f, y_gft, z_1)
            self.gift_fold_points['F1b'].z += bc_diff * 2

        # Calculate diagonal fold points F1c, I1c
        if self.folds_overlap:
            self.gift_fold_points['I1c'] = Vec(x_i, y_gft, z_1)
            self.gift_fold_points['I1c'].x -= bc_diff * 2
            self.gift_fold_points['F1c'] = Vec(x_f, y_gft, z_1)
            self.gift_fold_points['F1c'].x += bc_diff * 2

        # Calculate diagonal fold points F7a, I7a
        if not self.folds_overlap:
            self.gift_fold_points['I7a'] = Vec(x_i, y_gft, z_6)
            self.gift_fold_points['I7a'].z += self.sides['B']
            self.gift_fold_points['F7a'] = Vec(x_f, y_gft, z_6)
            self.gift_fold_points['F7a'].z += self.sides['B']
        else:
            self.gift_fold_points['I7a'] = Vec(x_i, y_gft, z_7)
            self.gift_fold_points['I7a'].x -= bc_diff
            self.gift_fold_points['F7a'] = Vec(x_f, y_gft, z_7)
            self.gift_fold_points['F7a'].x += bc_diff

        # Calculate diagonal fold points F7b, I7b
        if self.folds_overlap:
            self.gift_fold_points['I7b'] = Vec(x_i, y_gft, z_7)
            self.gift_fold_points['I7b'].z -= bc_diff
            self.gift_fold_points['F7b'] = Vec(x_f, y_gft, z_7)
            self.gift_fold_points['F7b'].z -= bc_diff

        # Padding folds --------------------------------------------------------
        thk = paper_thickness    # shorthand
                                 #     :.
                                 #     | ''.
                                 # leg |    /'.
        leg = thk * sqrt(2)      #     |  /thk '..
                                 #     |/_________:.
                                 #         leg

        # Calculate padding fold points F3x, F4xu, F4xus, F4xds, F4xd, F5x
        self.gift_fold_points['F3x'] = Vec(x_g - leg, y_gft, z_3)
        self.gift_fold_points['F4xu'] = Vec(x_g - thk - leg, y_gft, z_3 + thk)
        if not self.folds_overlap:
            z_xds = z_5 - self.sides['B'] + leg
            z_xus = z_3 + self.sides['B'] - leg
        else:
            z_xds = z_3 + self.sides['B'] - leg
            z_xus = z_5 - self.sides['B'] + leg
        self.gift_fold_points['F4xus'] = Vec(x_f, y_gft, z_xus)
        self.gift_fold_points['F4xds'] = Vec(x_f, y_gft, z_xds)
        self.gift_fold_points['F4xd'] = Vec(x_g - thk - leg, y_gft, z_5 - thk)
        self.gift_fold_points['F5x'] = Vec(x_g - leg, y_gft, z_5)

        # Calculate padding fold points F4x, F4y, F4z
        if self.folds_overlap:
            temp_xf = x_g - self.sides['E'] / 2
            self.gift_fold_points['F4x'] = Vec(temp_xf - leg, y_gft, 0.0)
            self.gift_fold_points['F4y'] = Vec(temp_xf - leg/2, y_gft, -leg/2)
            self.gift_fold_points['F4z'] = Vec(temp_xf - leg/2, y_gft, leg/2)

        # Calculate padding fold points F4u, F4d, F4us, F4ds
        self.gift_fold_points['F4u'] = Vec(x_g - thk, y_gft, z_3 + thk)
        self.gift_fold_points['F4d'] = Vec(x_g - thk, y_gft, z_5 - thk)
        self.gift_fold_points['F4us'] = Vec(x_f, y_gft, z_3 + thk)
        self.gift_fold_points['F4ds'] = Vec(x_f, y_gft, z_5 - thk)

        # Calculate padding fold points I4u, I4d, I4us, I4ds
        self.gift_fold_points['I4u'] = Vec(x_h + thk, y_gft, z_3 + thk)
        self.gift_fold_points['I4d'] = Vec(x_h + thk, y_gft, z_5 - thk)
        self.gift_fold_points['I4us'] = Vec(x_i, y_gft, z_3 + thk)
        self.gift_fold_points['I4ds'] = Vec(x_i, y_gft, z_5 - thk)

        # Calculate padding fold points I3x, I4xu, I4xus, I4xds, I4xd, I5x
        self.gift_fold_points['I3x'] = Vec(x_h + leg, y_gft, z_3)
        self.gift_fold_points['I4xu'] = Vec(x_h + thk + leg, y_gft, z_3 + thk)
        self.gift_fold_points['I4xus'] = Vec(x_i, y_gft, z_xus)
        self.gift_fold_points['I4xds'] = Vec(x_i, y_gft, z_xds)
        self.gift_fold_points['I4xd'] = Vec(x_h + thk + leg, y_gft, z_5 - thk)
        self.gift_fold_points['I5x'] = Vec(x_h + leg, y_gft, z_5)

        # Calculate padding fold points I4x, I4y, I4z
        if self.folds_overlap:
            temp_xi = x_h + self.sides['E'] / 2
            self.gift_fold_points['I4x'] = Vec(temp_xi + leg, y_gft, 0.0)
            self.gift_fold_points['I4y'] = Vec(temp_xi + leg/2, y_gft, -leg/2)
            self.gift_fold_points['I4z'] = Vec(temp_xi + leg/2, y_gft, leg/2)

        # Calculate padding fold points F1u, F1d, F1s, I1u, I1d, I1u
        self.gift_fold_points['F1u'] = Vec(x_g - thk, y_gft, z_1)
        self.gift_fold_points['F1d'] = Vec(x_g - thk, y_gft, z_2 - thk)
        self.gift_fold_points['F1s'] = Vec(x_f, y_gft, z_2 - thk)
        self.gift_fold_points['I1u'] = Vec(x_h + thk, y_gft, z_1)
        self.gift_fold_points['I1d'] = Vec(x_h + thk, y_gft, z_2 - thk)
        self.gift_fold_points['I1s'] = Vec(x_i, y_gft, z_2 - thk)

        # Calculate padding fold points F2x, F1xd, F1xm, F1xs,
        #                               I2x, I1xd, I1xm, I1xs
        self.gift_fold_points['F2x'] = Vec(x_g - leg, y_gft, z_2)
        self.gift_fold_points['F1xd'] = Vec(x_g - thk - leg, y_gft, z_2 - thk)
        self.gift_fold_points['I2x'] = Vec(x_h + leg, y_gft, z_2)
        self.gift_fold_points['I1xd'] = Vec(x_h + thk + leg, y_gft, z_2 - thk)
        if self.folds_overlap:
            tmp_xf = x_f + bc_diff
            tmp_xi = x_i - bc_diff
            tmp_z = z_1 + bc_diff + leg/2
            self.gift_fold_points['F1xm'] = Vec(tmp_xf - leg/2, y_gft, tmp_z)
            self.gift_fold_points['I1xm'] = Vec(tmp_xi + leg/2, y_gft, tmp_z)

        if self.folds_overlap:
            self.gift_fold_points['F1xs'] = Vec(x_f, y_gft, z_1 + leg)
            self.gift_fold_points['I1xs'] = Vec(x_i, y_gft, z_1 + leg)
        else:
            temp_z = z_2 - self.sides['B']
            self.gift_fold_points['F1xs'] = Vec(x_f, y_gft, temp_z + leg)
            self.gift_fold_points['I1xs'] = Vec(x_i, y_gft, temp_z + leg)


        # Calculate padding fold points F7u, F7s, F7d, F7m, F8d
        self.gift_fold_points['F7u'] = Vec(x_g - thk, y_gft, z_6 + thk)
        self.gift_fold_points['F7s'] = Vec(x_f, y_gft, z_6 + thk)
        if not self.folds_overlap:
            self.gift_fold_points['F7m'] = Vec(x_g - thk * 2, y_gft, z_7)
            self.gift_fold_points['F8d'] = Vec(x_g - thk * 2, y_gft, z_8)
        else:
            self.gift_fold_points['F7d'] = Vec(x_g - thk, y_gft, z_7)

        # Calculate padding fold points I7u, I7s, I7d, I7m, I8d
        self.gift_fold_points['I7u'] = Vec(x_h + thk, y_gft, z_6 + thk)
        self.gift_fold_points['I7s'] = Vec(x_i, y_gft, z_6 + thk)
        if not self.folds_overlap:
            self.gift_fold_points['I7m'] = Vec(x_h + thk * 2, y_gft, z_7)
            self.gift_fold_points['I8d'] = Vec(x_h + thk * 2, y_gft, z_8)
        else:
            self.gift_fold_points['I7d'] = Vec(x_h + thk, y_gft, z_7)

        # Calculate padding fold points F6x, F7xu, F7xs, F7xd,
        #                               I6x, I7xu, I7xs, I7xd
        self.gift_fold_points['F6x'] = Vec(x_g - leg, y_gft, z_6)
        self.gift_fold_points['F7xu'] = Vec(x_g - thk - leg, y_gft, z_6 + thk)
        self.gift_fold_points['I6x'] = Vec(x_h + leg, y_gft, z_6)
        self.gift_fold_points['I7xu'] = Vec(x_h + thk + leg, y_gft, z_6 + thk)
        if not self.folds_overlap:
            temp_z = z_6 + self.sides['B'] - leg
            self.gift_fold_points['F7xs'] = Vec(x_f, y_gft, temp_z)
            self.gift_fold_points['I7xs'] = Vec(x_i, y_gft, temp_z)
        else:
            temp_xf = x_f + bc_diff
            temp_xi = x_i - bc_diff
            self.gift_fold_points['F7xd'] = Vec(temp_xf - leg, y_gft, z_7)
            self.gift_fold_points['I7xd'] = Vec(temp_xi + leg, y_gft, z_7)

        # Calculate padding fold points F7xm, I7xm
        if self.folds_overlap:
            temp_xf = x_f + bc_diff
            temp_xi = x_i - bc_diff
            temp_z = z_7 - leg / 2
            self.gift_fold_points['F7xm'] = Vec(temp_xf - leg/2, y_gft, temp_z)
            self.gift_fold_points['I7xm'] = Vec(temp_xi + leg/2, y_gft, temp_z)

        # Other points ---------------------------------------------------------
        self.gift_fold_points['G2o'] = Vec(x_g, y_gft, z_2 + thk)
        self.gift_fold_points['H2o'] = Vec(x_h, y_gft, z_2 + thk)
        self.gift_fold_points['G3o'] = Vec(x_g, y_gft, z_3 - thk)
        self.gift_fold_points['H3o'] = Vec(x_h, y_gft, z_3 - thk)
        self.gift_fold_points['G5o'] = Vec(x_g, y_gft, z_5 + thk)
        self.gift_fold_points['H5o'] = Vec(x_h, y_gft, z_5 + thk)
        self.gift_fold_points['G6o'] = Vec(x_g, y_gft, z_6 - thk)
        self.gift_fold_points['H6o'] = Vec(x_h, y_gft, z_6 - thk)

    def point(self, point_id):
        return self.gift_fold_points[point_id]

    def getSideLength(self, side_id):
        return self.sides[side_id]

    def hasOverlappingFolds(self):
        return self.folds_overlap

    def getFlapLength(self):
        return self.flap_length

    def getPaperThickness(self):
        return self.paper_thickness

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
           |     |               |     |     ^
           |     |       :       |     |     |-- D
           |     |               |     |     |
        6_ |_____|_______________|_____|     v
           |    ¤|               |¤    |   ^
     (a+b),|  ¤  |       :       |  ¤  |   |-- C
        7_ |%_ _ |_ _ _ _ _ _ _ _|_ _ %|   v
           |     |               |     |     ^-- F (Only present
        8_ |_____|_______________|_____|     v      when no overlap)
                         :
           <= B =>               <= B =>
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
  :  |     .   xm    :   :
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
