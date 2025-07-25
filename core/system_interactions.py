import ctypes
import json
import logging
import os
import time
import webbrowser

import psutil
from pywinauto import Application, keyboard
from pywinauto.keyboard import send_keys
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import subprocess
from multiprocessing import Process, Queue
import keyboard as kb

from config import API_KEY_AI

logger = logging.getLogger(__name__)

class AppManager:
    def __init__(self):
        self.base_dir = os.path.normpath(f"{os.path.dirname(os.path.abspath(__file__))}\\web_ai")
        self.api_key = API_KEY_AI

    @staticmethod
    def app_exists(app_name: str) -> bool:
        result = subprocess.run(f"where {app_name}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0

    @staticmethod
    def is_process_running(process_name):
        for _ in range(10):
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() in process_name.lower():
                        logger.info(f"Process found: {proc.info['name']} (PID: {proc.info['pid']})")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            time.sleep(1)
        logger.warning(f"Process {process_name} not found")
        return False

    @staticmethod
    def close_app(exe_name):
        logger.info(f"Killing process {exe_name}...")
        os.system(f"taskkill /f /im {exe_name}.exe")

    def open_app(self, app_name: str, is_ai_need: bool):
        from core.web_ai.engine import AIModel

        if is_ai_need:
            ai_model = AIModel()
            ai_response = ai_model.request_to_ai(app_name)
        else:
            ai_response = app_name

        if self.app_exists(ai_response):
            logger.info(f"Opening app {ai_response}...")
            subprocess.run(f"start {ai_response}", shell=True)
        else:
            saved_paths_path = os.path.join(self.base_dir, "saved_paths.json")

            if os.path.exists(saved_paths_path):
                with open(saved_paths_path, "r", encoding="utf-8") as f:
                    if os.path.getsize(saved_paths_path) > 0:
                        content = json.load(f)
                        if ai_response.lower() in content and os.path.isfile(content[ai_response.lower()]):
                            logger.info(f"Opening app {content[ai_response.lower()]}")
                            subprocess.Popen([f"{content[ai_response.lower()]}"])
                            self.is_process_running(content[ai_response.lower()])
                            return

            logger.info("Application path not found, please select the file you want to open with this key")
            handler = NewPathHandler()
            path = handler.choose_executable_multiprocess()
            if path:
                handler.save_new_path(ai_response.lower(), path)
                logger.info(f"Opening app by abs path {path}")
                subprocess.run(f'start "" "{path}"', shell=True)

class NewPathHandler:
    def __init__(self):
        self.base_dir = os.path.normpath(f"{os.path.dirname(os.path.abspath(__file__))}\\web_ai")

    @staticmethod
    def tk_dialog(result_queue):
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Choose .exe",
            filetypes=[("Executable files", "*.exe")]
        )
        result_queue.put(file_path or "")
        root.destroy()

    def choose_executable_multiprocess(self):
        result_queue = Queue()
        p = Process(target=self.tk_dialog, args=(result_queue,))
        p.start()
        p.join()
        return result_queue.get() if not result_queue.empty() else None

    def save_new_path(self, app_name, path):
        logger.info(f"Saving new path for {app_name}...")

        content = {}

        if os.path.exists(os.path.join(self.base_dir, "saved_paths.json")):
            with open(os.path.join(self.base_dir, "saved_paths.json"), "r") as f:
                try:
                    content = json.load(f)
                except FileNotFoundError:
                    logger.error("Save new path error | File not found: saved_paths.json")
                    return
                except json.JSONDecodeError:
                    logger.error("Save new path error | Incorrect JSON in the file: saved_paths.json")
                    return

        content[app_name] = path

        with open(os.path.join(self.base_dir, "saved_paths.json"), "w") as f:
            json.dump(content, f, ensure_ascii=False, indent=4)

