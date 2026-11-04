import multiprocessing
from pathlib import Path

from Constants import Strings, Constants
from Containers.Document import Document
from Exceptions.FormatError import FormatError


class LoadFileProcess(multiprocessing.Process):
    """
    Load a new document.
    """

    def __init__(self, queue: multiprocessing.Queue, path: Path) -> None:
        """
        Thread constructor.
        :param queue: The Frame that called the thread.
        :param path: Document path.
        """
        super().__init__()
        # Storing parent is thread safe, the methods are called in CallAfter, not directly from the background thread.
        self._queue = queue
        self._path = path
        self.start()

    def run(self) -> None:
        """
        Run the thread and load a document from disk.
        :return: None
        """
        try:
            document = Document(self._path)
            document.read_document()
            self._queue.put((Constants.process_id_load, ('', document)))
        except PermissionError as e:
            self._queue.put((Constants.process_id_load, (str(e), None)))
            return
        except AttributeError as _:
            self._queue.put((Constants.process_id_load, (Strings.err_file_format, None)))
            return
        except FormatError as e:
            self._queue.put((Constants.process_id_load, (str(e), None)))
            return
