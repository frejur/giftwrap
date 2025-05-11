"""
Various constants used for setting up the window layout and controls
"""

# Window
WIN_NAME     = 'giftWrapWindow'
WIN_W        = 320
WIN_X_MARGIN = 10

# Spacing
ROW_SP = 0
COL_SP = 2

# Fonts
FNT_SM = 'smallBoldLabelFont'

# Column width helper variables: Window width / X
COL_X_2 = (WIN_W - WIN_X_MARGIN) / 2
COL_X_3 = (WIN_W - WIN_X_MARGIN) / 3
COL_X_4 = (WIN_W - WIN_X_MARGIN) / 4
COL_X_5 = (WIN_W - WIN_X_MARGIN) / 5
COL_X_6 = (WIN_W - WIN_X_MARGIN) / 6

# Separators
H_SEP_H = 10
V_SEP_W = 10

# Column width layouts
COLS_1_1_2   = (COL_X_4, COL_X_4, COL_X_2)
COLS_2_2     = (COL_X_2, COL_X_2)
               # Vertical separator in-between columns
COLS_1_SEP_1 = (COL_X_2 - V_SEP_W / 2, V_SEP_W, COL_X_2 - V_SEP_W / 2)
COLS_4       = (COL_X_4, COL_X_4, COL_X_4, COL_X_4)

# Paper-and-Ribbon column layout
COL_PAPER_RIBBON_L = (COL_X_4 - V_SEP_W / 2) * 0.85
COL_PAPER_RIBBON_R = (COL_X_4 - V_SEP_W / 2) * 1.15
COLS_PAPER_RIBBON  = (COL_PAPER_RIBBON_L, COL_PAPER_RIBBON_R)
SEP_PAPER_RIBBON_H = 70

# Animation Range column layout
COL_ANIM_L   = COL_X_4 * 0.85
COL_ANIM_GAP = 8
COL_ANIM_M   = COL_X_4 * 0.45
COL_ANIM_R   = COL_X_4 * 0.45
COLS_ANIM    = (COL_ANIM_L, COL_ANIM_M, COL_ANIM_GAP, COL_ANIM_R)

# Animation Toggles column layout
COL_ANIM_TGL_L  = COL_X_4 * 0.3
COL_ANIM_TGL_R  = COL_X_4 * 1.7
COLS_ANIM_TGL   = (COL_ANIM_TGL_L, COL_ANIM_TGL_R)
SEP_ANIM_WRAP_H = 70

# Wrap button column layout
BTN_WRAP_H = 40
COL_WRAP_L = COL_X_4 * 0.5
COL_WRAP_M = COL_X_4 * 1.0
COL_WRAP_R = COL_X_4 * 0.5
COLS_WRAP = (COL_WRAP_L, COL_WRAP_M, COL_WRAP_R)
COLS_KEEP = (COL_WRAP_L, COL_WRAP_M + COL_WRAP_R)

# Fine tuning column layout
COL_FINE_TUNE_L = 10
COL_FINE_TUNE_R = WIN_W - COL_FINE_TUNE_L - WIN_X_MARGIN
COLS_FINE_TUNE = (COL_FINE_TUNE_L, COL_FINE_TUNE_R)
                 # To use with rowLayout and counter padding / margin
COL_FINE_TUNE_R_ADJ = COL_FINE_TUNE_R - COL_FINE_TUNE_L * 0.9

# Orientation and placement column layout
ORIENT_TITLE_BG = (0.20, 0.20, 0.20)
ORIENT_BG       = (0.24, 0.24, 0.24)
ORIENT_MENU_BG  = (0.32, 0.32, 0.32)
COL_ORI_UP_1    = COL_FINE_TUNE_R_ADJ * 0.15
COL_ORI_UP_2    = COL_FINE_TUNE_R_ADJ * 0.25
COL_ORI_UP_3    = COL_FINE_TUNE_R_ADJ * 0.10
COL_ORI_UP_4    = COL_FINE_TUNE_R_ADJ * 0.30
COL_ORI_UP_5    = COL_FINE_TUNE_R_ADJ * 0.20
COLS_ORI_UP     = (COL_ORI_UP_1, COL_ORI_UP_2, COL_ORI_UP_3, COL_ORI_UP_4,
                   COL_ORI_UP_5)
COL_PLACE_1     = COL_FINE_TUNE_R_ADJ * 0.200
COL_PLACE_2     = COL_FINE_TUNE_R_ADJ * 0.425
COL_PLACE_3     = COL_FINE_TUNE_R_ADJ * 0.150
COL_PLACE_4     = COL_FINE_TUNE_R_ADJ * 0.225
COLS_PLACE      = (COL_PLACE_1, COL_PLACE_2, COL_PLACE_3, COL_PLACE_4)
