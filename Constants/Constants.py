from pathlib import Path
from typing import List

import wx.lib.newevent
from wx import Size

CheckboxChangedEvent, EVT_CHECKBOX_CHANGED = wx.lib.newevent.NewCommandEvent()

config_file: Path = Path.home() / '.config' / 'w-hinter.conf'

color_grey: wx.Colour = wx.Colour(158, 162, 168)
color_black: wx.Colour = wx.Colour(0, 0, 0)

status_places: int = 4
status_proportions: List[int] = [-6, -7, -3, -4]

main_window_size: Size = Size(1000, 800)
default_border: int = 3

icon_tool_height: int = 25
icon_tool_width: int = 25

style_default: str = "default"
style_bold: str = "bold"
style_italic: str = "italic"
style_bold_italic: str = "italic,bold"
style_break: str = "break"

style_map = {style_default: 0,
             style_bold: 1,
             style_italic: 2,
             style_bold_italic: 3}

about_dialog_width: int = 300
about_dialog_height: int = 300

words_dialog_width: int = 400
words_dialog_height: int = 900

plain_text_dialog_width: int = 400
plain_text_dialog_height: int = 600

word_list_width: int = 220

html_wildcard: str = "HTML files (*.html)|*.html"

config_min_repetitions: int = 2
config_min_repetitions_default: int = 3
config_max_repetitions: int = 100

config_min_len: int = 1
config_min_len_default: int = 3
config_max_len: int = 100

static_box_font_size: int = 9
statistics_timer_delay: int = 10000

report_name_lines: str = 'nl'
report_names_capitalized: str = 'nc'
report_leftover: str = 'left'
report_repetition: str = 'rep'
report_similar: str = 'sim'

msg_reply: int = 0
msg_info: int = 1
msg_warn: int = 2
msg_err: int = 3
