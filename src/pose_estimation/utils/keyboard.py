import keyboard
import queue

class KeyboardListener:

    def __init__(self):
        self._input_queue = queue.Queue()
        keyboard.on_press(self._on_key_event)

    def _on_key_event(self, event):
        self._input_queue.put(event.name)

    def poll(self):
        try:
            return self._input_queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        keyboard.unhook_all()