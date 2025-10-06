import time
from typing import Dict, Set, Callable, Optional, Any
from threading import Thread, Lock
import pygame


class InputManager:
    def __init__(self):
        self._pressed_keys: Set[int] = set()
        self._key_states: Dict[int, dict] = {}
        self._callbacks: Dict[str, Dict[int, list]] = {
            "press": {},
            "release": {},
            "hold": {},
        }
        self._hold_threads: Dict[int, Thread] = {}
        self._lock = Lock()
        self._running = False

    def start(self):
        if self._running:
            return
        self._running = True

    def stop(self):
        self._running = False
        # Stop all hold threads
        with self._lock:
            for thread in self._hold_threads.values():
                if thread.is_alive():
                    thread.join(timeout=0.1)
            self._hold_threads.clear()

    def handle_event(self, event):
        if not self._running:
            return

        if event.type == pygame.KEYDOWN:
            self._on_key_press(event.key)
        elif event.type == pygame.KEYUP:
            self._on_key_release(event.key)

    def _on_key_press(self, key: int):
        with self._lock:
            if key not in self._pressed_keys:
                self._pressed_keys.add(key)
                self._key_states[key] = {"press_time": time.time(), "is_held": False}

                # Trigger press callbacks
                self._trigger_callbacks("press", key)

                # Start hold monitoring thread
                hold_thread = Thread(target=self._monitor_hold, args=(key,))
                hold_thread.daemon = True
                self._hold_threads[key] = hold_thread
                hold_thread.start()

    def _on_key_release(self, key: int):
        with self._lock:
            if key in self._pressed_keys:
                self._pressed_keys.remove(key)

                # Clean up hold thread
                if key in self._hold_threads:
                    del self._hold_threads[key]

                # Trigger release callbacks
                self._trigger_callbacks("release", key)

                # Clean up key state
                if key in self._key_states:
                    del self._key_states[key]

    def _monitor_hold(self, key: int):
        hold_interval = 0.1  # Check every 100ms

        while self._running and key in self._pressed_keys:
            time.sleep(hold_interval)

            with self._lock:
                if key not in self._pressed_keys:
                    break

                if key in self._key_states:
                    if not self._key_states[key]["is_held"]:
                        self._key_states[key]["is_held"] = True

                    # Trigger hold callbacks
                    self._trigger_callbacks("hold", key)

    def _trigger_callbacks(self, event_type: str, key: int):
        if key in self._callbacks[event_type]:
            for callback in self._callbacks[event_type][key]:
                try:
                    callback(key)
                except Exception as e:
                    print(f"Error in {event_type} callback for key {key}: {e}")

    def on_key_press(self, key: int, callback: Callable[[int], Any]):
        if key not in self._callbacks["press"]:
            self._callbacks["press"][key] = []
        self._callbacks["press"][key].append(callback)

    def on_key_release(self, key: int, callback: Callable[[int], Any]):
        if key not in self._callbacks["release"]:
            self._callbacks["release"][key] = []
        self._callbacks["release"][key].append(callback)

    def on_key_hold(self, key: int, callback: Callable[[int], Any]):
        if key not in self._callbacks["hold"]:
            self._callbacks["hold"][key] = []
        self._callbacks["hold"][key].append(callback)

    def is_key_pressed(self, key: int) -> bool:
        with self._lock:
            return key in self._pressed_keys

    def get_pressed_keys(self) -> Set[int]:
        with self._lock:
            return self._pressed_keys.copy()

    def get_key_hold_duration(self, key: int) -> Optional[float]:
        with self._lock:
            if key in self._key_states:
                return time.time() - self._key_states[key]["press_time"]
            return None

    def remove_callback(
        self, event_type: str, key: int, callback: Callable[[int], None]
    ):
        if key in self._callbacks[event_type]:
            try:
                self._callbacks[event_type][key].remove(callback)
            except ValueError:
                pass

    def clear_callbacks(
        self, event_type: Optional[str] = None, key: Optional[int] = None
    ):
        if event_type is None:
            self._callbacks = {"press": {}, "release": {}, "hold": {}}
        elif key is None:
            self._callbacks[event_type] = {}
        else:
            if key in self._callbacks[event_type]:
                self._callbacks[event_type][key] = []
