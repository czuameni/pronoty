from PySide6.QtCore import QTimer

class AutoLock:
    def __init__(self, timeout_ms, lock_callback):
        self.timer = QTimer()
        self.timer.setInterval(timeout_ms)
        self.timer.timeout.connect(lock_callback)

    def start(self):
        self.timer.start()

    def reset(self):
        self.timer.start()