class DiscordManager:
    @staticmethod
    def discord_type_message(message: str) -> None:
        app = Application(backend="uia").connect(title_re=".*Discord.*")
        win = app.window(title_re=".*Discord.*")
        win.set_focus()
        edit_controls = win.descendants(control_type="Edit")
        if len(edit_controls) == 1:
            edit_controls[0].set_focus()
            send_keys(message + "{ENTER}", with_newlines=True, with_spaces=True)
        elif len(edit_controls) == 2:
            edit_controls[1].set_focus()
            send_keys(message + "{ENTER}", with_newlines=True, with_spaces=True)
        else:
            logger.error("Discord type message error | Error in input field search")

    @staticmethod
    def discord_find_chat(chat_name: str) -> True:
        try:
            app = Application(backend="uia").connect(title_re=".*Discord.*")
            win = app.window(title_re=".*Discord.*")
            win.set_focus()
            switch_to_english()

            home_page = win.descendants(control_type="TreeItem")[0]
            if home_page:
                home_page.click_input()
                home_page.click_input()

            keyboard.send_keys('^k')

            search_fields = win.descendants(control_type="ComboBox")
            if len(search_fields) == 1:
                search_field = search_fields[0]
            elif len(search_fields) == 2:
                search_field = search_fields[1]
            else:
                logger.error("Discord find chat error | Unable to find the search input field")
                return

            if search_field:
                search_field.set_focus()
                send_keys(chat_name, with_spaces=True)
            else:
                logger.error("Discord find chat error | Error when entering a chat name")
                home_page.click_input()
                return

            for button in win.descendants(control_type="ListItem"):
                if chat_name.lower() in str(button).lower():
                    button.click_input()
                    return True

            home_page.click_input()
            logger.error("Discord find chat error | Couldn't find the chat room")
        except Exception as e:
            logger.error(f"Discord find chat error | {e}")

    @staticmethod
    def discord_get_all_chats():
        app = Application(backend="uia").connect(title_re=".*Discord.*")
        win = app.window(title_re=".*Discord.*")
        win.set_focus()

        chat_list = win.descendants(control_type="Hyperlink")
        if chat_list:
            chat_names = []
            for chat in chat_list:
                chat_names.append(chat.window_text())

            return chat_names

    @staticmethod
    def generate_chat_selection_prompt(available_chats, query_chat_name):
        prompt = " ".join([
            "The user has a list of available chat rooms:",
            str(available_chats),

            f"The user said in voice or text: '{query_chat_name}'",

            "You need to select from the available chat rooms the one that best matches the user's request."
            "Important:",
            "- Titles can be in different languages.",
            "- Titles may be incomplete or misspoken.",
            "- The request can be said in Russian, and the chat name in English (or vice versa).",

            "Print only one most appropriate chat name from the list. Don't explain anything, just output the string, without values in brackets.",
            "If nothing fits, answer ‘Error’ and hyphenate the error itself."
        ])

        return prompt

    def discord_type_message_in_chat(self, chat_name: str, message: str):
        from core.web_ai.engine import AIModel
        if self.discord_find_chat(chat_name):
            self.discord_type_message(message)
        else:
            logger.info("Discord type_message in chat | Primary search failed, query to AI")
            prompt = self.generate_chat_selection_prompt(self.discord_get_all_chats(), chat_name)

            response = AIModel().request_to_ai(prompt)
            if self.discord_find_chat(response):
                time.sleep(0.3)
                self.discord_type_message(message)
                logger.info(f"Discord type_message in chat | The message was successfully written to the chat room {response}")
                return

class HotKeyInteraction:
    @staticmethod
    def minimize_windows():
        kb.send("win+d")

    @staticmethod
    def alt_tab():
        kb.send("alt+tab")

    @staticmethod
    def open_settings():
        kb.send("win+i")

    @staticmethod
    def open_task_manager():
        kb.send("ctrl+shift+esc")

    @staticmethod
    def open_search():
        kb.send("win+s")

    @staticmethod
    def close_current_window():
        kb.send("alt+f4")

def switch_to_english():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, 0)

    layout = ctypes.windll.user32.LoadKeyboardLayoutW("00000409", 1)

    ctypes.windll.user32.PostMessageW(hwnd, 0x50, 0, layout)
    logger.info("Keyboard language switched to english")

def change_volume(volume_percentage: int):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    volume.SetMasterVolumeLevelScalar(volume_percentage / 100, None)
    logger.info(f"Volume set to {volume_percentage}%")

def open_url(url):
    webbrowser.open_new_tab(url)