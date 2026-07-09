import html
import re
import shutil
import time
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Set

import wx
import wx.dataview as dv
import wx.grid
import wx.lib.scrolledpanel
import wx.stc as stc
from wx import ToolBarToolBase
from wx._core import StatusBar, ToolBar
from wx.svg import SVGimage

from Constants import Constants
from Constants import Strings
from Constants.Constants import EVT_CHECKBOX_CHANGED
from Containers.Document import Document
from Containers.ListItemPanel import ListItemPanel
from Containers.SidePanel import SidePanel
from Containers.Word import Word
from Dialogs.AboutDialog import AboutDialog
from Dialogs.PlainTextEditDialog import PlainTextEditDialog
from Dialogs.SaveLoadWaitDialog import SavingWaitDialog
from Dialogs.WordInfoDialog import WordInfoDialog
from Resources.Fetch import Fetch
from Threads.ColoratorThread import ColoratorThread
from Threads.LoadFileThread import LoadFileThread
from Threads.SaveFileThread import SaveFileThread
from Threads.StatisticsThread import StatisticsThread
from Tools.Config import Config


# todo spell check
# todo ai integration

class MainFrame(wx.Frame):
    """
    Main user interface class.
    """

    def __init__(self):
        """
        User interface constructor.
        """
        super(MainFrame, self).__init__(None, title=Strings.app_title.format(Strings.status_no_document),
                                        size=Constants.main_window_size)

        self.SetMinSize(Constants.main_window_size)

        self._current_document: Document = None

        self._main_text_field: stc.StyledTextCtrl = None
        self._repetition_selector: wx.SpinCtrl = None
        self._min_repeated_word_length_selector: wx.SpinCtrl = None
        self._max_repeated_word_length_selector: wx.SpinCtrl = None
        self._search_text_field: wx.TextCtrl = None
        self._log_text_field: wx.TextCtrl = None
        self._input_text_field: wx.TextCtrl = None
        self._search_button_up: wx.BitmapButton = None
        self._search_button_down: wx.BitmapButton = None
        self._search_results: wx.StaticText = None
        self._status_bar: StatusBar = None
        self._toolbar: ToolBar = None
        self._tools: List[wx.ToolBarToolBase] = []
        self._menu_items: List[wx.MenuItem] = []
        self._side_word_list: SidePanel = None
        self._splitter: wx.SplitterWindow = None

        # Used for undo.
        self._style_history = {}
        self._action_token = 0

        # Custom IDs
        self._id_add_ignore = wx.NewId()
        self._id_add_names = wx.NewId()
        self._id_del_ignore = wx.NewId()
        self._id_del_names = wx.NewId()
        self._id_limits = wx.NewId()
        self._id_synonym_ids = []

        self._available_indicators: Set[int] = set()
        self._selected_words: List[str] = []
        self._coloring_tool_off: bool = True

        self._found_words: List[tuple[tuple[int, int], int]] = []
        self._found_last_index = 0

        self._waiting_dialog: SavingWaitDialog = SavingWaitDialog(self)

        self._log_up: bool = False

        self._statistics_thread: StatisticsThread = None
        self._statistics_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_statistics_timer, self._statistics_timer)

        # Init layout:
        self._init_menu_bar()
        self._init_tool_bar()
        self._init_main_layout()
        self._init_status_bar()
        self._init_styles()
        self._disable_editor()
        self._set_status_text(Strings.status_ready, 0)
        self._set_status_text(Strings.status_no_document, 1)

        # Load configuration on startup.
        self._config = Config()
        if self._config.get_last_file() != Path():
            wx.CallAfter(self._on_fully_loaded)

        # todo
        self.post_message(Strings.msg_init, Constants.msg_info)

    # Layout ---------------------------------------------------------------------------------------------------------------
    def _init_menu_bar(self) -> None:
        """
        Menu bar initialization.
        :return: None
        """
        # Init menu bar.
        menubar = wx.MenuBar()

        # File menu:
        file_menu = wx.Menu()
        # Standard id will automatically add an icon and a shortcut.
        # Last parameter defines the short help string that is displayed on the statusbar.
        file_menu_item_new = file_menu.Append(wx.ID_NEW, Strings.menu_item_new, Strings.menu_item_new_hint)
        self._menu_items.append(file_menu_item_new)
        file_menu_item_open = file_menu.Append(wx.ID_OPEN, Strings.menu_item_open, Strings.menu_item_open_hint)
        self._menu_items.append(file_menu_item_open)
        file_menu_item_save = file_menu.Append(wx.ID_SAVE, Strings.menu_item_save, Strings.menu_item_save_hint)
        self._menu_items.append(file_menu_item_save)
        file_menu_item_save_as = file_menu.Append(wx.ID_SAVEAS, Strings.menu_item_save_as,
                                                  Strings.menu_item_save_as_hint)
        self._menu_items.append(file_menu_item_save_as)
        file_menu.AppendSeparator()
        file_menu_item_quit = file_menu.Append(wx.ID_EXIT, Strings.menu_item_quit, Strings.menu_item_quit_hint)
        self._menu_items.append(file_menu_item_quit)

        # Edit menu:
        edit_menu = wx.Menu()
        edit_menu_item_undo = edit_menu.Append(wx.ID_UNDO, Strings.menu_item_undo, Strings.menu_item_undo_hint)
        self._menu_items.append(edit_menu_item_undo)
        edit_menu_item_redo = edit_menu.Append(wx.ID_REDO, Strings.menu_item_redo, Strings.menu_item_redo_hint)
        self._menu_items.append(edit_menu_item_redo)
        edit_menu.AppendSeparator()

        edit_menu_item_bold = edit_menu.Append(wx.ID_BOLD, Strings.menu_item_bold, Strings.menu_item_bold_hint)
        self._menu_items.append(edit_menu_item_bold)
        edit_menu_item_italic = edit_menu.Append(wx.ID_ITALIC, Strings.menu_item_italic, Strings.menu_item_italic_hint)
        self._menu_items.append(edit_menu_item_italic)
        edit_menu_item_remove_styles = edit_menu.Append(wx.ID_CLEAR, Strings.menu_item_clear,
                                                        Strings.menu_item_clear_hint)
        self._menu_items.append(edit_menu_item_remove_styles)
        edit_menu.AppendSeparator()

        self._id_ignored = wx.NewId()
        edit_menu_item_ignored = edit_menu.Append(self._id_ignored, Strings.menu_item_edit_words_ignored,
                                                  Strings.menu_item_edit_words_ignored_hint)
        self._menu_items.append(edit_menu_item_ignored)
        self._id_names = wx.NewId()
        edit_menu_item_names = edit_menu.Append(self._id_names, Strings.menu_item_edit_words_names,
                                                Strings.menu_item_edit_words_names_hint)
        self._menu_items.append(edit_menu_item_names)
        self._id_edit_synonyms = wx.NewId()
        edit_menu_item_synonyms = edit_menu.Append(self._id_edit_synonyms, Strings.menu_item_edit_words_synonyms,
                                                   Strings.menu_item_edit_words_synonyms_hint)
        self._menu_items.append(edit_menu_item_synonyms)

        # Tools menu:
        tools_menu = wx.Menu()
        tools_menu_item_words = tools_menu.Append(wx.ID_INFO, Strings.menu_item_word_list,
                                                  Strings.menu_item_word_list_hint)
        self._menu_items.append(tools_menu_item_words)
        tools_menu_item_reset = tools_menu.Append(wx.ID_RESET, Strings.menu_item_reset,
                                                  Strings.menu_item_reset_hint)
        self._menu_items.append(tools_menu_item_reset)
        tools_menu_item_log = tools_menu.Append(wx.ID_UP, Strings.menu_item_log,
                                                Strings.menu_item_log_hint)
        self._menu_items.append(tools_menu_item_log)

        # About menu:
        about_menu = wx.Menu()
        about_menu_item_about = about_menu.Append(wx.ID_ABOUT, Strings.menu_item_about, Strings.menu_item_about_hint)
        self._menu_items.append(about_menu_item_about)

        menubar.Append(file_menu, Strings.menu_file)
        menubar.Append(edit_menu, Strings.menu_edit)
        menubar.Append(tools_menu, Strings.menu_tools)
        menubar.Append(about_menu, Strings.menu_about)

        # Bind menu item handlers.
        # File menu:
        self.Bind(wx.EVT_MENU, self._quit_handler, file_menu_item_quit)
        self.Bind(wx.EVT_MENU, self._open_file, file_menu_item_open)
        self.Bind(wx.EVT_MENU, self._save_file_handler, file_menu_item_save)
        self.Bind(wx.EVT_MENU, self._save_as_file_handler, file_menu_item_save_as)
        self.Bind(wx.EVT_MENU, self._new_file_handler, file_menu_item_new)

        # Edit menu:
        self.Bind(wx.EVT_MENU, self._clear_styles_handler, edit_menu_item_remove_styles)
        self.Bind(wx.EVT_MENU, self._undo_handler, edit_menu_item_undo)
        self.Bind(wx.EVT_MENU, self._redo_handler, edit_menu_item_redo)
        self.Bind(wx.EVT_MENU, self._make_bold_handler, edit_menu_item_bold)
        self.Bind(wx.EVT_MENU, self._make_italic_handler, edit_menu_item_italic)
        self.Bind(wx.EVT_MENU, self._edit_words_handler, edit_menu_item_names)
        self.Bind(wx.EVT_MENU, self._edit_words_handler, edit_menu_item_ignored)
        self.Bind(wx.EVT_MENU, self._edit_words_handler, edit_menu_item_synonyms)

        # Tools menu:
        self.Bind(wx.EVT_MENU, self._info_word_counts_handler, tools_menu_item_words)
        self.Bind(wx.EVT_MENU, self._reset_limits_handler, tools_menu_item_reset)
        self.Bind(wx.EVT_MENU, self._log_handler, tools_menu_item_log)

        # About menu:
        self.Bind(wx.EVT_MENU, self._about_handler, about_menu_item_about)

        self.SetMenuBar(menubar)

    def _init_tool_bar(self) -> None:
        """
        Toolbar initialization.
        :return: None
        """
        self._toolbar = self.CreateToolBar(style=wx.TB_DEFAULT_STYLE)

        new_tool: wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_NEW, Strings.menu_item_new,
                                                             self._scale_icon('new.svg',
                                                                              Constants.icon_tool_width,
                                                                              Constants.icon_tool_height),
                                                             Strings.menu_item_new)
        self._tools.append(new_tool)

        open_tool: wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_OPEN, Strings.menu_item_open,
                                                              self._scale_icon('open.svg',
                                                                               Constants.icon_tool_width,
                                                                               Constants.icon_tool_height),
                                                              Strings.menu_item_open)
        self._tools.append(open_tool)

        save_tool: wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_SAVE, Strings.menu_item_save,
                                                              self._scale_icon('save.svg',
                                                                               Constants.icon_tool_width,
                                                                               Constants.icon_tool_height),
                                                              Strings.menu_item_save)
        self._tools.append(save_tool)

        self._toolbar.AddSeparator()

        undo_tool: wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_UNDO, Strings.menu_item_undo,
                                                              self._scale_icon('undo.svg',
                                                                               Constants.icon_tool_width,
                                                                               Constants.icon_tool_height),
                                                              Strings.menu_item_undo)
        self._tools.append(undo_tool)

        redo_tool: wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_REDO, Strings.menu_item_redo,
                                                              self._scale_icon('redo.svg',
                                                                               Constants.icon_tool_width,
                                                                               Constants.icon_tool_height),
                                                              Strings.menu_item_redo)
        self._tools.append(redo_tool)

        self._toolbar.AddSeparator()

        bold_tool: wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_BOLD, Strings.menu_item_bold,
                                                              self._scale_icon('bold.svg', Constants.icon_tool_width,
                                                                               Constants.icon_tool_height),
                                                              Strings.menu_item_bold)
        self._tools.append(bold_tool)

        italic_tool: wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_ITALIC, Strings.menu_item_italic,
                                                                self._scale_icon('italic.svg',
                                                                                 Constants.icon_tool_width,
                                                                                 Constants.icon_tool_height),
                                                                Strings.menu_item_italic)
        self._tools.append(italic_tool)

        self._toolbar.AddSeparator()

        colorize_tool: wx.ToolBarToolBase = self._toolbar.AddCheckTool(toolId=wx.ID_APPLY,
                                                                       label=Strings.menu_item_italic,
                                                                       bitmap1=self._scale_icon('colorize.svg',
                                                                                                Constants.icon_tool_width,
                                                                                                Constants.icon_tool_height),
                                                                       shortHelp=Strings.menu_item_colorize)
        self._tools.append(colorize_tool)

        self._busy_wheel = wx.ActivityIndicator(self._toolbar, wx.ID_ANY, size=wx.Size(10, 10))
        self._toolbar.AddControl(self._busy_wheel, "")

        log_tool: wx.ToolBarToolBase = self._toolbar.AddCheckTool(toolId=wx.ID_UP,
                                                                  label=Strings.menu_item_log,
                                                                  bitmap1=self._scale_icon('up.svg',
                                                                                           Constants.icon_tool_width,
                                                                                           Constants.icon_tool_height),
                                                                  shortHelp=Strings.menu_item_log_hint)
        self._tools.append(log_tool)

        self.Bind(wx.EVT_MENU, self._apply_indicators_handler, colorize_tool)

        self._toolbar.Realize()

    @staticmethod
    def _scale_icon(name: str, width: int, height: int) -> wx.Bitmap:
        """
        Helper method to prepare icons for toolbar.
        :param name: Icon file name in Resources.
        :param width: Desired icon width.
        :param height: Desired icon height.
        :return: The icon bitmap
        """
        resource_path = Fetch.get_resource_path(name)
        svg_image = SVGimage.CreateFromFile(resource_path)
        return svg_image.ConvertToScaledBitmap(wx.Size(width, height))

    def _init_styles(self) -> None:
        """
        Init default stc styles.
        :return: None
        """
        self._main_text_field.StyleSetFaceName(stc.STC_STYLE_DEFAULT, "Courier New")
        self._main_text_field.StyleSetSize(stc.STC_STYLE_DEFAULT, 12)
        self._main_text_field.StyleSetForeground(stc.STC_STYLE_DEFAULT, wx.Colour(0, 0, 0))
        self._main_text_field.StyleSetBackground(stc.STC_STYLE_DEFAULT, wx.Colour(255, 255, 255))
        self._main_text_field.StyleSetBold(stc.STC_STYLE_DEFAULT, False)
        self._main_text_field.StyleSetItalic(stc.STC_STYLE_DEFAULT, False)

        # Apply style.
        self._main_text_field.StyleClearAll()

        self._main_text_field.StyleSetSpec(1, Constants.style_bold)
        self._main_text_field.StyleSetSpec(2, Constants.style_italic)
        self._main_text_field.StyleSetSpec(3, Constants.style_bold_italic)

        # todo use one with wx.stc.STC_INDIC_SQUIGGLE for spellcheck
        indicator_number = 0
        alpha = {1: 60, 2: 150}
        colors = {
            1: wx.Colour(255, 0, 0),  # Red
            2: wx.Colour(0, 0, 255),  # Blue
            3: wx.Colour(0, 128, 0),  # Green
            4: wx.Colour(255, 127, 0),  # Orange
            5: wx.Colour(128, 0, 128),  # Purple
            6: wx.Colour(139, 69, 19),  # Brown
            7: wx.Colour(255, 0, 255),  # Magenta
            8: wx.Colour(0, 128, 128),  # Teal
            9: wx.Colour(93, 89, 94),
            10: wx.Colour(50, 84, 54),
            11: wx.Colour(0, 239, 247),
        }
        for a, a_val in alpha.items():
            for c, c_val in colors.items():
                if (a, c) in [(1, 10)]:
                    # Skip combinations that are not distinct enough.
                    continue
                self._main_text_field.IndicatorSetStyle(indicator_number, wx.stc.STC_INDIC_FULLBOX)
                self._main_text_field.IndicatorSetForeground(indicator_number, c_val)
                self._main_text_field.IndicatorSetAlpha(indicator_number, a_val)
                self._main_text_field.IndicatorSetOutlineAlpha(indicator_number, a_val)
                indicator_number += 1
        for c, c_val in colors.items():
            if c in (9, 10):
                continue
            # Possibly wx.stc.STC_INDIC_COMPOSITIONTHICK
            self._main_text_field.IndicatorSetStyle(indicator_number, wx.stc.STC_INDIC_TEXTFORE)
            self._main_text_field.IndicatorSetForeground(indicator_number, c_val)
            self._main_text_field.IndicatorSetAlpha(indicator_number, 255)
            self._main_text_field.IndicatorSetOutlineAlpha(indicator_number, 255)
            indicator_number += 1

        # We have indicators 0-29 and can have 0-31, add two thick underlines
        self._main_text_field.IndicatorSetStyle(indicator_number, wx.stc.STC_INDIC_COMPOSITIONTHICK)
        self._main_text_field.IndicatorSetForeground(indicator_number, wx.Colour(255, 0, 0))
        self._main_text_field.IndicatorSetAlpha(indicator_number, 255)
        self._main_text_field.IndicatorSetOutlineAlpha(indicator_number, 255)
        indicator_number += 1
        self._main_text_field.IndicatorSetStyle(indicator_number, wx.stc.STC_INDIC_COMPOSITIONTHICK)
        self._main_text_field.IndicatorSetForeground(indicator_number, wx.Colour(0, 255, 0))
        self._main_text_field.IndicatorSetAlpha(indicator_number, 255)
        self._main_text_field.IndicatorSetOutlineAlpha(indicator_number, 255)

    def _init_status_bar(self) -> None:
        """
        Set up status bar for the frame.
        :return: None
        """
        # Create a status bar with 3 fields
        self._status_bar = self.CreateStatusBar(Constants.status_places)
        self._status_bar.SetStatusWidths(Constants.status_proportions)
        # Initialize status bar
        self._set_status_text('', 0)
        self._set_status_text('', 1)
        self._set_status_text('', 2)

    def _init_main_layout(self):
        """
        Main layout initialization.
        :return:
        """
        self._splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        top_panel = wx.Panel(self._splitter)
        bottom_panel = wx.Panel(self._splitter)
        self._splitter.SplitHorizontally(top_panel, bottom_panel)
        self._splitter.SetMinimumPaneSize(100)
        self._splitter.SetSashPosition(self.GetSize().height)
        self._splitter.SetSashGravity(0.5)

        self._repetition_selector = wx.SpinCtrl(top_panel, id=wx.ID_ANY,
                                                value=str(Constants.config_min_repetitions_default),
                                                style=wx.SP_ARROW_KEYS,
                                                size=wx.Size(120, -1),
                                                min=Constants.config_min_repetitions,
                                                max=Constants.config_max_repetitions,
                                                initial=Constants.config_min_repetitions_default)

        self._min_repeated_word_length_selector = wx.SpinCtrl(top_panel, id=wx.ID_ANY,
                                                              value=str(Constants.config_min_repetitions_default),
                                                              style=wx.SP_ARROW_KEYS,
                                                              size=wx.Size(120, -1),
                                                              min=Constants.config_min_len,
                                                              max=Constants.config_max_len,
                                                              initial=Constants.config_min_len_default)

        self._max_repeated_word_length_selector = wx.SpinCtrl(top_panel, id=wx.ID_ANY,
                                                              value=str(Constants.config_max_len),
                                                              style=wx.SP_ARROW_KEYS,
                                                              size=wx.Size(120, -1),
                                                              min=Constants.config_min_len,
                                                              max=Constants.config_max_len,
                                                              initial=Constants.config_max_len)

        self._search_text_field = wx.TextCtrl(top_panel, style=wx.TE_PROCESS_ENTER)
        self._search_button_up = wx.BitmapButton(top_panel, -1, wx.BitmapBundle(wx.ArtProvider.GetBitmap(wx.ART_GO_UP)))
        self._search_button_down = wx.BitmapButton(top_panel, -1,
                                                   wx.BitmapBundle(wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN)))
        self._search_results = wx.StaticText(top_panel, -1, label=Strings.label_search_results.format(0, 0))

        self._main_text_field = stc.StyledTextCtrl(top_panel, style=wx.TE_MULTILINE)
        self._main_text_field.SetWrapMode(1)
        self._main_text_field.SetCodePage(wx.stc.STC_CP_UTF8)
        self._main_text_field.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self._main_text_field.SetMarginMask(1, 0)
        self._main_text_field.SetMarginWidth(1, 30)

        self._input_text_field = wx.TextCtrl(bottom_panel, style=wx.TE_PROCESS_ENTER)
        self._log_text_field = wx.TextCtrl(bottom_panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        small_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
        self._log_text_field.SetFont(small_font)

        # Initialize word list:
        self._side_word_list = SidePanel(self)
        side_word_border_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, Strings.label_words)
        font = side_word_border_sizer.GetStaticBox().GetFont()
        font.SetPointSize(Constants.static_box_font_size)
        side_word_border_sizer.GetStaticBox().SetFont(font)
        side_word_border_sizer.Add(self._side_word_list, 1, wx.EXPAND)

        # Initialize search shortcut into accelerator table
        new_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self._focus_to_search_handler, id=new_id)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('F'), new_id)])
        self.SetAcceleratorTable(accel_tbl)

        coloring_repetitions_box = wx.StaticBoxSizer(wx.HORIZONTAL, top_panel, Strings.label_coloring_box_rep)
        font = coloring_repetitions_box.GetStaticBox().GetFont()
        font.SetPointSize(Constants.static_box_font_size)
        coloring_repetitions_box.GetStaticBox().SetFont(font)

        coloring_len_min_box = wx.StaticBoxSizer(wx.HORIZONTAL, top_panel, Strings.label_coloring_box_min_len)
        font = coloring_len_min_box.GetStaticBox().GetFont()
        font.SetPointSize(Constants.static_box_font_size)
        coloring_len_min_box.GetStaticBox().SetFont(font)

        coloring_len_max_box = wx.StaticBoxSizer(wx.HORIZONTAL, top_panel, Strings.label_coloring_box_max_len)
        font = coloring_len_max_box.GetStaticBox().GetFont()
        font.SetPointSize(Constants.static_box_font_size)
        coloring_len_max_box.GetStaticBox().SetFont(font)

        search_box = wx.StaticBoxSizer(wx.HORIZONTAL, top_panel, Strings.label_search_box)
        search_box.SetMinSize(width=350, height=-1)
        font = search_box.GetStaticBox().GetFont()
        font.SetPointSize(Constants.static_box_font_size)
        search_box.GetStaticBox().SetFont(font)

        # Main text area context menu.
        self._main_text_field.UsePopUp(stc.STC_POPUP_NEVER)

        # todo use this for the side panel.
        # Side panel context menu.
        # self._menu_side = wx.Menu()
        # self._menu_item_up = wx.MenuItem(self._menu_side, wx.ID_UP, "test")
        # self._menu_side.Append(self._menu_item_up)
        # self.Bind(wx.EVT_CONTEXT_MENU, self._on_context_menu_sidepanel_handler, self._side_word_list)

        self.Bind(stc.EVT_STC_MODIFIED, self.on_modified_handler)
        self.Bind(wx.EVT_CLOSE, self._on_exit_handler)

        self.Bind(wx.EVT_SPINCTRL, self._handle_marking_selector_handler, self._repetition_selector)
        self.Bind(wx.EVT_SPINCTRL, self._handle_marking_selector_handler, self._min_repeated_word_length_selector)
        self.Bind(wx.EVT_SPINCTRL, self._handle_marking_selector_handler, self._main_text_field)

        self.Bind(EVT_CHECKBOX_CHANGED, self._word_list_handler)

        self.Bind(wx.EVT_BUTTON, self._search_up_handler, self._search_button_up)
        self.Bind(wx.EVT_BUTTON, self._search_down_handler, self._search_button_down)

        self.Bind(wx.EVT_TEXT, self._search_handler, self._search_text_field)
        self.Bind(wx.EVT_TEXT_ENTER, self._search_enter_handler, self._search_text_field)

        self.Bind(wx.EVT_CONTEXT_MENU, self._on_main_text_right_click, self._main_text_field)
        self.Bind(wx.EVT_MENU, lambda _on_copy: self._main_text_field.Copy(), id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, lambda _on_paste: self._main_text_field.Paste(), id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, lambda _on_select_all: self._main_text_field.SelectAll(), id=wx.ID_SELECTALL)

        # Assemble
        main_horizontal_box = wx.BoxSizer(wx.HORIZONTAL)
        toolbar_horizontal_box = wx.BoxSizer(wx.HORIZONTAL)

        coloring_repetitions_box.Add(self._repetition_selector, 0, wx.LEFT, Constants.default_border)
        coloring_len_min_box.Add(self._min_repeated_word_length_selector, 0, wx.LEFT,
                                 Constants.default_border)
        coloring_len_max_box.Add(self._max_repeated_word_length_selector, 0, wx.LEFT,
                                 Constants.default_border)
        search_box.Add(self._search_text_field, 0, wx.LEFT, Constants.default_border)
        search_box.Add(self._search_button_up, 0, wx.LEFT, Constants.default_border)
        search_box.Add(self._search_button_down, 0, wx.LEFT, Constants.default_border)
        search_box.Add(self._search_results, 0, wx.LEFT | wx.CENTER, Constants.default_border)

        toolbar_horizontal_box.Add(coloring_repetitions_box, 0, wx.LEFT | wx.RIGHT, Constants.default_border)
        toolbar_horizontal_box.Add(coloring_len_min_box, 0, wx.LEFT, Constants.default_border)
        toolbar_horizontal_box.Add(coloring_len_max_box, 0, wx.LEFT, Constants.default_border)
        toolbar_horizontal_box.Add(search_box, 1, wx.LEFT, Constants.default_border)

        top_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        bottom_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        top_panel.SetSizer(top_panel_sizer)
        bottom_panel.SetSizer(bottom_panel_sizer)

        main_horizontal_box.Add(self._splitter, 1, wx.EXPAND)

        top_panel_sizer.Add(toolbar_horizontal_box, 0, wx.EXPAND)
        top_panel_sizer.Add(self._main_text_field, 4, wx.EXPAND | wx.BOTTOM | wx.LEFT, Constants.default_border)

        bottom_panel_sizer.Add(self._log_text_field, 1, wx.EXPAND)
        bottom_panel_sizer.Add(self._input_text_field, 0, wx.EXPAND | wx.BOTTOM, Constants.default_border)

        main_horizontal_box.Add(side_word_border_sizer, 0, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT,
                                Constants.default_border)

        self.SetSizer(main_horizontal_box)

    # Handlers ---------------------------------------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def _on_main_text_right_click(self, event: wx.ContextMenuEvent) -> None:
        """
        Create anc display the context pop up menu.
        :param event: Unused.
        :return: None
        """
        self._main_text_field.TargetFromSelection()

        if self._main_text_field.GetSelectionEmpty():
            # Select the word under the cursor.
            pos = self._main_text_field.ScreenToClient(wx.GetMousePosition())
            text_pos = self._main_text_field.PositionFromPoint(pos)
            word_start = self._main_text_field.WordStartPosition(text_pos, True)
            word_end = self._main_text_field.WordEndPosition(text_pos, True)
            self._main_text_field.SetSelection(word_start, word_end)

        menu = wx.Menu()
        undo_item = menu.Append(wx.ID_UNDO, Strings.menu_item_undo)
        redo_item = menu.Append(wx.ID_REDO, Strings.menu_item_redo)
        menu.AppendSeparator()
        copy_item = menu.Append(wx.ID_COPY, Strings.menu_item_copy)
        paste_item = menu.Append(wx.ID_PASTE, Strings.menu_item_paste)
        menu.Append(wx.ID_SELECTALL, Strings.menu_item_select_all)
        menu.AppendSeparator()

        ignore_item = menu.Append(self._id_add_ignore, Strings.menu_item_add_ignored)
        self.Bind(wx.EVT_MENU, self._on_context_menu_text_handler, id=self._id_add_ignore)

        name_item = menu.Append(self._id_add_names, Strings.menu_item_add_name)
        self.Bind(wx.EVT_MENU, self._on_context_menu_text_handler, id=self._id_add_names)

        menu.AppendSeparator()

        ignore_del_item = menu.Append(self._id_del_ignore, Strings.menu_item_del_ignored)
        self.Bind(wx.EVT_MENU, self._on_context_menu_text_handler, id=self._id_del_ignore)

        name_del_item = menu.Append(self._id_del_names, Strings.menu_item_del_name)
        self.Bind(wx.EVT_MENU, self._on_context_menu_text_handler, id=self._id_del_names)

        menu.AppendSeparator()

        limits_item = menu.Append(self._id_limits, Strings.menu_item_limits)
        self.Bind(wx.EVT_MENU, self._on_context_menu_text_handler, id=self._id_limits)

        enable = False
        if len(self._main_text_field.GetSelectedText()):
            enable = True
            for ch in "., ;":
                if ch in self._main_text_field.GetSelectedText().strip().lower():
                    enable = False
                    break

        if enable:
            submenu = wx.Menu()
            selection = self._sanitized_selection()
            if selection:
                synonyms = self._current_document.find_synonyms(selection)
                self._id_synonym_ids.clear()
                for synonym in synonyms:
                    new_id = wx.NewId()
                    self._id_synonym_ids.append(new_id)
                    submenu_item = wx.MenuItem(menu, new_id, synonym)
                    submenu.Append(submenu_item)
                    self.Bind(wx.EVT_MENU, self._on_context_menu_text_handler)
                if synonyms:
                    menu.AppendSubMenu(submenu, Strings.menu_item_synonym)
                else:
                    # Append a fake disabled synonym button.
                    synonyms_item = menu.Append(wx.ID_ANY, Strings.menu_item_synonym)
                    synonyms_item.Enable(False)

        copy_item.Enable(enable)
        ignore_item.Enable(enable)
        name_item.Enable(enable)
        limits_item.Enable(enable)
        ignore_del_item.Enable(enable)
        name_del_item.Enable(enable)

        undo_item.Enable(self._main_text_field.CanUndo())
        redo_item.Enable(self._main_text_field.CanRedo())
        paste_item.Enable(self._main_text_field.CanPaste())

        self.PopupMenu(menu)
        menu.Destroy()

    def _on_context_menu_text_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle clicks on the text area context menu buttons.
        :param event: Used to get ID to distinguish button.
        :return: None
        """
        event_id = event.GetId()
        selection = self._sanitized_selection()
        if selection:
            if event_id == self._id_add_ignore:
                words = self._current_document.get_ignored_words()
                words.add(selection)
                self._set_status_text(Strings.status_ignored.format(len(self._current_document.get_ignored_words())), 2)
                self._current_document.set_modified(True)
                self._apply_indicators_handler(event)
            if event_id == self._id_del_ignore:
                words = self._current_document.get_ignored_words()
                words.discard(selection)
                self._set_status_text(Strings.status_ignored.format(len(self._current_document.get_ignored_words())), 2)
                self._current_document.set_modified(True)
            if event_id == self._id_add_names:
                words = self._current_document.get_names()
                words.add(selection)
                self._current_document.set_modified(True)
            if event_id == self._id_del_names:
                words = self._current_document.get_names()
                words.discard(selection)
                self._current_document.set_modified(True)
            if event_id in self._id_synonym_ids:
                item_id = event.GetId()
                menu = event.GetEventObject()
                menu_item = menu.FindItemById(item_id)
                item_text = menu_item.GetItemLabelText()
                self._main_text_field.ReplaceSelection(item_text)
            if event_id == self._id_limits:
                self._max_repeated_word_length_selector.SetValue(len(selection))
                self._min_repeated_word_length_selector.SetValue(len(selection))
                self._handle_marking_selector_handler(event)

    # noinspection PyUnusedLocal
    def _focus_to_search_handler(self, event: wx.CommandEvent) -> None:
        """
        Handles Ctrl+F shortcut to set focus into the search box.
        :param event: Not used
        :return: None
        """
        self._search_text_field.SetFocus()

    def _reset_limits_handler(self, event: wx.CommandEvent) -> None:
        """
        Reset the spinner controls to default values.
        :param event: Passed along
        :return: None
        """
        self._repetition_selector.SetValue(Constants.config_min_repetitions_default)
        self._min_repeated_word_length_selector.SetValue(Constants.config_min_len_default)
        self._max_repeated_word_length_selector.SetValue(Constants.config_max_len)
        self._apply_indicators_handler(event)

    # noinspection PyUnusedLocal
    def _search_handler(self, event: wx.CommandEvent) -> None:
        """
        Undo last change.
        :param event: Not used
        :return: None
        """
        text = self._search_text_field.GetValue()
        if text:
            last_found_pos = 0
            found_word = (0, 0)
            self._found_words.clear()
            self._found_last_index = 0
            counter = 1
            while found_word != (-1, -1):
                found_word = self._main_text_field.FindText(last_found_pos, self._main_text_field.GetTextLength(),
                                                            text)
                if found_word != (-1, -1):
                    self._found_words.append((found_word, counter))
                    counter += 1
                last_found_pos = found_word[1]
            self._search_results.SetLabel(
                Strings.label_search_results.format(1 if self._found_words else 0, len(self._found_words)))
            if self._found_words:
                self._main_text_field.SetSelection(self._found_words[0][0][0], self._found_words[0][0][1])
                self._main_text_field.VerticalCentreCaret()
        else:
            self._found_last_index = 0
            self._found_words.clear()
            self._main_text_field.SetSelection(0, 0)
            self._search_results.SetLabel(label=Strings.label_search_results.format(0, 0))

    def _search_enter_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle the Enter key behavior of searching and cycle through results.
        :param event: Used to detect direction.
        :return: None
        """
        try:
            if self._found_words:
                if event.GetString() == 'up':
                    self._found_last_index -= 1
                else:
                    self._found_last_index += 1
                self._main_text_field.SetSelection(self._found_words[self._found_last_index][0][0],
                                                   self._found_words[self._found_last_index][0][1])
                self._main_text_field.VerticalCentreCaret()
                self._search_results.SetLabel(Strings.label_search_results.
                format(
                    self._found_words[self._found_last_index][1] if self._found_words else 0,
                    len(self._found_words)))
            else:
                # Restart search when the text was edited.
                self._search_handler(event)
        except IndexError as _:
            if event.GetString() == 'up':
                self._found_last_index = len(self._found_words)
            else:
                self._found_last_index = 0

    def _search_up_handler(self, event: wx.CommandEvent) -> None:
        """
        Search button up handler.
        :param event: Used to set direction.
        :return: None
        """
        event.SetString('up')
        self._search_enter_handler(event)

    def _search_down_handler(self, event: wx.CommandEvent) -> None:
        """
        Search button down handler.
        :param event: Not used.
        :return: None
        """
        self._search_enter_handler(event)

    # noinspection PyUnusedLocal
    def _undo_handler(self, event: wx.CommandEvent) -> None:
        """
        Undo last change.
        :param event: Not used.
        :return: None
        """
        self._main_text_field.Undo()
        self._main_text_field.Refresh()

    # noinspection PyUnusedLocal
    def _redo_handler(self, event: wx.CommandEvent) -> None:
        """
        Redo last change.
        :param event: Not used.
        :return: None
        """
        self._main_text_field.Redo()
        self._main_text_field.Refresh()

    def _edit_words_handler(self, event: wx.CommandEvent) -> None:
        """
        Open a dialog for word list editing.
        :param event: Not used.
        :return: None
        """
        button_id = event.GetId()
        dialog = None
        if button_id == self._id_ignored:
            dialog = PlainTextEditDialog(self, Strings.menu_item_edit_words_ignored_hint, self._current_document)
        elif button_id == self._id_names:
            dialog = PlainTextEditDialog(self, Strings.menu_item_edit_words_names_hint, self._current_document)
        elif button_id == self._id_edit_synonyms:
            dialog = PlainTextEditDialog(self, Strings.menu_item_edit_words_synonyms_hint, self._current_document)
        if dialog:
            dialog.ShowModal()
        self._set_status_text(Strings.status_ignored.format(len(self._current_document.get_ignored_words())), 2)

    # noinspection PyUnusedLocal
    def _new_file_handler(self, event: wx.CommandEvent) -> None:
        """
        Create a new empty file.
        :param event: Not used.
        :return: None
        """
        if self._current_document:
            self._emergency_save()

        location = self._open_save_dialog()
        if location:
            # Replace the current document with a new one.
            self._clear_editor()
            if not location.endswith(".html"):
                location = f"{location}.html"
            shutil.copy(Path(Fetch.get_resource_path('template.html')), location)
            self._load_document(Path(location))

    # noinspection PyUnusedLocal
    def _info_word_counts_handler(self, event: wx.CommandEvent) -> None:
        """
        Show a dialog with information about word counts.
        :param event: Not used.
        :return: None
        """
        WordInfoDialog(self, self._current_document.get_word_marking_data())

    # noinspection PyUnusedLocal
    def _log_handler(self, event: wx.CommandEvent) -> None:
        """
        Show log by moving the divider up.
        :param event: Not used.
        :return: None
        """
        if self._log_up:
            self._splitter.SetSashPosition(self.GetSize().height, True)
        else:
            self._splitter.SetSashPosition(10, True)
        self._log_up = not self._log_up

    # noinspection PyUnusedLocal
    def _open_file(self, event: wx.CommandEvent) -> None:
        """
        Open existing file for editing.
        :param event: Not used
        :return: None
        """
        if self._current_document:
            self._emergency_save()

        dialog = wx.FileDialog(self, Strings.dialog_open, "", "", Constants.html_wildcard,
                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            self._clear_editor()
            self._load_document(Path(dialog.GetPath()))

    # noinspection PyUnusedLocal
    def _apply_indicators_handler(self, event: wx.CommandEvent) -> None:
        """
        Apply word repetition indicators into text.
        :param event: Not used
        :return: None
        """
        # todo if a word becomes missing in text, it remains in the side panel while the tool is active.
        #  Can we update the list somehow automatically? Timer?
        # Clear before reapplying. We always have 0-31 indicators.
        for indicator in range(32):
            self._main_text_field.SetIndicatorCurrent(indicator)
            self._main_text_field.IndicatorClearRange(0, self._main_text_field.GetTextLength())
            if not self._selected_words and self._coloring_tool_off:
                self._side_word_list.clear_list()

        colorize_tool: ToolBarToolBase = self._toolbar.FindById(wx.ID_APPLY)
        if not colorize_tool.IsToggled():
            # Clear if we are turning the tool off.
            self._main_text_field.Refresh()
            self._side_word_list.clear_list()
            self._coloring_tool_off = True
            return
        else:
            if self._coloring_tool_off:
                self._busy_wheel.Start()
                ColoratorThread(self, self._current_document, self._main_text_field.GetText())
            else:
                # If the tool run before and is still active, do not recalculate.
                # todo changing the text and then using the checkboxes messes up the positions. Solve this later. Start recalculating once idle in background?
                ColoratorThread(self, self._current_document, self._main_text_field.GetText())
                self.apply_indicators_callback({}, {})

    def apply_indicators_callback(self, plain_words: Dict[bytes, int],
                                  spans_by_word: defaultdict[bytes, List[re.Match]]) -> None:
        """
        Thread callback to finish applying indicators once the calculations are made.
        :return: None
        """
        # todo this method is slow on long texts.
        word_data: Dict[bytes, ListItemPanel] = self._current_document.get_word_marking_data()
        # Update or create word panels
        # This can not be done in a thread because it is calling a gui method and will segfault.
        if self._coloring_tool_off:
            for word, count in plain_words.items():
                spans = spans_by_word[word]
                panel = word_data.get(word)
                if panel is None:
                    new_panel = self._side_word_list.add_hidden_item(Word(word.decode('utf-8'), spans, count))
                    word_data[word] = new_panel
                else:
                    word_container = panel.get_word_instance()
                    word_container.set_spans(spans)
                    word_container.set_count(count)

        repetition_limit = self._repetition_selector.GetValue()
        length_min_limit = self._min_repeated_word_length_selector.GetValue()
        length_max_limit = self._max_repeated_word_length_selector.GetValue()

        # Filter the words that fit the marking criteria to a new list and work on that.
        fitting_words: List[ListItemPanel] = []
        for panel in word_data.values():
            panel: ListItemPanel
            word_instance = panel.get_word_instance()
            word = word_instance.get_word()
            w_count = word_instance.get_count()
            if w_count >= repetition_limit and length_min_limit <= len(word) <= length_max_limit:
                if word not in self._current_document.get_ignored_words():
                    if word in self._selected_words:
                        panel.set_checked(True)
                    fitting_words.append(panel)

        # Assign indicators to filtered words.
        if self._coloring_tool_off:
            # The tool is running for the first time, assign indicators to everything top down.
            indicator_counter = 31
            # Sort the words from the highest number of repetitions down.
            for w in sorted(fitting_words, reverse=True):
                w: ListItemPanel
                word_instance = w.get_word_instance()
                word_instance.set_indicator(indicator_counter)
                if self._selected_words:
                    if word_instance.is_selected():
                        w.set_checked(True)
                else:
                    w.set_checked(True)
                indicator_counter -= 1
                if indicator_counter == -1:
                    break

        # Fill word list.
        if self._coloring_tool_off:
            # Fill only once when the tool runs the first time.
            self._side_word_list.add_items(fitting_words)
            self._coloring_tool_off = False
        else:
            if self._available_indicators:
                # We have some spare indicators, enable all checkboxes.
                for item in self._side_word_list.GetChildren():
                    item: ListItemPanel
                    if not item.is_enabled():
                        item.set_enabled(True)
            else:
                # Disable extra checkboxes.
                for item in self._side_word_list.GetChildren():
                    item: ListItemPanel
                    has_indicator = item.get_word_instance().has_indicator()
                    item.set_enabled(has_indicator)

        # Display indicators.
        # todo this is the slowest part
        # todo can we apply indicators only to the currently visible lines?
        # Reduce redrawing with freeze.
        self._main_text_field.Freeze()
        for w in fitting_words:
            w: ListItemPanel
            word_instance = w.get_word_instance()
            if word_instance.has_indicator() and w.is_checked():
                indicator = word_instance.get_indicator()
                locations = word_instance.get_spans()
                for word_span in locations:
                    word_span: re.Match
                    self._main_text_field.SetIndicatorCurrent(indicator)
                    self._main_text_field.IndicatorFillRange(word_span.span()[0],
                                                             word_span.span()[1] - word_span.span()[0])
        self._main_text_field.Thaw()
        self._main_text_field.Refresh()
        self._update_indicator_count()
        self._busy_wheel.Stop()

    def _handle_marking_selector_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle changes to word repetition spin ctrls.
        :param event: Not used.
        :return: None
        """
        colorize_tool: ToolBarToolBase = self._toolbar.FindById(wx.ID_APPLY)
        if colorize_tool.IsToggled():
            self._apply_indicators_handler(event)

    def _word_list_handler(self, event: dv.DataViewEvent) -> None:
        """
        Handle checkboxes in the side word list.
        This even fires after the checkbox has been changed.
        :param event: Passed along.
        :return: None
        """
        self._selected_words.clear()
        for item in self._side_word_list.GetChildren():
            item: ListItemPanel
            if item.is_checked():
                self._selected_words.append(item.get_word_instance().get_word())
                if not item.get_word_instance().has_indicator():
                    item.get_word_instance().set_indicator(self._available_indicators.pop())
            else:
                # Return indicator to magazine.
                indicator = item.get_word_instance().get_indicator()
                if indicator > -1:
                    self._available_indicators.add(indicator)
                    item.get_word_instance().clear_indicator()
        self._apply_indicators_handler(event)

    # noinspection PyUnusedLocal
    def _make_bold_handler(self, event: wx.CommandEvent) -> None:
        """
        Change text to bold.
        :param event: Not used.
        :return: None
        """
        start_pos = self._main_text_field.GetSelectionStart()
        style = self._main_text_field.GetStyleAt(start_pos)
        if style == Constants.style_map[Constants.style_bold]:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        Constants.style_map[Constants.style_default])
        elif style == Constants.style_map[Constants.style_italic]:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        Constants.style_map[Constants.style_bold_italic])
        elif style == Constants.style_map[Constants.style_bold_italic]:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        Constants.style_map[Constants.style_italic])
        else:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        Constants.style_map[Constants.style_bold])

    # noinspection PyUnusedLocal
    def _make_italic_handler(self, event: wx.CommandEvent) -> None:
        """
        Change text to italic.
        :param event: Not used.
        :return: None
        """
        start_pos = self._main_text_field.GetSelectionStart()
        style = self._main_text_field.GetStyleAt(start_pos)
        if style == Constants.style_map[Constants.style_italic]:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        Constants.style_map[Constants.style_default])
        elif style == Constants.style_map[Constants.style_bold]:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        Constants.style_map[Constants.style_bold_italic])
        elif style == Constants.style_map[Constants.style_bold_italic]:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        Constants.style_map[Constants.style_bold])
        else:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        Constants.style_map[Constants.style_italic])

    def on_modified_handler(self, event: wx._stc.StyledTextEvent) -> None:
        """
        Catches modifications and handles custom undo/redo events.
        :param event: Used to get modification data.
        :return: None
        """
        # The even contains a bit mask of what happened, we need to compare it with &.
        mod_type: int = event.GetModificationType()
        if mod_type & stc.STC_MOD_CHANGEINDICATOR:
            return

        self._found_last_index = 0
        self._found_words.clear()

        if self._current_document:
            self._current_document.set_modified(True)

        if not self.GetTitle().startswith('*'):
            self.SetTitle(f"* {self.GetTitle()}")

        if mod_type & stc.STC_MOD_CONTAINER:
            token = event.GetToken()
            action = self._style_history.get(token)
            if not action:
                return

            start = action['start']
            length = action['length']
            if mod_type & stc.STC_PERFORMED_UNDO:
                for i, old_style_byte in enumerate(action['old_styles']):
                    self._main_text_field.StartStyling(start + i)
                    self._main_text_field.SetStyling(1, old_style_byte)
            elif mod_type & stc.STC_PERFORMED_REDO:
                self._main_text_field.StartStyling(start)
                self._main_text_field.SetStyling(length, action['new_style_id'])

    # noinspection PyUnusedLocal
    def _clear_styles_handler(self, event: wx.CommandEvent) -> None:
        """
        Change text to default style.
        :param event: Not used.
        :return: None
        """
        start_pos = self._main_text_field.GetSelectionStart()
        self._main_text_field.StartStyling(start_pos)
        self._main_text_field.SetStyling(len(self._main_text_field.GetSelectedText()),
                                         Constants.style_map[Constants.style_default])

    # noinspection PyUnusedLocal
    def _save_file_handler(self, event: wx.CommandEvent) -> None:
        """
        Save file.
        :param event: Not used
        :return: None
        """
        self._save_document()

    # noinspection PyUnusedLocal
    def _save_as_file_handler(self, event: wx.CommandEvent) -> None:
        """
        Save file.
        :param event: Not used
        :return: None
        """
        self._save_document(save_as=True)

    # noinspection PyUnusedLocal
    def _quit_handler(self, event: wx.CommandEvent) -> None:
        """
        Quit the program.
        :param _: Unused
        :return: None
        """
        if self._current_document:
            self._emergency_save()
        self.Close()

    # noinspection PyUnusedLocal
    def _on_exit_handler(self, event: wx.CommandEvent) -> None:
        """
        Closing the window with X.
        :param event: Not used.
        :return: None
        """
        if self._current_document:
            self._emergency_save()
        self.Destroy()

    # noinspection PyUnusedLocal
    def _about_handler(self, event: wx.CommandEvent) -> None:
        """
        Show the About dialog.
        :param event: Not used.
        :return: None
        """
        AboutDialog(self)

    # Methods---------------------------------------------------------------------------------------------------------------

    def _sanitized_selection(self) -> str:
        return self._main_text_field.GetSelectedText().strip().lower().lstrip('.').rstrip('.').lstrip(',').rstrip(',')

    def _clear_editor(self) -> None:
        """
        Clear the gui to default state.
        :return: None
        """
        self._main_text_field.ClearAll()

    def _update_indicator_count(self) -> None:
        """
        Update how many free indicators we have in the status panel.
        :return: None
        """
        free = len(self._available_indicators)
        # 32 is our maximum number of usable indicators.
        self._set_status_text(Strings.status_indicators.format(32 - free, free), 3)

    def _apply_style_with_undo(self, start, length, new_style_id) -> None:
        """
        Applies a style to a range of text and records it in the native undo stack.
        :param start:
        :param length:
        :param new_style_id:
        :return:
        """
        if length <= 0:
            return
        old_styles = [self._main_text_field.GetStyleAt(start + i) for i in range(length)]
        self._action_token += 1
        token = self._action_token

        self._style_history[token] = {
            'start': start,
            'length': length,
            'old_styles': old_styles,
            'new_style_id': new_style_id
        }

        self._main_text_field.BeginUndoAction()
        self._main_text_field.StartStyling(start)
        self._main_text_field.SetStyling(length, new_style_id)
        # 0 means this action cannot be (merged) with adjacent text typing
        self._main_text_field.AddUndoAction(token, 0)
        self._main_text_field.EndUndoAction()

    def _set_status_text(self, text: str, position=0) -> None:
        """
        Set a text into a position in status bar and prepend a separator.
        :param text: Text to set.
        :param position: Where to set the text, 0 is default
        :return: None
        """
        to_set = f'| {text}'
        self._status_bar.SetStatusText(to_set, position)

    def _on_fully_loaded(self) -> None:
        """
        Runs once the gui is loaded.
        :return: None
        """
        last_file = self._config.get_last_file()
        if self._show_yes_no_dialog(Strings.warn_load_last_file.format(last_file), wx.ICON_QUESTION):
            self._load_document(last_file)

    def _disable_editor(self, everything=False) -> None:
        """
        Disable all features.
        :param everything: Disable every control in the window.
        :return: None
        """
        if everything:
            self.Disable()
            for t in self._tools:
                self._toolbar.EnableTool(t.GetId(), False)
            return
        self._repetition_selector.Disable()
        self._min_repeated_word_length_selector.Disable()
        self._max_repeated_word_length_selector.Disable()
        self._main_text_field.Disable()
        for t in self._tools:
            if t.GetId() not in [wx.ID_NEW, wx.ID_OPEN]:
                self._toolbar.EnableTool(t.GetId(), False)
        for i in self._menu_items:
            if i.GetId() not in [wx.ID_NEW, wx.ID_OPEN, wx.ID_EXIT, wx.ID_ABOUT]:
                i.Enable(False)

    def enable_editor(self) -> None:
        """
        Enable all features of the editor.
        :return: None
        """
        self.Enable()
        self._repetition_selector.Enable()
        self._min_repeated_word_length_selector.Enable()
        self._max_repeated_word_length_selector.Enable()
        self._main_text_field.Enable()
        for t in self._tools:
            self._toolbar.EnableTool(t.GetId(), True)
        for i in self._menu_items:
            i.Enable(True)

    def _open_save_dialog(self) -> str:
        """
        Return path to the new file location or empty string.
        :return: Path to the new file location or empty string.
        """
        with wx.FileDialog(self, Strings.dialog_save, wildcard=Constants.html_wildcard,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return ""
            return fileDialog.GetPath()

    def _show_error_ok_dialog(self, error: str) -> None:
        """
        Display an error dialog with the error text. Set error state into the status bar.
        :param error: The error to display in the dialog.
        :return: None
        """
        wx.MessageBox(error, Strings.status_warning, wx.OK | wx.ICON_WARNING)
        self._set_status_text(Strings.status_warning, 1)

    def _show_yes_no_dialog(self, message: str, kind: int) -> bool:
        """
        Display a dialog with message and yes/no buttons.
        :param message: The message to display in the dialog.
        :return: User choice. True if yes.
        """
        dialog = wx.MessageDialog(self, message, Strings.status_warning, wx.YES_NO | kind)
        if dialog.ShowModal() == wx.ID_YES:
            return True
        return False

    def _on_statistics_timer(self, event: wx.CommandEvent) -> None:
        """
        Statistics timer handler. Runs periodically. Runs a background thread that calculates text stats.
        :param event: Not used.
        :return: None
        """
        if self._statistics_thread is None or not self._statistics_thread.is_alive():
            self._statistics_thread = StatisticsThread(self, self._main_text_field.GetText())
            self._statistics_thread.start()

    def text_statistics_callback(self, words: int) -> None:
        """
        Thread callback for text statistics. Sets the status bar information.
        :return: None
        """
        lines = self._main_text_field.NumberOfLines
        chars = self._main_text_field.GetTextLength()
        self._set_status_text(Strings.status_doc_info.format(lines, words, chars), 0)

    def append_styled_text(self, text: str, style: str) -> None:
        """
        Add text to text area with style.
        :param text: The text to add.
        :param style: Style name.
        :return: None
        """
        start_pos = self._main_text_field.GetLength()
        self._main_text_field.AppendText(text)
        self._main_text_field.StartStyling(start_pos)
        self._main_text_field.SetStyling(len(text), Constants.style_map[style])

    def append_new_line(self) -> None:
        """
        Add new line to text area.
        :return: None
        """
        self._main_text_field.AppendText('\n')

    def _load_document(self, file_path: Path) -> None:
        """
        Load document into editor. Rtf can not be used by richtextctrl yet.
        :param file_path: Document path.
        :return: None
        """
        self._waiting_dialog.Show()
        self._waiting_dialog.start(saving=False)
        self._set_status_text(Strings.status_loading, 0)
        self._disable_editor(everything=True)

        # Clear tools
        self._toolbar.ToggleTool(wx.ID_APPLY, False)
        self._toolbar.Refresh()
        self._found_last_index = 0
        self._search_text_field.SetValue('')
        self._found_words.clear()
        self._side_word_list.wipe_list()
        self._selected_words.clear()
        self._coloring_tool_off = True

        # Create a new document container for the file and give it to a thread to load.
        self._current_document = Document(file_path)
        LoadFileThread(self, self._current_document)

    def load_document_callback(self, exp: str) -> None:
        """
        Thread callback after loading a new document.
        :return: None
        """
        if exp:
            self._show_error_ok_dialog(exp)
            return

        errors = self._current_document.get_errors()
        if errors:
            formatted = ''
            for e in errors:
                formatted += f"{e}\n"
            self._show_error_ok_dialog(Strings.warn_errors.format(formatted))
            return

        # Todo spinner stops spinning at the end while loading large document 1000+ a4 pages. Text field is rendering the text on main thead.
        self._main_text_field.EmptyUndoBuffer()
        self.SetTitle(Strings.app_title.format(self._current_document.get_path().name))
        self._set_status_text(self._current_document.get_path().name, 1)
        # on_modified will run while loading and erroneously set modified to True so we need to fix it.
        self._current_document.set_modified(False)
        self._set_status_text(Strings.status_ignored.format(len(self._current_document.get_ignored_words())), 2)
        self.enable_editor()
        self._main_text_field.SetFocus()
        self._config.set_last_file(self._current_document.get_path())
        self._config.save_config()
        self._waiting_dialog.Close()
        self._statistics_timer.Start(Constants.statistics_timer_delay)
        self._set_status_text(Strings.status_calculating, 0)
        self.post_message(Strings.msg_loaded.format(self._current_document.get_path()), Constants.msg_info)

    def _save_document(self, save_as: bool = False) -> None:
        """
        Save current file and optionally show a save as dialog.
        :param save_as: True to show dialog.
        :return: None
        """
        self._set_status_text(Strings.status_saving, 0)
        self._disable_editor(everything=True)
        destination = self._current_document.get_path()
        if self._current_document.is_new() or save_as:
            destination = self._open_save_dialog()

        if destination:
            self._waiting_dialog.Show()
            self._waiting_dialog.start(saving=True)
            self._current_document.set_path(Path(destination))
            SaveFileThread(self, self._current_document, self._convert_document(), self._main_text_field.GetText())
        else:
            # Canceled dialog.
            self._set_status_text(Strings.status_not_saved.format('canceled'), 0)
            return

    def save_document_callback(self, result: bool) -> None:
        """
        Thread callback after saving current document.
        :param result: True if save was successful.
        :return: None
        """
        if result:
            self._set_status_text(self._current_document.get_path().name, 1)
            self._main_text_field.SetSavePoint()
            self.SetTitle(Strings.app_title.format(self._current_document.get_path().name))
            self._config.set_last_file(self._current_document.get_path())
            self._config.save_config()
            self._current_document.set_modified(False)
            self._set_status_text(Strings.status_saved.format('Ok'), 0)
            self.enable_editor()
        else:
            self._set_status_text(Strings.status_not_saved.format('error'), 0)
            self._show_error_ok_dialog(Strings.status_not_saved.format('error'))
        self._waiting_dialog.Close()
        self.post_divider()
        self.post_message(Strings.msg_saved.format(self._current_document.get_path()), Constants.msg_info)

    def post_message(self, message: str, severity: int) -> None:
        """
        Print a message into the status/log box.
        :param message: The message.
        :param severity: Style of message affecting color and warning type.
        :return: None
        """
        # todo equip stuff with log messages
        # todo post save checks into the log and show a dialog about it
        stamp = time.strftime('%H:%M')
        if severity == Constants.msg_reply:
            self._log_text_field.SetForegroundColour(wx.BLACK)
            self._log_text_field.AppendText(f"{stamp} [R]: {message}\n")
        elif severity == Constants.msg_info:
            self._log_text_field.SetForegroundColour(wx.BLUE)
            self._log_text_field.AppendText(f"{stamp} [I]: {message}\n")
        elif severity == Constants.msg_warn:
            self._log_text_field.SetForegroundColour(wx.Colour(252, 119, 3))
            self._log_text_field.AppendText(f"{stamp} [W]: {message}\n")
        elif severity == Constants.msg_err:
            self._log_text_field.SetForegroundColour(wx.RED)
            self._log_text_field.AppendText(f"{stamp} [E]: {message}\n")

    def post_divider(self) -> None:
        """
        Post a divider into the log field.
        :return: None
        """
        self._log_text_field.SetForegroundColour(wx.BLACK)
        self._log_text_field.AppendText(f"{179 * '-'}\n")

    def _convert_document(self) -> List:
        """
        Extracts text and styling into the simple dictionary format.
        :return: List of tuples with style and text information.
        """
        converted = []

        length = self._main_text_field.GetTextLength()
        if length == 0:
            return converted

        current_style: int = self._main_text_field.GetStyleAt(0)
        chunk_start: int = 0
        for pos in range(length):
            style_at_pos = self._main_text_field.GetStyleAt(pos)

            # When the style changes, save the previous chunk.
            if style_at_pos != current_style:
                text_chunk = self._main_text_field.GetTextRange(chunk_start, pos)
                # Escape HTML characters (<, >, &, etc.)
                escaped_text = html.escape(text_chunk)

                for style, style_id in Constants.style_map.items():
                    if style_id == current_style:
                        converted.append((style, escaped_text))

                current_style = style_at_pos
                chunk_start = pos
        # Save last chunk where the style does not change.
        text_chunk = self._main_text_field.GetTextRange(chunk_start, length)
        for style, style_id in Constants.style_map.items():
            if style_id == current_style:
                converted.append((style, html.escape(text_chunk)))
        return converted

    def _emergency_save(self) -> None:
        """
        User is performing an action that could destroy the document, ask for save.
        :return: None
        """
        if self._current_document.is_modified():
            if self._show_yes_no_dialog(Strings.warn_file_not_saved.format(self._current_document.get_path().name),
                                        wx.ICON_ASTERISK):
                self._save_document()
