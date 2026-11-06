import multiprocessing

from Constants import Constants


class StatisticsProcess(multiprocessing.Process):
    """
    Text statistics thread
    """

    def __init__(self, text: str, queue: multiprocessing.SimpleQueue) -> None:
        """
        Process constructor.
        :param text: Data prepared for saving.
        :param queue: The Frame that called the thread.
        :return: None
        """
        super().__init__()
        self._text = text
        self._queue = queue

    def run(self) -> None:
        """
        Count various statistics on text and send them back to the main thread.
        :return: None
        """
        self._queue.put((Constants.process_id_statistics, len(self._text.split())))
