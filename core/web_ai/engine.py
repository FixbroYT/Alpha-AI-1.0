import json
import logging
import os
import threading
import time
from datetime import datetime

import pyautogui
import requests

from config import API_KEY_AI
from core.tts import TTS

logger = logging.getLogger(__name__)

class AIModel:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.api_key = API_KEY_AI

    def request_to_ai(self, content: str, is_context_need: bool = False, chat: str = "chat_1.json", min_context: bool = False):
        history_file = os.path.join(self.base_dir, "chats", chat)
        default_context = self.generate_default_context()
        min_context_text = 'You are a helper who helps with various tasks. Always return your response strictly in this JSON format: [{"command_type”: "text", ‘message’: "message as requested"}]. Reply only with correct JSON and nothing else.'

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        url = "https://api.groq.com/openai/v1/chat/completions"
        messages = [{"role": "system", "content": default_context if not min_context else min_context_text}]

        if is_context_need:
            if os.path.exists(history_file):
                with open(history_file, "r", encoding="utf-8") as f:
                    try:
                        messages = json.load(f)
                        messages[0]["content"] = default_context if not min_context else min_context_text
                    except json.JSONDecodeError:
                        logger.warning("History's been corrupted. We're starting over.")

        messages.append({"role": "user", "content": content})

        if len(messages) > 20:
            logger.info("Context is too long, sending last 20 messages")
            last_messages = [messages[0]]
            for message in messages[-19:]:
                last_messages.append(message)
                messages = last_messages
        elif chat == "voice_input_chat.json":
            logger.info("Sending voice input request...")
            voice_messages = [messages[0]]
            for message in messages[-9:]:
                voice_messages.append(message)

            messages = voice_messages


        payload = {
            "model": "llama3-70b-8192",
            "messages": messages,
            "temperature": 0.7
        }

        logger.info("Sending request...")
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=10)
        if "error" in response.json().keys():
            logger.error("Reached limit of tokens or invalid token.")
            return
        formated_response = response.json()['choices'][0]['message']
        messages.append(formated_response)
        response_content = formated_response['content']

        if is_context_need:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=4)

        with open(os.path.join(self.base_dir, "latest_chat.json"), 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)

        return response_content

    def generate_default_context(self):
        paths = {}
        if os.path.exists(os.path.join(self.base_dir, "saved_paths.json")):
            with open(os.path.join(self.base_dir, "saved_paths.json"), "r") as f:
                try:
                    paths = json.load(f)
                except json.JSONDecodeError:
                    logger.error("Incorrect JSON in the file: saved_paths.json")

        with open(os.path.join(self.base_dir, "base_prompt.txt"), "r", encoding="utf-8") as f:
            context = f.read()

        settings = {}
        if os.path.exists(os.path.join(self.base_dir, "../../gui/setting.json")):
            with open(os.path.join(self.base_dir, "../../gui/setting.json"), "r", encoding="utf-8") as f:
                settings = json.load(f)

        protocols = {}
        if os.path.exists(os.path.join(self.base_dir, "saved_protocols.json")):
            with open(os.path.join(self.base_dir, "saved_protocols.json"), "r", encoding="utf-8") as f:
                protocols = json.load(f)

        context += f"\nHere is the list of available applications: {', '.join(paths.keys()) if paths.keys() else "The list of saved applications is currently empty"}."
        context += f"\nSaved protocols: {protocols if protocols else "the saved minutes are missing."}"
        context += f"\nThe current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC/GMT +2:00."
        context += f"\nKeep in mind that your name is {settings["assistant_name"] if settings else "Альфа"}"

        return context

