import logging
import os.path
import threading
import time

import sounddevice as sd
import queue
import vosk
import json

from core.tts import TTS
from core.web_ai.engine import main_handler

logger = logging.getLogger(__name__)

class STTHandler:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(self.base_dir, "../gui/setting.json"), encoding="utf-8") as f:
            content = json.load(f)
            self.wake_word = content["assistant_name"]

        if not os.path.exists(os.path.join(self.base_dir, "web_ai/chats/voice_input_chat.json")):
            open(os.path.join(self.base_dir, "web_ai/chats/voice_input_chat.json"), "w", encoding="utf-8").close()

        self.model_path = "core/assets/vosk-model-small-ru-0.22"
        self.session = False
        self.session_counter = 0
        self.q = queue.Queue()

    def audio_callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def start_session_counter(self):
        while self.session:
            self.session_counter += 1
            if self.session_counter == 15:
                self.session = False
            time.sleep(1)

    def listen_loop(self):
        model = vosk.Model(model_path=self.model_path)
        recognizer = vosk.KaldiRecognizer(model, 16000)

        with open(os.path.join(self.base_dir, "../gui/setting.json"), encoding="utf-8") as f:
            settings = json.load(f)

        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=self.audio_callback):
            logger.info("Starting voice listening")

            while True:
                data = self.q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if self.session and result.get("text") or result.get("text") and self.wake_word in result.get("text"):
                        logger.info("The assistant hears the wake word or session request and starts executing the request")

                        self.session_counter = 0
                        tts_thread = threading.Thread(target=TTS().speak, daemon=True, args=("Выполняю...",))
                        tts_thread.start()
                        handler_thread = threading.Thread(target=main_handler, daemon=True, args=(result["text"], "voice_input_chat.json", True, settings["tts"]))
                        handler_thread.start()
                        tts_thread.join()
                        handler_thread.join()
                        self.session_counter = 0


                        if self.wake_word in result["text"]:
                            self.session = True
                            threading.Thread(target=self.start_session_counter, daemon=True).start()