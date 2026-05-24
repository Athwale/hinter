from pathlib import Path
import wx.lib.newevent

from wx import Size

CheckboxChangedEvent, EVT_CHECKBOX_CHANGED = wx.lib.newevent.NewCommandEvent()

config_file: Path = Path.home() / '.config' / 'w-hinter.conf'

main_window_size: Size = Size(1000, 800)
default_border: int = 3

icon_tool_height: int = 16
icon_tool_width: int = 16

style_default: str = "default"
style_bold: str = "bold"
style_italic: str = "italic"
style_bold_italic: str = "italic,bold"
style_break: str = "break"

about_dialog_width: int = 300
about_dialog_height: int = 300

words_dialog_width: int = 400
words_dialog_height: int = 900

word_list_width: int = 220

html_wildcard: str = "HTML files (*.html)|*.html"

config_min_repetitions: int = 2
config_min_repetitions_default: int = 3
config_max_repetitions: int = 100

config_min_len: int = 1
config_min_len_default: int = 3
config_max_len: int = 100

static_box_font_size: int = 9

statistics_delay: int = 3000