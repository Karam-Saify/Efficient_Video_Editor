"""Caption style presets and zoom limits (H-0025): one table shared by the validator, the renderer and the ops.

Every preset uses the EXP-008 font pair at Regular weight (style font Noto Sans Arabic, Latin runs tagged
`{\\fnNoto Sans}` by src/render/fontrun.py) and ASS `Encoding: -1`, so RTL and LTR lines get libass's
first-strong-character base direction (E6). No preset is bold: EXP-008 declared only the Regular files.

  clean     white text, black outline, bottom third (the H-0024 default look)
  bold_box  white text on a semi-opaque black box (ASS BorderStyle 3), bottom third; "bold" means the box,
            not the font weight
  hook      large yellow text, black outline, upper third (attention line at the start of a Short)

A caption without `style` renders as `clean`. Any other style name is UNSUPPORTED_FIELD in src.validate.
"""
from __future__ import annotations

from typing import Any

DEFAULT_PRESET = "clean"

# ASS numpad alignment: 2 = bottom centre, 8 = top centre. Colours are #RRGGBB; alpha 0 = opaque, 255 = clear.
CAPTION_PRESETS: dict[str, dict[str, Any]] = {
    "clean": {"size": 80, "color": "#FFFFFF", "outline_color": "#000000", "outline_alpha": 0,
              "back_color": "#000000", "back_alpha": 128, "border_style": 1, "outline": 4, "shadow": 0,
              "alignment": 2, "margin_v": 320},
    "bold_box": {"size": 76, "color": "#FFFFFF", "outline_color": "#000000", "outline_alpha": 64,
                 "back_color": "#000000", "back_alpha": 64, "border_style": 3, "outline": 18, "shadow": 0,
                 "alignment": 2, "margin_v": 340},
    "hook": {"size": 104, "color": "#FFD400", "outline_color": "#000000", "outline_alpha": 0,
             "back_color": "#000000", "back_alpha": 128, "border_style": 1, "outline": 6, "shadow": 2,
             "alignment": 8, "margin_v": 420},
}

# Zoom = punch-in (src/render): centre crop by 1/scale, scaled back to the canvas, instant in and out.
ZOOM_MIN_SCALE = 1.0
ZOOM_MAX_SCALE = 2.0
ZOOM_DEFAULT_SCALE = 1.2
