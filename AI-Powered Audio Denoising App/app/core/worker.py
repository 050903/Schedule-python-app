from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot
import traceback
import sys

class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)

class Worker(QRunnable):
    """
    Worker thread for running background tasks.
    """
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        try:
            # Add progress_callback and status_callback to kwargs
            self.kwargs['progress_callback'] = self.signals.progress.emit
            self.kwargs['status_callback'] = self.signals.status.emit
            
            result = self.fn(*self.args, **self.kwargs)
            
            # Return the result of the processing
            self.signals.result.emit(result)
        except:
            traceback_str = traceback.format_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback_str))
        finally:
            self.signals.finished.emit()