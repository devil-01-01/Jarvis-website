import sys
import time
import threading
from colorama import init, Fore, Style

class ThinkingLoader:
    def __init__(self):
        self._running = False
        self._thread = None

    def _animate(self):
        dots = [".  ", ".. ", "...", "   "]
        i = 0
        while self._running :
            print(f"\r Thinking{dots[i % 4]}", end="")
            i += 1
            time.sleep(0.4)
        print("\r" + ""*20 + "\r", end="", flush=True)

    def start(self):
        if not self._running:
            self._running = True
            self.thread = threading.Thread(target=self._animate, daemon=True)
            self.thread.start()

    def stop(self):
        if self._running :
            self._running = False
            if self.thread:
                self.thread.join()
