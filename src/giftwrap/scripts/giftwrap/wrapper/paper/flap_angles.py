def calculateFirstFlapAngle(flap_length, paper_thickness, is_upper=True):
    """
    Calculates the angle by which the first flap should be rotated, so that
    its underside lays flush with the side of the wrapped paper's bounding box.
    (See diagram at the bottom of this file for more details)

    Args:
        flap_length: length of the flap in maya units
        paper_thickness: thickness of the paper in maya units
        is_upper: True if the first flap is on top (Inverts the angle if not)
    """


"""
Flaps diagram:

                         Side of the
                       wrapped paper's
                         bounding box
                              |
                              v
                              :
 _______ _____________________:_______
|_______:_:_________________:_:_______|
        : :                 : :
        : :                 : :__  First flap
        : :                 : / /     :
        : :                 :/:/ <---"
 _______:_:_________________/ /
|_______:_:_________________:'


                           Side of the
                          first flap when
                              folded
                                |
                                v
                                :
 _______ ______________________ :
|_______:_:_________________:_:'\
        : :                 : :\:\  Second flap
        : :                 : :_: \     :
        : :                 : / /\_\ <-"
        : :                 :/ /:
 _______:_:_________________/ / :
|_______:_:_________________:'  :


"""
