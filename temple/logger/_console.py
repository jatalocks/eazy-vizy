import json
import yaml
import re
from shutil import get_terminal_size
from threading import Event, Thread

# from .._request import RequestState

# From cli-spinners (https://www.npmjs.com/package/cli-spinners)
INTERVAL = 0.080  # seconds
FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

COLORS = dict(red=31, green=32, yellow=33, blue=34, grey=90)


class ConsoleLogger:
    def __init__(self):
        self._active = None
        self._stop_event = Event()

    def bold(self, text):
        return f"\033[1m{text}\033[22m"

    def color(self, text, color):
        return f"\033[{COLORS[color]}m{text}\033[0m"

    def error(self, error):
        text = str(error)
        if not text:
            return

        error_text = self.bold(self.color("ERROR:", "red"))
        print(f"{error_text} {text}")

    def close(self):
        self._stop_event.set()
        if self._active:
            self._active.join()
            self._active = None