class JsonHandler:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def add_new_message(self, chat_name, role, message):
        if os.path.exists(os.path.join(self.base_dir, f"chats/{chat_name}")):
            with open(os.path.join(self.base_dir, f"chats/{chat_name}"), "r", encoding="utf-8") as f:
                try:
                    messages = json.load(f)
                except json.JSONDecodeError:
                    logger.warning("History's been corrupted. We're starting over")

            messages.append({"role": role, "content": message})

            with open(os.path.join(self.base_dir, f"chats/{chat_name}"), "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=4)

    def save_protocol(self, protocol_name, protocol_commands):
        protocols = {}
        if os.path.exists(os.path.join(self.base_dir, "saved_protocols.json")):
            with open(os.path.join(self.base_dir, "saved_protocols.json"), "r", encoding="utf-8") as f:
                try:
                    protocols = json.load(f)
                except json.JSONDecodeError:
                    logger.warning("File saved_protocols.json has been corrupted")

        protocols[protocol_name] = protocol_commands

        with open(os.path.join(self.base_dir, "saved_protocols.json"), "w", encoding="utf-8") as f:
            json.dump(protocols, f, ensure_ascii=False, indent=4)


def main_handler(request: str, chat_name: str = "", is_context_need: bool = False, tts_need: bool = False):
    import core.system_interactions as si
    import core.external_interactions as ei

    raw_response = AIModel().request_to_ai(request, is_context_need=is_context_need, chat=chat_name)
    try:
        commands = json.loads(raw_response)

        logger.info("Command execution...")
        response = []

        tts_handler = TTS()
        if tts_need:
            text = ""
            for cmd in commands:
                text += cmd["message"] + " "

            threading.Thread(target=tts_handler.speak, daemon=True, args=(text,)).start()

        for cmd in commands:
            match cmd["command_type"]:
                case "open_app":
                    si.AppManager().open_app(app_name=cmd["content"], is_ai_need=False)
                case "send_message":
                    si.DiscordManager().discord_type_message_in_chat(cmd["content"]["target"], cmd["content"]["message"])
                case "get_time":
                    response.append(cmd["message"])
                case "explain_term":
                    response.append(cmd["message"])
                case "play_pause":
                    pyautogui.press('playpause')
                case "next_track":
                    pyautogui.press('nexttrack')
                case "previous_track":
                    pyautogui.press('prevtrack')
                case "change_volume":
                    si.change_volume(cmd["content"])
                case "delay":
                    time.sleep(cmd["content"])
                case "text":
                    response.append(cmd["message"])
                case "close_app":
                    si.AppManager.close_app(cmd["content"])
                case "error":
                    logger.error(cmd["content"])
                case "minimize_windows":
                    si.HotKeyInteraction.minimize_windows()
                case "alt_tab":
                    si.HotKeyInteraction.alt_tab()
                case "open_settings":
                    si.HotKeyInteraction.open_settings()
                case "open_task_manager":
                    si.HotKeyInteraction.open_task_manager()
                case "open_search":
                    si.HotKeyInteraction.open_search()
                case "close_current_window":
                    si.HotKeyInteraction.close_current_window()
                case "open_url":
                    si.open_url(cmd["content"])
                case "weather":
                    weather = ei.Weather().get_weather(cmd["content"])
                    if weather:
                        weather_message = AIModel().request_to_ai(f"You need to package that data into a nice response for a weather query: {weather}(values are metric), use text command type, in response content is not required, just answer in message parameter. to Determine the language in which to respond, here's a past message from the chat room: {cmd["message"]}", min_context=True)
                        if is_context_need:
                            JsonHandler().add_new_message(chat_name=chat_name, role="assistant", message=weather_message)
                        if tts_need:
                            clear_weather_message = json.loads(weather_message)[0]["message"]
                            threading.Thread(target=tts_handler.speak, daemon=True, args=(clear_weather_message,)).start()
                case "save_protocol":
                    JsonHandler().save_protocol(cmd["protocol_name"], json.loads(cmd["content"]))
                case "get_latest_news":
                    news = ei.get_news()
                    news_message = AIModel().request_to_ai(f"You need to package that data into a nice response for a news query: {news}. Use text command type, in response content is not required, just answer in message parameter. to Determine the language in which to respond, here's a past message from the chat room: {cmd["message"]}", min_context=True)
                    if is_context_need:
                        JsonHandler().add_new_message(chat_name=chat_name, role="assistant", message=news_message)
                    if tts_need:
                        clear_news_message = json.loads(news_message)[0]["message"]
                        threading.Thread(target=tts_handler.speak, daemon=True, args=(clear_news_message,)).start()
                case "search_query":
                    si.open_url(cmd["content"])
                case _:
                    logger.error("Main handler error | Command type not found")

        logger.info("All commands successfully executed")

        if response:
            return response

    except json.JSONDecodeError:
        logger.error("The AI returned invalid JSON")