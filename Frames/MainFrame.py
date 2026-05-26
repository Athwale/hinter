import re
import shutil
from itertools import count
from pathlib import Path
from typing import List, Dict

import html
import wx
import wx.grid
import wx.stc as stc
from wx import ToolBarToolBase
from wx._core import StatusBar, ToolBar
from wx.svg import SVGimage
import wx.dataview as dv
import wx.lib.scrolledpanel

from Constants import Constants
from Constants import Strings
from Constants.Constants import EVT_CHECKBOX_CHANGED
from Containers.ListItemPanel import ListItemPanel
from Containers.Document import Document
from Containers.SidePanel import SidePanel
from Containers.Word import Word
from Dialogs.AboutDialog import AboutDialog
from Dialogs.WordInfoDialog import WordInfoDialog
from Resources.Fetch import Fetch
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
        self._main_text_field: stc.StyledTextCtrl = None
        self._repetition_selector: wx.SpinCtrl = None
        self._min_repeated_word_length_selector: wx.SpinCtrl = None
        self._max_repeated_word_length_selector: wx.SpinCtrl = None
        self._search_text_field: wx.TextCtrl = None
        self._search_button_up: wx.BitmapButton = None
        self._search_button_down: wx.BitmapButton = None
        self._search_results: wx.StaticText = None

        self._current_document: Document = None
        self._status_bar: StatusBar = None
        self._toolbar: ToolBar = None
        self._tools: List[wx.ToolBarToolBase] = []
        self._menu_items: List[wx.MenuItem] = []
        self._style_map = {Constants.style_default: 0,
                           Constants.style_bold: 1,
                           Constants.style_italic: 2,
                           Constants.style_bold_italic: 3}
        # Used for undo.
        self._style_history = {}
        self._action_token = 0

        self._side_word_list: SidePanel = None
        self._used_indicators: Dict[int, bool] = {}
        self._selected_words: List[str] = []

        self._init_menu_bar()
        self._init_tool_bar()
        self._init_layout()
        self._init_status_bar()
        self._set_styles()
        self._disable_editor()
        self._set_status_text(Strings.status_ready, 0)
        self._set_status_text(Strings.status_no_document, 1)

        self._found_words: List[tuple[tuple[int, int], int]] = []
        self._found_last_index = 0

        # Load configuration
        self._config = Config()
        if self._config.get_last_file() != Path():
            wx.CallAfter(self._on_fully_loaded)

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
        file_menu_item_save_as = file_menu.Append(wx.ID_SAVEAS, Strings.menu_item_save_as, Strings.menu_item_save_as_hint)
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
        edit_menu_item_remove_styles = edit_menu.Append(wx.ID_CLEAR, Strings.menu_item_clear, Strings.menu_item_clear_hint)
        self._menu_items.append(edit_menu_item_remove_styles)

        # Tools menu:
        tools_menu = wx.Menu()
        tools_menu_item_words = tools_menu.Append(wx.ID_INFO, Strings.menu_item_word_list,
                                                Strings.menu_item_word_list_hint)
        self._menu_items.append(tools_menu_item_words)

        # About menu:
        about_menu = wx.Menu()
        about_menu_item_about = about_menu.Append(wx.ID_ABOUT, Strings.menu_item_about, Strings.menu_item_about_hint)
        self._menu_items.append(about_menu_item_about)

        menubar.Append(file_menu, Strings.menu_file)
        menubar.Append(edit_menu, Strings.menu_edit)
        menubar.Append(tools_menu, Strings.menu_tools)
        menubar.Append(about_menu, Strings.menu_about)

        # Bind menu item handlers.
        self.Bind(wx.EVT_MENU, self._quit, file_menu_item_quit)
        self.Bind(wx.EVT_MENU, self._open_file, file_menu_item_open)
        self.Bind(wx.EVT_MENU, self._save_file_handler, file_menu_item_save)
        self.Bind(wx.EVT_MENU, self._save_as_file_handler, file_menu_item_save_as)
        self.Bind(wx.EVT_MENU, self._make_bold, edit_menu_item_bold)
        self.Bind(wx.EVT_MENU, self._make_italic, edit_menu_item_italic)
        self.Bind(wx.EVT_MENU, self._new_file, file_menu_item_new)
        self.Bind(wx.EVT_MENU, self._about, about_menu_item_about)
        self.Bind(wx.EVT_MENU, self._undo, edit_menu_item_undo)
        self.Bind(wx.EVT_MENU, self._redo, edit_menu_item_redo)
        self.Bind(wx.EVT_MENU, self._clear_styles, edit_menu_item_remove_styles)
        self.Bind(wx.EVT_MENU, self._info_word_counts, tools_menu_item_words)

        self.Bind(stc.EVT_STC_MODIFIED, self.on_modified)
        self.Bind(wx.EVT_CLOSE, self._on_exit)

        self.SetMenuBar(menubar)

    def _init_tool_bar(self) -> None:
        """
        Toolbar initialization.
        :return: None
        """
        self._toolbar = self.CreateToolBar(style=wx.TB_DEFAULT_STYLE)

        new_tool: wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_NEW, Strings.menu_item_new,
                                                              wx.ArtProvider.GetBitmap(wx.ART_NEW),
                                                              Strings.menu_item_new)
        self._tools.append(new_tool)

        open_tool: wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_OPEN, Strings.menu_item_open,
                                                             wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN),
                                                             Strings.menu_item_open)
        self._tools.append(open_tool)

        save_tool: wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_SAVE, Strings.menu_item_save,
                                                             wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE),
                                                             Strings.menu_item_save)
        self._tools.append(save_tool)

        self._toolbar.AddSeparator()

        undo_tool: wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_UNDO, Strings.menu_item_undo,
                                                             wx.ArtProvider.GetBitmap(wx.ART_UNDO),
                                                             Strings.menu_item_undo)
        self._tools.append(undo_tool)

        redo_tool: wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_REDO, Strings.menu_item_redo,
                                                         wx.ArtProvider.GetBitmap(wx.ART_REDO),
                                                         Strings.menu_item_redo)
        self._tools.append(redo_tool)

        self._toolbar.AddSeparator()

        bold_tool: wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_BOLD, Strings.menu_item_bold,
                                                         self._scale_icon('bold.svg', Constants.icon_tool_width,
                                                                          Constants.icon_tool_height),
                                                         Strings.menu_item_bold)
        self._tools.append(bold_tool)

        italic_tool: wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_ITALIC, Strings.menu_item_italic,
                                                         self._scale_icon('italic.svg', Constants.icon_tool_width,
                                                                          Constants.icon_tool_height),
                                                         Strings.menu_item_italic)
        self._tools.append(italic_tool)

        self._toolbar.AddSeparator()

        colorize_tool: wx.ToolBarToolBase = self._toolbar.AddCheckTool(toolId=wx.ID_APPLY,
                                                                       label=Strings.menu_item_italic,
                                                                       bitmap1=self._scale_icon('colorize.svg',
                                                                                        Constants.icon_tool_width,
                                                                                        Constants.icon_tool_height),
                                                                       bmpDisabled=self._scale_icon('colorize.svg',
                                                                                        Constants.icon_tool_width,
                                                                                        Constants.icon_tool_height),
                                                                       shortHelp=Strings.menu_item_italic)
        self._tools.append(colorize_tool)

        self.Bind(wx.EVT_MENU, self._apply_indicators, colorize_tool)

        self._toolbar.Realize()

    def _set_styles(self) -> None:
        """
        Set stc styles.
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
        alpha = {1:60, 2:150}
        colors = {
            1: wx.Colour(255, 0, 0), # Red
            2: wx.Colour(0, 0, 255), # Blue
            3: wx.Colour(0, 128, 0), # Green
            4: wx.Colour(255, 127, 0), # Orange
            5: wx.Colour(128, 0, 128), # Purple
            6: wx.Colour(139, 69, 19), # Brown
            7: wx.Colour(255, 0, 255), # Magenta
            8: wx.Colour(0, 128, 128), # Teal
            9: wx.Colour(93, 89, 94),
            10: wx.Colour(50, 84, 54),
            11: wx.Colour(0, 239, 247),
        }
        for a, a_val in alpha.items():
            for c, c_val  in colors.items():
                if (a, c) in [(1, 10)]:
                    # Skip combinations that are not distinct enough.
                    continue
                self._main_text_field.IndicatorSetStyle(indicator_number, wx.stc.STC_INDIC_FULLBOX)
                self._main_text_field.IndicatorSetForeground(indicator_number, c_val)
                self._main_text_field.IndicatorSetAlpha(indicator_number, a_val)
                self._main_text_field.IndicatorSetOutlineAlpha(indicator_number, a_val)
                self._used_indicators[indicator_number] = False
                indicator_number += 1
        for c, c_val  in colors.items():
            if c in (9, 10):
                continue
            # Possibly wx.stc.STC_INDIC_COMPOSITIONTHICK
            self._main_text_field.IndicatorSetStyle(indicator_number, wx.stc.STC_INDIC_TEXTFORE)
            self._main_text_field.IndicatorSetForeground(indicator_number, c_val)
            self._main_text_field.IndicatorSetAlpha(indicator_number, 255)
            self._main_text_field.IndicatorSetOutlineAlpha(indicator_number, 255)
            self._used_indicators[indicator_number] = False
            indicator_number += 1

        # We have indicators 0-29 and can have 0-31, add two thick underlines
        self._main_text_field.IndicatorSetStyle(indicator_number, wx.stc.STC_INDIC_COMPOSITIONTHICK)
        self._main_text_field.IndicatorSetForeground(indicator_number,  wx.Colour(255, 0, 0))
        self._main_text_field.IndicatorSetAlpha(indicator_number, 255)
        self._main_text_field.IndicatorSetOutlineAlpha(indicator_number, 255)
        self._used_indicators[indicator_number] = False
        indicator_number += 1
        self._main_text_field.IndicatorSetStyle(indicator_number, wx.stc.STC_INDIC_COMPOSITIONTHICK)
        self._main_text_field.IndicatorSetForeground(indicator_number, wx.Colour(0, 255, 0))
        self._main_text_field.IndicatorSetAlpha(indicator_number, 255)
        self._main_text_field.IndicatorSetOutlineAlpha(indicator_number, 255)
        self._used_indicators[indicator_number] = False

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

    def _init_layout(self):
        """
        Main layout initialization.
        :return:
        """
        self._repetition_selector = wx.SpinCtrl(self, id=wx.ID_ANY,
                                                value=str(Constants.config_min_repetitions_default),
                                                style=wx.SP_ARROW_KEYS,
                                                min=Constants.config_min_repetitions,
                                                max=Constants.config_max_repetitions,
                                                initial=Constants.config_min_repetitions_default)

        self._min_repeated_word_length_selector = wx.SpinCtrl(self, id=wx.ID_ANY,
                                                              value=str(Constants.config_min_repetitions_default),
                                                              style=wx.SP_ARROW_KEYS,
                                                              min=Constants.config_min_len,
                                                              max=Constants.config_max_len,
                                                              initial=Constants.config_min_len_default)

        self._max_repeated_word_length_selector = wx.SpinCtrl(self, id=wx.ID_ANY,
                                                              value=str(Constants.config_max_len),
                                                              style=wx.SP_ARROW_KEYS,
                                                              min=Constants.config_min_len,
                                                              max=Constants.config_max_len,
                                                              initial=Constants.config_max_len)

        self.Bind(wx.EVT_SPINCTRL, self._handle_marking_selector, self._repetition_selector)
        self.Bind(wx.EVT_SPINCTRL, self._handle_marking_selector, self._min_repeated_word_length_selector)
        self.Bind(wx.EVT_SPINCTRL, self._handle_marking_selector, self._main_text_field)


        self._main_text_field = stc.StyledTextCtrl(self, style=wx.TE_MULTILINE)
        self._main_text_field.SetWrapMode(1)
        self._main_text_field.SetCodePage(wx.stc.STC_CP_UTF8)
        self._main_text_field.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self._main_text_field.SetMarginMask(1, 0)
        self._main_text_field.SetMarginWidth(1, 30)
        # todo Add a list view and a statistics area.
        #  show a list of all words sorted by repetitions and have a checkbox to enable or disable their coloring.
        #  show words with 2 or more repetitions and their average distance in lines, on click show lines where they are.

        # Initialize word list:
        self._side_word_list = SidePanel(self)
        side_word_border_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, Strings.label_words)
        font = side_word_border_sizer.GetStaticBox().GetFont()
        font.SetPointSize(Constants.static_box_font_size)
        side_word_border_sizer.GetStaticBox().SetFont(font)
        side_word_border_sizer.Add(self._side_word_list, 1, wx.EXPAND)

        self._search_text_field = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self._search_button_up = wx.BitmapButton(self, -1, wx.ArtProvider.GetBitmap(wx.ART_GO_UP))
        self._search_button_down = wx.BitmapButton(self, -1, wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN))
        self._search_results = wx.StaticText(self, -1, label=Strings.label_search_results.format(0, 0))

        self.Bind(EVT_CHECKBOX_CHANGED, self._word_list_handler)

        self.Bind(wx.EVT_BUTTON, self._search_up, self._search_button_up)
        self.Bind(wx.EVT_BUTTON, self._search_down, self._search_button_down)

        self.Bind(wx.EVT_TEXT, self._search, self._search_text_field)
        self.Bind(wx.EVT_TEXT_ENTER, self._search_enter, self._search_text_field)
        # Initialize search shortcut into accelerator table
        new_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self._focus_to_search, id=new_id)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('F'), new_id)])
        self.SetAcceleratorTable(accel_tbl)

        main_vertical_box = wx.BoxSizer(wx.VERTICAL)
        main_horizontal_box = wx.BoxSizer(wx.HORIZONTAL)
        toolbar_horizontal_box = wx.BoxSizer(wx.HORIZONTAL)

        coloring_repetitions_box = wx.StaticBoxSizer(wx.HORIZONTAL, self, Strings.label_coloring_box_rep)
        font = coloring_repetitions_box.GetStaticBox().GetFont()
        font.SetPointSize(Constants.static_box_font_size)
        coloring_repetitions_box.GetStaticBox().SetFont(font)

        coloring_len_min_box = wx.StaticBoxSizer(wx.HORIZONTAL, self, Strings.label_coloring_box_min_len)
        font = coloring_len_min_box.GetStaticBox().GetFont()
        font.SetPointSize(Constants.static_box_font_size)
        coloring_len_min_box.GetStaticBox().SetFont(font)

        coloring_len_max_box = wx.StaticBoxSizer(wx.HORIZONTAL, self, Strings.label_coloring_box_max_len)
        font = coloring_len_max_box.GetStaticBox().GetFont()
        font.SetPointSize(Constants.static_box_font_size)
        coloring_len_max_box.GetStaticBox().SetFont(font)

        search_box = wx.StaticBoxSizer(wx.HORIZONTAL, self, Strings.label_search_box)
        search_box.SetMinSize(width=350, height=-1)
        font = search_box.GetStaticBox().GetFont()
        font.SetPointSize(Constants.static_box_font_size)
        search_box.GetStaticBox().SetFont(font)

        # todo select word and context menu to set lengths?

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
        toolbar_horizontal_box.Add(search_box, 0, wx.LEFT, Constants.default_border)

        main_vertical_box.Add(toolbar_horizontal_box, 0)
        main_vertical_box.Add(main_horizontal_box, 1, wx.EXPAND)
        main_horizontal_box.Add(self._main_text_field, 4, wx.EXPAND | wx.BOTTOM | wx.LEFT, Constants.default_border)
        main_horizontal_box.Add(side_word_border_sizer, 0, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, Constants.default_border)

        self.SetSizer(main_vertical_box)

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
    # ------------------------------------------------------------------------------------------------------------------

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

    def _disable_editor(self) -> None:
        """
        Disable all features.
        :return: None
        """
        self._repetition_selector.Disable()
        self._min_repeated_word_length_selector.Disable()
        self._max_repeated_word_length_selector.Disable()
        self._main_text_field.Disable()
        for t in self._tools:
            if t.GetId() not in [wx.ID_NEW, wx.ID_OPEN]:
                self._toolbar.EnableTool(t.GetId(), False)
        for i in self._menu_items:
            if i.GetId() not in [wx.ID_NEW, wx.ID_OPEN, wx.ID_EXIT,  wx.ID_ABOUT]:
                i.Enable(False)

    def _enable_editor(self) -> None:
        """
        Enable all features of the editor.
        :return: None
        """
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

    def _focus_to_search(self, event: wx.CommandEvent) -> None:
        """
        Handles Ctrl+F shortcut to set focus into the search box.
        :param event: Not used
        :return: None
        """
        self._search_text_field.SetFocus()

    def _search(self, event: wx.CommandEvent) -> None:
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
            self._search_results.SetLabel(Strings.label_search_results.format(1 if self._found_words else 0, len(self._found_words)))
            if self._found_words:
                self._main_text_field.SetSelection(self._found_words[0][0][0], self._found_words[0][0][1])
                self._main_text_field.VerticalCentreCaret()
        else:
            self._found_last_index = 0
            self._found_words.clear()
            self._main_text_field.SetSelection(0,0)
            self._search_results.SetLabel(label=Strings.label_search_results.format(0, 0))

    def _search_enter(self, event: wx.CommandEvent) -> None:
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
                                              format(self._found_words[self._found_last_index][1] if self._found_words else 0,
                                                     len(self._found_words)))
            else:
                # Restart search when the text was edited.
                self._search(event)
        except IndexError as _:
            if event.GetString() == 'up':
                self._found_last_index = len(self._found_words)
            else:
                self._found_last_index = 0

    def _search_up(self, event: wx.CommandEvent) -> None:
        """
        Search button up handler.
        :param event: Used to set direction.
        :return: None
        """
        event.SetString('up')
        self._search_enter(event)

    def _search_down(self, event: wx.CommandEvent) -> None:
        """
        Search button down handler.
        :param event: Not used.
        :return: None
        """
        self._search_enter(event)

    def _undo(self, event: wx.CommandEvent) -> None:
        """
        Undo last change.
        :param event: Not used.
        :return: None
        """
        self._main_text_field.Undo()
        self._main_text_field.Refresh()

    def _redo(self, event: wx.CommandEvent) -> None:
        """
        Redo last change.
        :param event: Not used.
        :return: None
        """
        self._main_text_field.Redo()
        self._main_text_field.Refresh()

    def _new_file(self, event: wx.CommandEvent) -> None:
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

    def _info_word_counts(self, event: wx.CommandEvent) -> None:
        """
        Show a dialog with information about word counts.
        :param event: Not used.
        :return: None
        """
        WordInfoDialog(self, self._current_document.get_word_marking_data())

    def _clear_editor(self) -> None:
        """
        Clear the gui to default state.
        :return: None
        """
        self._main_text_field.ClearAll()

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

    def _apply_indicators(self, event: wx.CommandEvent) -> None:
        """
        Apply word repetition indicators into text.
        :param event: Not used
        :return: None
        """
        # Clear before reapplying.
        for indicator in self._used_indicators.keys():
            self._main_text_field.SetIndicatorCurrent(indicator)
            self._main_text_field.IndicatorClearRange(0, self._main_text_field.GetTextLength())
            self._used_indicators[indicator] = False
            if not self._selected_words:
                # todo this does not work, it clears everything, clear just data
                self._side_word_list.clear_list()

        colorize_tool: ToolBarToolBase = self._toolbar.FindById(wx.ID_APPLY)
        if not colorize_tool.IsToggled():
            self._main_text_field.Refresh()
            self._side_word_list.clear_list()
            self._selected_words.clear()
            return
        else:
            # Saving splits the new document into words for coloring.
            self._save_file()
            # todo list of default ignored words + metadata
            word_data: List[Word] = self._current_document.get_word_marking_data()
            repetition_limit = self._repetition_selector.GetValue()
            length_min_limit = self._min_repeated_word_length_selector.GetValue()
            length_max_limit = self._max_repeated_word_length_selector.GetValue()

            all_words = []

            # Filter the words that fit the criteria to a new list and work on that.
            for w in sorted(word_data, reverse=True):
                word = w.get_word()
                count = w.get_count()
                if count >= repetition_limit and length_min_limit <= len(word) <= length_max_limit:
                    if word.decode('utf-8') in self._selected_words:
                        w.set_selected(True)
                    all_words.append(w)

            # Assign indicators to filtered words.
            for w in sorted(all_words, reverse=True):
                indicator_n = -1
                # Find first unused indicator ID.
                for i_id, state in self._used_indicators.items():
                    if not state:
                        indicator_n = i_id
                        break

                if indicator_n == -1:
                    # todo handle not enough indicators
                    pass
                    #print(f'not enough indicators for: {word}, {count}')
                else:
                    if self._selected_words:
                        if w.is_selected():
                            # Give indicators only to words selected in the side panel list.
                            w.set_indicator(indicator_n)
                            self._used_indicators[indicator_n] = True
                    else:
                        # The tool is running for the first time, assign indicators to everything top down.
                        w.set_indicator(indicator_n)
                        self._used_indicators[indicator_n] = True

            # Display indicators.
            for w in all_words:
                if w.has_indicator():
                    indicator = w.get_indicator()
                    locations = w.get_spans()
                    for word_span in locations:
                        word_span: re.Match
                        self._main_text_field.SetIndicatorCurrent(indicator)
                        self._main_text_field.IndicatorFillRange(word_span.span()[0],
                                                                 word_span.span()[1] - word_span.span()[0])
            # Fill word list.
            if not self._selected_words:
                # Fill only once.
                word_index = 0
                new_items = {}
                for w in sorted(all_words, reverse=True):
                    w: Word
                    new_items[word_index] = (w, True if w.has_indicator() else False)
                    word_index += 1
                self._side_word_list.add_items(new_items)
            else:
                # todo do not reassign indicators?
                for w in sorted(all_words, reverse=True):
                    w: Word
                    if not w.is_selected():
                        w.set_indicator(-1)
        self._main_text_field.Refresh()
        self._update_indicator_count()

    def _update_indicator_count(self) -> None:
        """
        Update how many free indicators we have in the status panel.
        :return: None
        """
        used = sum(self._used_indicators.values())
        # 32 is our maximum number of usable indicators.
        self._set_status_text(Strings.status_indicators.format(used, 32 - used), 3)

    def _handle_marking_selector(self, event: wx.CommandEvent) -> None:
        """
        Handle changes to word repetition spin ctrls.
        :param event: Not used.
        :return: None
        """
        colorize_tool: ToolBarToolBase = self._toolbar.FindById(wx.ID_APPLY)
        if colorize_tool.IsToggled():
            self._apply_indicators(event)

    def _word_list_handler(self, event: dv.DataViewEvent) -> None:
        """
        Handle checkboxes in the side word list.
        This even fires after the checkbox has been changed.
        :param event: Passed along.
        :return: None
        """
        # todo do we need to save each time or would splitting it be faster?
        # todo if we do not have spare indicators prevent clicking more checkboxes, show a warning.
        # todo re-enable if we do have spare indicators.
        # todo disabling the last indicator enables all of them again.

        self._selected_words.clear()
        for item in self._side_word_list.GetChildren():
            item: ListItemPanel
            checked = item.is_checked()
            word = item.get_word()
            if item.is_checked():
                self._selected_words.append(item.get_word().get_word().decode('utf-8'))
        self._apply_indicators(event)
        # todo show how many free indicators we have somewhere.
        spare_indicators = not all(self._used_indicators.values())
        print(spare_indicators)

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

    def _make_bold(self, event: wx.CommandEvent) -> None:
        """
        Change text to bold.
        :param event: Not used.
        :return: None
        """
        start_pos = self._main_text_field.GetSelectionStart()
        style = self._main_text_field.GetStyleAt(start_pos)
        if style == self._style_map[Constants.style_bold]:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        self._style_map[Constants.style_default])
        elif style == self._style_map[Constants.style_italic]:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        self._style_map[Constants.style_bold_italic])
        elif style == self._style_map[Constants.style_bold_italic]:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        self._style_map[Constants.style_italic])
        else:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        self._style_map[Constants.style_bold])

    def _make_italic(self, event: wx.CommandEvent) -> None:
        """
        Change text to italic.
        :param event: Not used.
        :return: None
        """
        start_pos = self._main_text_field.GetSelectionStart()
        style = self._main_text_field.GetStyleAt(start_pos)
        if style == self._style_map[Constants.style_italic]:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        self._style_map[Constants.style_default])
        elif style == self._style_map[Constants.style_bold]:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        self._style_map[Constants.style_bold_italic])
        elif style == self._style_map[Constants.style_bold_italic]:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        self._style_map[Constants.style_bold])
        else:
            self._apply_style_with_undo(start_pos, len(self._main_text_field.GetSelectedText()),
                                        self._style_map[Constants.style_italic])

    def _text_statistics(self) -> None:
        """
        Update the status bar with text information.
        :return: None
        """
        lines = self._main_text_field.NumberOfLines
        words = len(self._main_text_field.GetText().split())
        chars = self._main_text_field.GetLastPosition()
        self._set_status_text(Strings.status_doc_info.format(lines, words, chars), 0)

    def on_modified(self, event: wx._stc.StyledTextEvent) -> None:
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
        # todo statistics calls are slow on large documents, run in background.
        wx.CallLater(Constants.statistics_delay, self._text_statistics)

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

    def _clear_styles(self, event: wx.CommandEvent) -> None:
        """
        Change text to default style.
        :param event: Not used.
        :return: None
        """
        start_pos = self._main_text_field.GetSelectionStart()
        self._main_text_field.StartStyling(start_pos)
        self._main_text_field.SetStyling(len(self._main_text_field.GetSelectedText()),
                                             self._style_map[Constants.style_default])

    def _append_styled_text(self, text: str, style: str) -> None:
        """
        Add text to text area with style.
        :param text: The text to add.
        :param style: Style name.
        :return: None
        """
        start_pos = self._main_text_field.GetLength()
        self._main_text_field.AppendText(text)
        self._main_text_field.StartStyling(start_pos)
        self._main_text_field.SetStyling(len(text), self._style_map[style])

    def _load_document(self, file_path: Path) -> None:
        """
        Load document into editor. Rtf can not be used by richtextctrl yet.
        :param file_path: Document path.
        :return: None
        """
        # todo Open in background eventually and disable the editor in the meanwhile.
        self._main_text_field.Freeze()
        self._toolbar.ToggleTool(wx.ID_APPLY, False)
        self._toolbar.Refresh()
        # Clear search
        self._found_last_index = 0
        self._found_words.clear()
        self._search_text_field.SetValue('')
        self._side_word_list.clear_list()
        self._current_document = Document(file_path)
        try:
            self._current_document.read_document()
        except PermissionError as _:
            self._show_error_ok_dialog(Strings.err_file_permissions)
            return
        except AttributeError as _:
            self._show_error_ok_dialog(Strings.err_file_format)
            return
        errors = self._current_document.get_errors()
        if errors:
            formatted = ''
            for e in errors:
                formatted += f"{e}\n"
            self._show_error_ok_dialog(Strings.warn_errors.format(formatted))
            return

        self._set_status_text(self._current_document.get_path().name, 1)
        parsed_text = self._current_document.get_parsed_text()
        for style, content in parsed_text:
            if style == 'break':
                self._main_text_field.AppendText('\n')
            else:
                self._append_styled_text(content, style)

        self._main_text_field.EmptyUndoBuffer()
        self._current_document.split_words(self._main_text_field.GetText())
        self._main_text_field.Thaw()
        self.SetTitle(Strings.app_title.format(self._current_document.get_path().name))
        # on_modified will run while loading and erroneously set modified to True so we need to fix it.
        self._current_document.set_modified(False)
        self._enable_editor()
        self._main_text_field.SetFocus()
        wx.CallLater(Constants.statistics_delay, self._text_statistics)

    def _save_file(self, save_as: bool = False) -> None:
        """
        Save current file and optionally show a save as dialog.
        :param save_as: True to show dialog.
        :return: None
        """
        # todo save in background eventually. Autosave on timer.
        # todo metadata raw text editor/parser-checker?
        self._main_text_field.Freeze()
        destination = self._current_document.get_path()
        if self._current_document.is_new() or save_as:
            destination = self._open_save_dialog()

        if destination:
            self._current_document.set_path(Path(destination))
            self._current_document.set_converted(self._convert_document())
            try:
                if self._current_document.save_document():
                    self._set_status_text(Strings.status_saved, 0)
                    self._set_status_text(self._current_document.get_path().name, 1)
                    self._main_text_field.SetSavePoint()
                    self.SetTitle(Strings.app_title.format(self._current_document.get_path().name))
                    self._current_document.split_words(self._main_text_field.GetText())
                    self._config.set_last_file(self._current_document.get_path())
                    self._config.save_config()
                    self._current_document.set_modified(False)
                    self._main_text_field.Thaw()
                else:
                    self._set_status_text(Strings.status_not_saved, 0)
            except PermissionError as _:
                self._show_error_ok_dialog(Strings.err_file_permissions_save)
                self._set_status_text(Strings.status_not_saved, 0)
        else:
            # Canceled dialog.
            self._set_status_text(Strings.status_not_saved, 0)
            self._main_text_field.Thaw()
            return
        wx.CallLater(Constants.statistics_delay, self._text_statistics)

    def _convert_document(self) -> List:
        """
        Extracts text and styling into the simple dictionary format and stores it in the Document class.
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

                for style, style_id in self._style_map.items():
                    if style_id == current_style:
                        converted.append((style, escaped_text))

                current_style = style_at_pos
                chunk_start = pos
        # Save last chunk where the style does not change.
        text_chunk = self._main_text_field.GetTextRange(chunk_start, length)
        for style, style_id in self._style_map.items():
            if style_id == current_style:
                converted.append((style, html.escape(text_chunk)))
        return converted

    def _save_file_handler(self, event: wx.CommandEvent) -> None:
        """
        Save file.
        :param event: Not used
        :return: None
        """
        self._save_file()

    def _save_as_file_handler(self, event: wx.CommandEvent) -> None:
        """
        Save file.
        :param event: Not used
        :return: None
        """
        self._save_file(save_as=True)

    def _emergency_save(self) -> None:
        """
        User is performing an action that could destroy the document, ask for save.
        :return: None
        """
        if self._current_document.is_modified():
            if self._show_yes_no_dialog(Strings.warn_file_not_saved.format(self._current_document.get_path().name),
                                        wx.ICON_ASTERISK):
                self._save_file()

    def _quit(self, _) -> None:
        """
        Quit the program.
        :param _: Unused
        :return: None
        """
        if self._current_document:
            self._emergency_save()
        self.Close()

    def _on_exit(self, event: wx.CommandEvent) -> None:
        """
        Closing the window with X.
        :param event: Not used.
        :return: None
        """
        if self._current_document:
            self._emergency_save()
        self.Destroy()

    def _about(self, event: wx.CommandEvent) -> None:
        """
        Show the About dialog.
        :param event: Not used.
        :return: None
        """
        AboutDialog(self)