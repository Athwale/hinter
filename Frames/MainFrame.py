import sys
from pathlib import Path
from sys import path
from typing import List

import wx
from wx import richtext
from wx._core import StatusBar, ToolBar
from wx.svg import SVGimage

from Constants import Constants
from Constants import Strings
from Containers.Document import Document
from Resources.Fetch import Fetch


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
        super(MainFrame, self).__init__(None, title=Strings.app_title, size=Constants.main_window_size)

        self._main_text_field: richtext.RichTextCtrl = None
        self._html_handler = richtext.RichTextHTMLHandler()

        self._current_document: Document = None
        self._status_bar: StatusBar = None
        self._toolbar: ToolBar = None
        self._tools: List[wx.ToolBarToolBase] = []

        self._init_menu_bar()
        self._init_tool_bar()
        self._init_layout()
        self._init_status_bar()
        self._disable_editor()

    def _init_menu_bar(self) -> None:
        """
        Menu bar initialization.
        :return: None
        """
        # Init menu bar.
        menubar = wx.MenuBar()

        # todo bind handlers.

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
        edit_menu.AppendSeparator()
        edit_menu_item_bold = edit_menu.Append(wx.ID_BOLD, Strings.menu_item_bold, Strings.menu_item_bold_hint)
        edit_menu_item_italic = edit_menu.Append(wx.ID_ITALIC, Strings.menu_item_italic, Strings.menu_item_italic_hint)

        # About menu:
        about_menu = wx.Menu()
        about_menu_item_about = about_menu.Append(wx.ID_ABOUT, Strings.menu_item_about, Strings.menu_item_about_hint)

        menubar.Append(file_menu, Strings.menu_file)
        menubar.Append(edit_menu, Strings.menu_edit)
        menubar.Append(about_menu, Strings.menu_about)

        # Bind menu item handlers.
        self.Bind(wx.EVT_MENU, self._quit, file_menu_item_quit)
        self.Bind(wx.EVT_MENU, self._open_file, file_menu_item_open)
        self.Bind(wx.EVT_MENU, self._save_file, file_menu_item_save)
        self.Bind(wx.EVT_MENU, self._make_bold, edit_menu_item_bold)
        self.Bind(wx.EVT_MENU, self._make_italic, edit_menu_item_italic)
        self.Bind(wx.EVT_MENU, self._new_file, file_menu_item_new)

        self.SetMenuBar(menubar)

    def _init_tool_bar(self) -> None:
        """
        Toolbar initialization.
        :return: None
        """
        self._toolbar = self.CreateToolBar(style=wx.TB_DEFAULT_STYLE)

        new_tool = wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_NEW, Strings.menu_item_new,
                                                              wx.ArtProvider.GetBitmap(wx.ART_NEW),
                                                              Strings.menu_item_new)
        self._tools.append(new_tool)

        open_tool = wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_OPEN, Strings.menu_item_open,
                                                             wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN),
                                                             Strings.menu_item_open)
        self._tools.append(open_tool)

        save_tool = wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_SAVE, Strings.menu_item_save,
                                                             wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE),
                                                             Strings.menu_item_save)
        self._tools.append(save_tool)

        undo_tool = wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_UNDO, Strings.menu_item_undo,
                                                             wx.ArtProvider.GetBitmap(wx.ART_UNDO),
                                                             Strings.menu_item_undo)
        self._tools.append(undo_tool)

        redo_tool = wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_REDO, Strings.menu_item_redo,
                                                         wx.ArtProvider.GetBitmap(wx.ART_REDO),
                                                         Strings.menu_item_redo)
        self._tools.append(redo_tool)

        bold_tool = wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_BOLD, Strings.menu_item_bold,
                                                         self._scale_icon('bold.svg', Constants.icon_tool_width,
                                                                          Constants.icon_tool_height),
                                                         Strings.menu_item_bold)
        self._tools.append(bold_tool)

        italic_tool = wx.ToolBarToolBase = self._toolbar.AddTool(wx.ID_ITALIC, Strings.menu_item_italic,
                                                         self._scale_icon('italic.svg', Constants.icon_tool_width,
                                                                          Constants.icon_tool_height),
                                                         Strings.menu_item_italic)
        self._tools.append(italic_tool)

        self._toolbar.Realize()

        # todo bind handlers for unusual functions.
        #self.Bind(wx.EVT_TOOL, self.quit, open_file_tool)

    @staticmethod
    def _scale_icon(name: str, width: int, height: int) -> wx.Bitmap:
        """
        Helper method to prepare icons for toolbar.
        :param name: Icon file name in Resources.
        :param width: Desired icon width.
        :param height: Desired icon height.
        :return: The icon bitmap
        """
        path = Fetch.get_resource_path(name)
        svg_image = SVGimage.CreateFromFile(path)
        return svg_image.ConvertToScaledBitmap(wx.Size(width, height))

    def _init_layout(self):
        """
        Main layout initialization.
        :return:
        """
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

    def _disable_editor(self) -> None:
        """
        Disable all features.
        :return: None
        """
        # Todo disable until a document is loaded.
        self._main_text_field.Disable()
        for t in self._tools:
            if t.GetId() not in [wx.ID_NEW, wx.ID_OPEN]:
                self._toolbar.EnableTool(t.GetId(), False)

    def _enable_editor(self) -> None:
        """
        Enable all features of the editor.
        :return: None
        """
        self._main_text_field.Enable()
        for t in self._tools:
            self._toolbar.EnableTool(t.GetId(), True)

    def _new_file(self, event: wx.CommandEvent) -> None:
        """
        Create a new empty file.
        :param event: Not used.
        :return: None
        """
        # todo open file dialog to select a new file location.
        print("not done")

    def _open_file(self, event: wx.CommandEvent) -> None:
        """
        Open existing file for editing.
        :param event: Not used
        :return: None
        """
        dialog = wx.FileDialog(self, "Open", "", "", "Text files (*.html)|*.html",
                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            self._load_document(Path(dialog.GetPath()))

    def _make_bold(self, event: wx.CommandEvent) -> None:
        """
        Change text to bold.
        :param event: Not used.
        :return: None
        """
        self._main_text_field.ApplyBoldToSelection()

    def _make_italic(self, event: wx.CommandEvent) -> None:
        """
        Change text to italic.
        :param event: Not used.
        :return: None
        """
        self._main_text_field.ApplyItalicToSelection()

    def _load_document(self, path: Path) -> None:
        """
        Load document into editor. Rtf can not be used by richtextctrl yet.
        :param path: Document path.
        :return: None
        """
        self._main_text_field.Freeze()
        self._main_text_field.BeginSuppressUndo()

        self._current_document = Document(path)
        # todo handle exceptions from read document.
        self._current_document.read_document()
        self._set_status_text(self._current_document.get_path().name, 1)
        parsed_text = self._current_document.get_parsed_text()
        for p in parsed_text:
            if not p:
                # <p></p>
                self._main_text_field.Newline()
            elif len(p) > 0:
                for style, content in p:
                    if style == 'bold':
                        self._main_text_field.BeginBold()
                        self._main_text_field.WriteText(content)
                        self._main_text_field.EndBold()
                    elif style == 'italic':
                        self._main_text_field.BeginItalic()
                        self._main_text_field.WriteText(content)
                        self._main_text_field.EndItalic()
                    elif style == ('bold_italic'):
                        self._main_text_field.BeginBold()
                        self._main_text_field.BeginItalic()
                        self._main_text_field.WriteText(content)
                        self._main_text_field.EndItalic()
                        self._main_text_field.EndBold()
                    elif style == 'text':
                        self._main_text_field.WriteText(content)
                    elif style == 'break':
                        self._main_text_field.LineBreak()
                self._main_text_field.Newline()
        self._main_text_field.Refresh()
        # todo Open in background eventually and disable the editor in the meanwhile.

        self._main_text_field.Thaw()
        self._main_text_field.EndSuppressUndo()
        self._enable_editor()

    def _save_file(self, event: wx.CommandEvent) -> None:
        """
        Save file.
        :param event: Not used
        :return: None
        """
        # todo save in background eventually. Autosave on timer.
        self._main_text_field.Freeze()
        # todo open save dialog if new file.
        # todo save as variant.
        if self._current_document.save_document(self._html_handler, self._main_text_field.GetBuffer()):
            print("ok")
        else:
            print("no ok")
        self._main_text_field.Thaw()

    def _quit(self, _) -> None:
        """
        Quit the program.
        :param _: Unused
        :return: None
        """
        self.Close()