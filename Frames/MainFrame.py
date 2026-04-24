import shutil
from pathlib import Path
from typing import List

import wx
import wx.stc as stc
from wx._core import StatusBar, ToolBar
from wx.svg import SVGimage

from Constants import Constants
from Constants import Strings
from Containers.Document import Document
from Dialogs.AboutDialog import AboutDialog
from Resources.Fetch import Fetch


# todo spell check
# todo ai integration
# todo ask for save on exit

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

        self._main_text_field: stc.StyledTextCtrl = None
        self._side_text_field: wx.TextCtrl = None

        self._current_document: Document = None
        self._status_bar: StatusBar = None
        self._toolbar: ToolBar = None
        self._tools: List[wx.ToolBarToolBase] = []
        self._menu_items: List[wx.MenuItem] = []
        self._style_map = {'default': 0,
                           'bold': 1,
                           'italic': 2,
                           'bold_italic': 3}

        self._init_menu_bar()
        self._init_tool_bar()
        self._init_layout()
        self._init_status_bar()
        self._set_styles()
        self._disable_editor()
        self._set_status_text(Strings.status_ready, 0)
        self._set_status_text(Strings.status_no_document, 1)

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

        # About menu:
        about_menu = wx.Menu()
        about_menu_item_about = about_menu.Append(wx.ID_ABOUT, Strings.menu_item_about, Strings.menu_item_about_hint)
        self._menu_items.append(about_menu_item_about)

        menubar.Append(file_menu, Strings.menu_file)
        menubar.Append(edit_menu, Strings.menu_edit)
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

        # Special events
        self.Bind(wx.EVT_TEXT, self._text_changed, self._main_text_field)

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

    def _set_styles(self) -> None:
        """
        Set stc styles.
        :return: None
        """
        self._main_text_field.StyleSetFaceName(stc.STC_STYLE_DEFAULT, "Courier New")
        self._main_text_field.StyleSetSize(stc.STC_STYLE_DEFAULT, 10)
        self._main_text_field.StyleSetForeground(stc.STC_STYLE_DEFAULT, wx.Colour(0, 0, 0))
        self._main_text_field.StyleSetBackground(stc.STC_STYLE_DEFAULT, wx.Colour(255, 255, 255))
        self._main_text_field.StyleSetBold(stc.STC_STYLE_DEFAULT, False)
        self._main_text_field.StyleSetItalic(stc.STC_STYLE_DEFAULT, False)

        # Apply style.
        self._main_text_field.StyleClearAll()

        self._main_text_field.StyleSetSpec(1, "bold")
        self._main_text_field.StyleSetSpec(2, "italic")
        self._main_text_field.StyleSetSpec(3, "italic,bold")

        # todo styles for background colors.

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
        # todo switch to scintilla
        self._main_text_field = stc.StyledTextCtrl(self, style=wx.TE_MULTILINE)
        self._main_text_field.SetWrapMode(1)
        self._side_text_field = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE | wx.TE_RICH2 |
                                                        wx.TE_WORDWRAP)

        main_horizontal_box = wx.BoxSizer(wx.HORIZONTAL)
        main_horizontal_box.Add(self._main_text_field, 3, wx.EXPAND | wx.BOTTOM | wx.LEFT, Constants.default_border)
        main_horizontal_box.Add(self._side_text_field, 1, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, Constants.default_border)

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

    def _show_error_dialog(self, error: str) -> None:
        """
        Display an error dialog with the error text. Set error state into the status bar.
        :param error: The error to display in the dialog.
        :return: None
        """
        wx.MessageBox(error, Strings.status_warning, wx.OK | wx.ICON_WARNING)
        self._set_status_text(Strings.status_warning, 1)

    def _text_changed(self, event: wx.CommandEvent) -> None:
        """
        Undo last change.
        :param event: Not used.
        :return: None
        """
        # todo the text ctrl is very slow with lots of text, use styledtextctrl?
        print(self._main_text_field.NumberOfLines)

    def _undo(self, event: wx.CommandEvent) -> None:
        """
        Undo last change.
        :param event: Not used.
        :return: None
        """
        self._main_text_field.Undo()

    def _redo(self, event: wx.CommandEvent) -> None:
        """
        Redo last change.
        :param event: Not used.
        :return: None
        """
        self._main_text_field.Redo()

    def _new_file(self, event: wx.CommandEvent) -> None:
        """
        Create a new empty file.
        :param event: Not used.
        :return: None
        """
        if self._current_document:
            self._show_error_dialog(Strings.warn_file_not_saved.format(self._current_document.get_path().name))
            self._save_file()

        location = self._open_save_dialog()
        if location:
            # Replace the current document with a new one.
            self._clear_editor()
            if not location.endswith(".html"):
                location = f"{location}.html"
            shutil.copy(Path(Fetch.get_resource_path('template.html')), location)
            self._load_document(Path(location))
        else:
            # todo new file dialog canceled anything to do here?`
            pass

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
        # todo if a file is already loaded, save it and clear
        if self._current_document:
            self._show_error_dialog(Strings.warn_file_not_saved.format(self._current_document.get_path().name))
            self._save_file()

        dialog = wx.FileDialog(self, Strings.dialog_open, "", "", Constants.html_wildcard,
                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            self._clear_editor()
            self._load_document(Path(dialog.GetPath()))

    def _make_bold(self, event: wx.CommandEvent) -> None:
        """
        Change text to bold.
        :param event: Not used.
        :return: None
        """
        # todo fix these
        self._main_text_field.ApplyBoldToSelection()

    def _make_italic(self, event: wx.CommandEvent) -> None:
        """
        Change text to italic.
        :param event: Not used.
        :return: None
        """
        self._main_text_field.ApplyItalicToSelection()

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
        self._main_text_field.Freeze()
        self._current_document = Document(file_path)
        # todo handle exceptions from read document.
        self._current_document.read_document()
        self._set_status_text(self._current_document.get_path().name, 1)
        parsed_text = self._current_document.get_parsed_text()
        for p in parsed_text:
            if not p:
                # <p></p>
                self._main_text_field.AppendText('\n')
            elif len(p) > 0:
                for style, content in p:
                    if style == 'bold':
                        self._append_styled_text(content, style)
                    elif style == 'italic':
                        self._append_styled_text(content, style)
                    elif style == 'bold_italic':
                        self._append_styled_text(content, style)
                    elif style == 'text':
                        self._append_styled_text(content, 'default')
                    elif style == 'break':
                        self._main_text_field.AppendText('\n')
                self._main_text_field.AppendText('\n')
        self._main_text_field.Refresh()
        # todo Open in background eventually and disable the editor in the meanwhile.

        self._main_text_field.Thaw()
        self.SetTitle(Strings.app_title.format(self._current_document.get_path().name))
        self._enable_editor()

    def _save_file(self, save_as: bool = False) -> None:
        """
        Save current file and optionally show a save as dialog.
        :param save_as: True to show dialog.
        :return: None
        """
        # todo save in background eventually. Autosave on timer.
        # todo the current document must be effectively switched to the save as new file.
        # todo indicate changes to file in window title.
        self._main_text_field.Freeze()
        if self._current_document.is_new() or save_as:
            destination = self._open_save_dialog()
            if destination:
                self._current_document.set_path(Path(destination))
                if self._current_document.save_document():
                    self._set_status_text(Strings.status_saved, 0)
                    self._set_status_text(self._current_document.get_path().name, 1)
                else:
                    self._set_status_text(Strings.status_not_saved, 0)
            else:
                # Canceled dialog.
                self._set_status_text(Strings.status_not_saved, 0)
                return
        else:
            if self._current_document.save_document():
                self._set_status_text(Strings.status_saved, 0)
            else:
                self._set_status_text(Strings.status_not_saved, 0)
        self._main_text_field.Thaw()

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

    def _quit(self, _) -> None:
        """
        Quit the program.
        :param _: Unused
        :return: None
        """
        self.Close()

    def _about(self, event: wx.CommandEvent) -> None:
        """
        Show the About dialog.
        :param event: Not used.
        :return: None
        """
        AboutDialog(self)