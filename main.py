import json
import os.path
import threading

from core.voice_input import STTHandler
from gui.main_gui import run_all
from gui.quick_access_gui import listen_hotkeys
from gui.tray import run_tray
from logger import logger

if __name__ == "__main__":
    logger.info("App starting...")
    threading.Thread(target=run_tray, daemon=True).start()
    threading.Thread(target=listen_hotkeys, daemon=True).start()

    if os.path.exists("gui/setting.json"):
        with open("gui/setting.json", encoding="utf-8") as f:
            content = json.load(f)
            if content["voice_input"]:
                voice_input = STTHandler()
                threading.Thread(target=voice_input.listen_loop, daemon=True).start()

    run_all()