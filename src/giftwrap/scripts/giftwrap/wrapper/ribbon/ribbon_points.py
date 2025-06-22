from ...utils.custom_types.vec import Vec

def getRibbonPoints(obj_width, obj_height, obj_depth, paper_thickness,
                    ribbon_thickness, ribbon_width):
    """
    Calculate the coordinates of the nurbs curve controlling the
    extrusion of the ribbon surface.

    Args:
        obj_width:        Width of the object to be wrapped.
        obj_height:       Height of the object to be wrapped.
        obj_depth:        Depth of the object to be wrapped.
        paper_thickness:  Thickness of the paper mesh.
        ribbon_thickness: The thickness of the ribbon.
        ribbon_width:     The width of the ribbon.

    Returns:
        A dictionary with the following format: { <Side ID>: Position (Vec) }
        (See the diagram at the bottom of this file for details)
    """
    print(f'Object width: {obj_width}')

    def _cpVec(xyz):
        """Deep copies Vec"""
        return Vec(xyz.x, xyz.y, xyz.z)

    wrapped_width = obj_width + 2 * ribbon_thickness
    y_pos = obj_height + paper_thickness * 2 + (ribbon_thickness / 3)
    x_pos = (obj_width / 2) + (ribbon_thickness / 2 + paper_thickness)
    z_pos = (obj_depth / 2) + (ribbon_thickness / 2 + paper_thickness)
    edg_m = paper_thickness / 2  # edge margin
    mid_c = 0.5  # mid point coefficient
    end_m = 2 * paper_thickness  # end point margin
    x_pos_m = paper_thickness * 3 # width (L and R) margin
    x_edge = (wrapped_width / 2)  # + thickness + (r_thickness / 2)
    half_h = obj_height * 0.5
    y_3rd = y_pos / 3
    qrt_y = y_pos / 4

    # ==========================================================================
    # Ribbon points
    # ==========================================================================

    pts = {
        'U': Vec(0, y_pos, 0),       'D': Vec(0, 0, 0),
        'L': Vec(-x_pos, half_h, 0), 'R': Vec(x_pos, half_h, 0),
        'F': Vec(0, half_h, z_pos),  'B': Vec(0, half_h, -z_pos)}

    # Upper side ===============================================================
    pts['UL'] = Vec(-x_edge, pts['U'].y, pts['U'].z)
    pts.update({
        'ULmid': Vec(pts['UL'].x * mid_c, pts['UL'].y, pts['UL'].z),
        'ULend': Vec(pts['UL'].x + end_m * 2, pts['UL'].y, pts['UL'].z)})

    pts['UR'] = Vec(x_edge, pts['U'].y, pts['U'].z)
    pts.update({
        'URmid': Vec(pts['UR'].x * mid_c, pts['UR'].y, pts['UR'].z),
        'URend': Vec(pts['UR'].x - end_m * 2, pts['UR'].y, pts['UR'].z)})

    pts['UB'] = Vec(pts['U'].x, pts['U'].y, pts['B'].z + edg_m)
    pts.update({
        'UBmid': Vec(pts['UB'].x, pts['UB'].y, pts['UB'].z * mid_c),
        'UBend': Vec(pts['UB'].x, pts['UB'].y, pts['UB'].z + end_m)})

    pts['UF'] = Vec(pts['U'].x, pts['U'].y, pts['F'].z - edg_m)
    pts.update({
        'UFmid': Vec(pts['UF'].x, pts['UF'].y, pts['UF'].z * mid_c),
        'UFend': Vec(pts['UF'].x, pts['UF'].y, pts['UF'].z - end_m)})

    # Downside  ================================================================
    pts['DL'] = Vec(-x_edge, pts['D'].y, pts['D'].z)
    pts.update({
        'DLmid': Vec(pts['DL'].x * mid_c, pts['DL'].y, pts['DL'].z),
        'DLend': Vec(pts['DL'].x + end_m * 2, pts['DL'].y, pts['DL'].z)})

    pts['DR'] = Vec(x_edge, pts['D'].y, pts['D'].z)
    pts.update({
        'DRmid': Vec(pts['DR'].x * mid_c, pts['DR'].y, pts['DR'].z),
        'DRend': Vec(pts['DR'].x - end_m * 2, pts['DR'].y, pts['DR'].z)})

    pts['DB'] = Vec(pts['D'].x, pts['D'].y, pts['B'].z + edg_m)
    pts.update({
        'DBmid': Vec(pts['DB'].x, pts['DB'].y, pts['DB'].z * mid_c),
        'DBend': Vec(pts['DB'].x, pts['DB'].y, pts['DB'].z + end_m)})

    pts['DF'] = Vec(pts['D'].x, pts['D'].y, pts['F'].z - edg_m)
    pts.update({
        'DFmid': Vec(pts['DF'].x, pts['DF'].y, pts['DF'].z * mid_c),
        'DFend': Vec(pts['DF'].x, pts['DF'].y, pts['DF'].z - end_m)})

    # Left side ================================================================
    pts['LU'] = Vec(-(x_edge + x_pos_m), pts['U'].y - edg_m, pts['L'].z)
    diff_x = pts['LU'].x - pts['L'].x
    pts.update({
        'LUmid': Vec(pts['L'].x + diff_x / 2, pts['L'].y + qrt_y , pts['L'].z),
        'LUend': Vec(pts['LU'].x - x_pos_m, pts['LU'].y - end_m, pts['LU'].z)})

    pts['LD'] = Vec(-(x_edge + x_pos_m), pts['D'].y + edg_m, pts['L'].z)
    pts.update({
        'LDmid': Vec(pts['L'].x, pts['L'].y - y_3rd, pts['L'].z),
        'LDend': Vec(pts['LU'].x - x_pos_m, pts['LD'].y + end_m, pts['LU'].z)})

    pts['LB'] = Vec(pts['L'].x, pts['L'].y, pts['B'].z + edg_m)
    pts.update({
        'LBmid': Vec(pts['LB'].x, pts['LB'].y , pts['LB'].z * mid_c),
        'LBend': Vec(pts['LB'].x, pts['LB'].y, pts['LB'].z + end_m)})

    pts['LF'] = Vec(pts['L'].x, pts['L'].y, pts['F'].z + edg_m)
    pts.update({
        'LFmid': Vec(pts['LF'].x, pts['LF'].y, pts['LF'].z * mid_c),
        'LFend': Vec(pts['LF'].x, pts['LF'].y, pts['LF'].z - end_m)})

    # Right side ===============================================================
    pts['RU'] = Vec(x_edge + x_pos_m, pts['U'].y - edg_m, pts['R'].z)
    pts.update({
        'RUmid': Vec(x_edge + x_pos_m, pts['R'].y + qrt_y , pts['R'].z),
        'RUend': Vec(pts['RU'].x + x_pos_m, pts['RU'].y - end_m, pts['RU'].z)})

    pts['RD'] = Vec(x_edge + x_pos_m, pts['D'].y + edg_m, pts['R'].z)
    pts.update({
        'RDmid': Vec(pts['R'].x, pts['R'].y - y_3rd, pts['R'].z),
        'RDend': Vec(pts['RU'].x + x_pos_m, pts['RD'].y + end_m, pts['RU'].z)})

    pts['RB'] = Vec(pts['R'].x, pts['R'].y, pts['B'].z + edg_m)
    pts.update({
        'RBmid': Vec(pts['RB'].x, pts['RB'].y , pts['RB'].z * mid_c),
        'RBend': Vec(pts['RB'].x, pts['RB'].y, pts['RB'].z + end_m)})

    pts['RF'] = Vec(pts['R'].x, pts['R'].y, pts['F'].z - edg_m)
    pts.update({
        'RFmid': Vec(pts['RF'].x, pts['RF'].y, pts['RF'].z * mid_c),
        'RFend': Vec(pts['RF'].x, pts['RF'].y, pts['RF'].z - end_m)})

    # Back side ================================================================
    pts['BU'] = Vec(pts['B'].x, pts['U'].y - edg_m, pts['B'].z)
    pts.update({
        'BUmid': Vec(pts['B'].x, pts['B'].y + qrt_y , pts['B'].z),
        'BUend': Vec(pts['BU'].x, pts['BU'].y - end_m, pts['BU'].z)})

    pts['BD'] = Vec(pts['B'].x, pts['D'].y + edg_m, pts['B'].z)
    pts.update({
        'BDmid': Vec(pts['BD'].x, pts['BD'].y + qrt_y, pts['BD'].z),
        'BDend': Vec(pts['BD'].x, pts['BD'].y + end_m, pts['BD'].z)})

    pts['BL'] = Vec(pts['L'].x + edg_m, pts['B'].y, pts['B'].z)
    pts.update({
        'BLmid': Vec(pts['BL'].x * mid_c, pts['BL'].y, pts['BL'].z),
        'BLend': Vec(pts['BL'].x + end_m, pts['BL'].y, pts['BL'].z)})

    pts['BR'] = Vec(pts['R'].x - edg_m, pts['B'].y, pts['B'].z)
    pts.update({
        'BRmid': Vec(pts['BR'].x * mid_c, pts['BR'].y, pts['BR'].z),
        'BRend': Vec(pts['BR'].x - end_m, pts['BR'].y, pts['BR'].z)})

    # Front side ===============================================================
    pts['FU'] = Vec(pts['F'].x, pts['U'].y - edg_m, pts['F'].z)
    pts.update({
        'FUmid': Vec(pts['FU'].x, pts['FU'].y - qrt_y , pts['FU'].z),
        'FUend': Vec(pts['FU'].x, pts['FU'].y - end_m, pts['FU'].z)})

    pts['FD'] = Vec(pts['F'].x, pts['D'].y + edg_m, pts['F'].z)
    pts.update({
        'FDmid': Vec(pts['FD'].x, pts['FD'].y + qrt_y, pts['FD'].z),
        'FDend': Vec(pts['FD'].x, pts['FD'].y + end_m, pts['FD'].z)})

    pts['FL'] = Vec(pts['L'].x + edg_m, pts['F'].y, pts['F'].z)
    pts.update({
        'FLmid': Vec(pts['FL'].x * mid_c, pts['FL'].y, pts['FL'].z),
        'FLend': Vec(pts['FL'].x + end_m, pts['FL'].y, pts['FL'].z)})

    pts['FR'] = Vec(pts['R'].x - edg_m, pts['F'].y, pts['F'].z)
    pts.update({
        'FRmid': Vec(pts['FR'].x * mid_c, pts['FR'].y, pts['FR'].z),
        'FRend': Vec(pts['FR'].x - end_m, pts['FR'].y, pts['FR'].z)})

    # ==========================================================================
    # Bow Points
    # ==========================================================================
    loop_width = obj_width / 3
    loop_height = obj_width / 4
    half_rib_w = ribbon_width / 2
    qrt_rib_w = ribbon_width / 4
    rib_w_85 = ribbon_width * 0.85
    half_rib_thk = ribbon_thickness / 2
    half_w = obj_width / 2
    half_lp_w = loop_width / 2
    half_lp_h = loop_height / 2

    # Left Loop ================================================================
    pts.update({
        'bow_L1': _cpVec(pts['U']),
        'bow_L2': Vec(-loop_width, pts['U'].y + ribbon_thickness, pts['U'].z)})
    pts.update({
        'bow_L3': Vec(pts['bow_L2'].x - half_rib_w, pts['bow_L2'].y + half_lp_h,
                      pts['bow_L2'].z),
        'bow_L4': Vec(pts['bow_L2'].x + qrt_rib_w,
                      pts['bow_L2'].y + loop_height,
                      pts['bow_L2'].z),
        'bow_L5': Vec(pts['bow_L1'].x - rib_w_85,
                      pts['bow_L1'].y + ribbon_thickness,
                      pts['bow_L1'].z)})
    pts.update({
        'bow_L6': Vec(pts['bow_L5'].x + half_rib_w, pts['bow_L5'].y,
                      pts['bow_L5'].z),
        'bow_L7': Vec(pts['bow_L1'].x, pts['bow_L1'].y + half_rib_thk,
                      pts['bow_L1'].z),
    })

    # Right Loop ================================================================
    pts.update({
        'bow_R1': _cpVec(pts['U']),
        'bow_R2': Vec(loop_width, pts['U'].y + ribbon_thickness, pts['U'].z)})
    pts.update({
        'bow_R3': Vec(pts['bow_R2'].x + half_rib_w, pts['bow_R2'].y + half_lp_h,
                      pts['bow_R2'].z),
        'bow_R4': Vec(pts['bow_R2'].x - qrt_rib_w,
                      pts['bow_R2'].y + loop_height,
                      pts['bow_R2'].z),
        'bow_R5': Vec(pts['bow_R1'].x + rib_w_85,
                      pts['bow_R1'].y + ribbon_thickness,
                      pts['bow_R1'].z)})
    pts.update({
        'bow_R6': Vec(pts['bow_R5'].x - half_rib_w, pts['bow_R5'].y,
                      pts['bow_R5'].z),
        'bow_R7': Vec(pts['bow_R1'].x, pts['bow_R1'].y + half_rib_thk,
                      pts['bow_R1'].z),
    })

    # ==========================================================================
    # Knot
    # ==========================================================================

    pts['knot_1'] = Vec(pts['U'].x, pts['U'].y, pts['U'].z + half_rib_w)
    pts.update({
        'knot_2': Vec(pts['knot_1'].x, pts['knot_1'].y + half_rib_thk,
                      pts['knot_1'].z),
        'knot_3': Vec(pts['U'].x, pts['U'].y + ribbon_thickness * 2,
                      pts['U'].z)})
    pts.update({
        'knot_4': Vec(pts['knot_2'].x, pts['knot_2'].y + ribbon_width * 0.15,
                      pts['knot_2'].z - ribbon_width * 1.5),
        'knot_5': Vec(pts['U'].x, pts['U'].y, pts['U'].z - half_rib_w)})

    # ==========================================================================
    # Left End
    # ==========================================================================
    pts['end_L1'] = Vec(pts['U'].x, pts['U'].y, pts['U'].z + half_rib_w)

    return pts

"""
    Sides notation:
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
