import json
import logging
import re

import torch
import sounddevice as sd
import numpy as np

logger = logging  .getLogger(__name__)

class TTS:
    def __init__(self):
        self.language = 'ru'
        self.model_id = 'v3_1_ru'
        self.sample_rate = 48000
        self.speaker = 'eugene'
        self.model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                          model='silero_tts',
                          language=self.language,
                          speaker=self.model_id)

    def speak(self, text):
        from core.web_ai.engine import AIModel

        if self.needs_ai_normalization(text):
            logger.info("Invalid characters were found in the text for voiceover, request to normalize the text...")
            response = AIModel().request_to_ai(f"Your task is to paraphrase the text so that it is fully readable to the voice-over, so that instead of 444 it is four hundred and forty-four and so on. You can use the type - text command, paraphrasing the text into a message. Without the “here is your text:”. Write the whole text in one command.It's also important to reply in Russian, text: \n{text}", min_context=True)
            clear_text = json.loads(response)[0]["message"]
        else:
            clear_text = text
        audio = self.model.apply_tts(text=clear_text, speaker=self.speaker, sample_rate=self.sample_rate)

        sd.play(np.array(audio), samplerate=self.sample_rate)
        sd.wait()

    @staticmethod
    def needs_ai_normalization(text: str) -> bool:
        if re.search(r"[A-Za-z]", text):
            return True

        if re.search(r"\d", text):
            return True

        if re.search(r"[\"#@^~_=<>\\{}\[\]*&$%№]", text):
            return True

        if len(text) > 500:
            return True

        return False
