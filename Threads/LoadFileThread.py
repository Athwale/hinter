from threading import Thread

import wx

from Constants import Strings
from Containers.Document import Document
from Exceptions.FormatError import FormatError


class LoadFileThread(Thread):
    """
    Load a new document.
    """

    def __init__(self, parent, document: Document) -> None:
        """
        Thread constructor.
        :param parent: The Frame that called the thread.
        """
        super().__init__()
        self._parent = parent
        self._document = document
        self.start()

    def run(self) -> None:
        """
        Run the thread and load a document from disk.
        :return: None
        """
        try:
            self._document.read_document()
            for style, content in self._document.get_parsed_text():
                if style == 'break':
                    wx.CallAfter(self._parent.append_new_line)
                else:
                    wx.CallAfter(self._parent.append_styled_text, content, style)
            wx.CallAfter(self._parent.load_document_callback, '')
        except PermissionError as e:
            wx.CallAfter(self._parent.load_document_callback, str(e))
            return
        except AttributeError as _:
            wx.CallAfter(self._parent.load_document_callback, Strings.err_file_format)
            return
        except FormatError as e:
            wx.CallAfter(self._parent.load_document_callback, str(e))
            return
