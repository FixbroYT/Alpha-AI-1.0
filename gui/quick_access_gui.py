import json
import logging
import os
import time
from multiprocessing.context import Process

import flet as ft
import keyboard

from core.web_ai.engine import main_handler
from gui.ui_config import get_theme_colors, get_text_language

logger = logging.getLogger(__name__)

def listen_hotkeys():
    keyboard.add_hotkey('ctrl+alt+q', run_all)
    keyboard.wait("esc")

def main(page: ft.Page):
    page.window.width = 500
    page.window.height = 125
    page.window.resizable = False
    page.title = "Alpha AI - Quick access"
    page.window.icon = os.path.abspath("gui/assets/favicon.ico")
    page.window.center()

    with open("gui/setting.json", "r", encoding="utf-8") as f:
        content = json.load(f)
        current_theme = "dark" if content["dark_theme"] else "light"
        current_language = content["current_language"]

    border_color = get_theme_colors(current_theme)["border"]
    page.theme_mode = current_theme

    def send_handler(e):
        if len(input_field.value) != 0:
            main_handler(request=input_field.value, tts_need=content["tts"])
            input_field.value = ""
            page.window.visible = False
            time.sleep(0.3)
            page.window.destroy()

    input_field = ft.TextField(
        label=get_text_language(current_language)["chat_input"],
        border=ft.InputBorder.NONE,
        on_submit=send_handler
    )

    page.add(
        ft.Container(
            content=ft.Row(
                [
                    input_field,
                    ft.IconButton(
                        ft.Icons.ARROW_FORWARD,
                        on_click=send_handler
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            border=ft.Border(
                ft.BorderSide(2, color=border_color),
                ft.BorderSide(2, color=border_color),
                ft.BorderSide(2, color=border_color),
                ft.BorderSide(2, color=border_color)
            ),
            border_radius=10,
            expand=True,
            padding=5
        )
    )

def run_app():
    logger.info("Opening quick access window")
    ft.app(target=main)

def run_all():
    p = Process(target=run_app)
    p.start()
    p.join()
    logger.info("Quick access process ended")