"""
Conversion Worker — File Converter Pro
conversion_worker.py

Runs any conversion workload in a background QThread so the UI
never freezes.  Drop-in replacement for the blocking for-loops
that previously ran on the main thread.

Usage (from app.py):
    from conversion_worker import ConversionWorker

    self._worker = ConversionWorker(tasks, runner_fn)
    self._worker.progress.connect(self.progress_bar.setValue)
    self._worker.file_done.connect(self._on_file_done)
    self._worker.finished.connect(self._on_conversion_finished)
    self._worker.error.connect(self._on_conversion_error)
    self._worker.start()

Author: Hyacinthe
Version: 1.0
"""

from PySide6.QtCore import QThread, Signal

class ConversionWorker(QThread):
    """
    Generic background worker for file conversions.

    Parameters
    ----------
    tasks : list[dict]
        Each dict must have at minimum:
            'index'       : int   - position in the batch (0-based)
            'total'       : int   - total number of tasks
            'input_path'  : str   - source file path
            'output_path' : str   - destination file path
        Additional keys are forwarded verbatim to runner_fn.

    runner_fn : callable(task: dict) -> dict
        Called once per task, in the worker thread.
        Must return a result dict with at minimum:
            'success' : bool
            'error'   : str  (empty string on success)
        May add any extra keys (e.g. 'operation_time', 'file_size').
        Must NOT touch Qt widgets — communicate only via signals.
    """

    # int 0-100: overall progress across all tasks
    progress = Signal(int)

    # dict: result returned by runner_fn, augmented with the original task
    file_done = Signal(dict)

    # dict: summary {'success_count', 'total', 'failed', 'total_time'}
    finished = Signal(dict)

    # str: unexpected exception message (stops the batch)
    error = Signal(str)

    def __init__(self, tasks: list, runner_fn, parent=None):
        super().__init__(parent)
        self._tasks     = tasks
        self._runner_fn = runner_fn
        self._abort     = False

    def abort(self):
        """Request a graceful stop after the current file finishes."""
        self._abort = True

    def run(self):
        import time
        t0            = time.perf_counter()
        total         = len(self._tasks)
        success_count = 0
        failed        = []

        for task in self._tasks:
            if self._abort:
                break
            try:
                result = self._runner_fn(task)
            except Exception as exc:
                result = {"success": False, "error": str(exc)}

            result.update(task)          # merge original task keys into result

            if result.get("success"):
                success_count += 1
            else:
                failed.append({
                    "name":  task.get("input_path", "?"),
                    "error": result.get("error", "unknown error"),
                })

            idx = task.get("index", 0)
            self.progress.emit(int((idx + 1) / total * 100))
            self.file_done.emit(result)

        self.finished.emit({
            "success_count": success_count,
            "total":         total,
            "failed":        failed,
            "total_time":    time.perf_counter() - t0,
        })
