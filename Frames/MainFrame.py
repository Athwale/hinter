from pathlib import Path

import wx
import wx.richtext
from wx import richtext

from Constants import Constants
from Constants import Strings

class MainFrame(wx.Frame):

    def __init__(self):
        super(MainFrame, self).__init__(None, title=Strings.app_title, size=Constants.main_window_size)

        self._main_text_field = None
        self._current_file = None
        self._status_bar = None

        self._init_menu_bar()
        self._init_tool_bar()
        self._init_layout()
        self._init_status_bar()

    def _init_menu_bar(self):
        # Init menu bar.
        menubar = wx.MenuBar()

        # todo bind handlers.
        # todo open simple text file handler. Open in background eventually.

        # File menu:
        file_menu = wx.Menu()
        # Standard id will automatically add an icon and a shortcut.
        # Last parameter defines the short help string that is displayed on the statusbar.
        file_menu_item_new = file_menu.Append(wx.ID_NEW, Strings.menu_item_new, Strings.menu_item_new_hint)
        file_menu_item_open = file_menu.Append(wx.ID_OPEN, Strings.menu_item_open, Strings.menu_item_open_hint)
        file_menu_item_save = file_menu.Append(wx.ID_SAVE, Strings.menu_item_save, Strings.menu_item_save_hint)
        file_menu_item_save_as = file_menu.Append(wx.ID_SAVEAS, Strings.menu_item_save_as, Strings.menu_item_save_as_hint)
        file_menu.AppendSeparator()
        file_menu_item_quit = file_menu.Append(wx.ID_EXIT, Strings.menu_item_quit, Strings.menu_item_quit_hint)

        # Edit menu:
        edit_menu = wx.Menu()
        edit_menu_item_undo = edit_menu.Append(wx.ID_UNDO, Strings.menu_item_undo, Strings.menu_item_undo_hint)
        edit_menu_item_redo = edit_menu.Append(wx.ID_REDO, Strings.menu_item_redo, Strings.menu_item_redo_hint)

        # About menu:
        about_menu = wx.Menu()
        about_menu_item_about = about_menu.Append(wx.ID_ABOUT, Strings.menu_item_about, Strings.menu_item_about_hint)

        menubar.Append(file_menu, Strings.menu_file)
        menubar.Append(edit_menu, Strings.menu_edit)
        menubar.Append(about_menu, Strings.menu_about)

        # Bind menu item handlers.
        self.Bind(wx.EVT_MENU, self._quit, file_menu_item_quit)
        self.Bind(wx.EVT_MENU, self._open_file, file_menu_item_open)

        self.SetMenuBar(menubar)

    def _init_tool_bar(self):
        toolbar = self.CreateToolBar(style=wx.TB_DEFAULT_STYLE)

        # todo do not use none, it shows as too hint
        new_tool = wx.ToolBarToolBase = toolbar.AddTool(wx.ID_NEW, Strings.menu_item_new,
                                                              wx.ArtProvider.GetBitmap(wx.ART_NEW),
                                                              Strings.menu_item_new)

        open_tool = wx.ToolBarToolBase = toolbar.AddTool(wx.ID_OPEN, Strings.menu_item_open,
                                                             wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN),
                                                             Strings.menu_item_open)

        save_tool = wx.ToolBarToolBase = toolbar.AddTool(wx.ID_SAVE, Strings.menu_item_save,
                                                             wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE),
                                                             Strings.menu_item_save)

        undo_tool = wx.ToolBarToolBase = toolbar.AddTool(wx.ID_UNDO, Strings.menu_item_undo,
                                                             wx.ArtProvider.GetBitmap(wx.ART_UNDO),
                                                             Strings.menu_item_undo)

        redo_tool = wx.ToolBarToolBase = toolbar.AddTool(wx.ID_REDO, Strings.menu_item_redo,
                                                         wx.ArtProvider.GetBitmap(wx.ART_REDO),
                                                         Strings.menu_item_redo)

        toolbar.Realize()

        # todo bind handlers
        #self.Bind(wx.EVT_TOOL, self.quit, open_file_tool)

    def _init_layout(self):
        self._main_text_field = richtext.RichTextCtrl(self, style=wx.VSCROLL | wx.NO_BORDER)
        right_panel = wx.Panel(self)

        right_panel.SetBackgroundColour('#4f5048')

        main_horizontal_box = wx.BoxSizer(wx.HORIZONTAL)
        main_horizontal_box.Add(self._main_text_field, 3, wx.EXPAND | wx.BOTTOM | wx.LEFT, Constants.default_border)
        main_horizontal_box.Add(right_panel, 1, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, Constants.default_border)

        self.SetSizer(main_horizontal_box)

    def _init_status_bar(self) -> None:
        """
        Set up status bar for the frame.
        :return: None
        """
        # Create a status bar with 3 fields
        self._status_bar = self.CreateStatusBar(3)
        self._status_bar.SetStatusWidths([-6, -7, -2])
        # Initialize status bar
        self._set_status_text('', 0)
        self._set_status_text('', 1)

    def _set_status_text(self, text: str, position=0) -> None:
        """
        Set a text into a position in status bar and prepend a separator.
        :param text: Text to set.
        :param position: Where to set the text, 0 is default
        :return: None
        """
        to_set = f'| {text}'
        self._status_bar.SetStatusText(to_set, position)

    def _open_file(self, e):
        dialog = wx.FileDialog(self, "Open", "", "", "Text files (*.txt)|*.txt",
                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            self._current_file = Path(dialog.GetPath())
            self._set_status_text(self._current_file.name, 1)

    def _quit(self, _):
        self.Close()