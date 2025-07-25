import json
import logging
import os
import re
import subprocess

import flet as ft

from core.web_ai.engine import main_handler
from gui.ui_config import get_theme_colors, get_text_language
from gui.tray import update_menu_label
from gui.tray import update_flet_page

flet_page = None
logger = logging.getLogger(__name__)

def flet_main(page: ft.Page):
    from gui import app_state
    global flet_page

    flet_page = page
    update_flet_page(page)

    page.window.min_width = 700
    page.window.min_height = 400
    page.title = "Alpha AI"
    page.window.icon = os.path.abspath("gui/assets/favicon.ico")
    page.window.center()

    page.fonts = {
        "Oxanium": "gui/assets/fonts/Oxanium-VariableFont_wght.ttf"
    }

    def create_new_chat(raw_chat_name):
        chat_name = re.sub(r" ", "_", raw_chat_name.lower())
        if f"{chat_name}.json" not in get_chat_list():
            open(f"{app_state.chats_dir}/{chat_name}.json", "w", encoding="utf-8").close()

    def set_default_settings():
        with open("gui/setting.json", "w", encoding="utf-8") as f:
            base_settings = {
                "dark_theme": True,
                "current_language": "english",
                "voice_input": False,
                "tts": False,
                "assistant_name": "Альфа"
            }
            json.dump(base_settings, f, ensure_ascii=False, indent=4)

    def make_border():
        border_color = get_theme_colors(page.theme_mode)["border"]

        return ft.Border(
            ft.BorderSide(2, color=border_color),
            ft.BorderSide(2, color=border_color),
            ft.BorderSide(2, color=border_color),
            ft.BorderSide(2, color=border_color)
        )


    def send_button_handler(e):
        if len(chat_input.value) != 0 and app_state.current_chat:
            with open("gui/setting.json", encoding="utf-8") as f:
                setting = json.load(f)

            main_handler(chat_input.value, chat_name=app_state.current_chat, is_context_need=True, tts_need=setting["tts"])
            chat_input.value = ""
            update_messages()
            page.update()

    def update_chat_list():
        displayed_chats_box.controls.clear()
        displayed_chats_box.controls = generate_chat_list()
        app_state.chats = get_chat_list()
        page.update()

    def new_chat_button_handler(e):
        if len(new_chat_input.value) != 0 and len(new_chat_input.value) < 30:
            create_new_chat(new_chat_input.value)
            update_chat_list()
            new_chat_input.value = ""
            page.update()

    def handle_home_button(e):
        app_state.current_page = "main"
        page.controls.clear()
        page.add(
            header,
            main_container if app_state.current_page == "main" else settings_page
        )

    def handle_settings_button(e):
        app_state.current_page = "settings"
        page.controls.clear()
        page.add(
            header,
            main_container if app_state.current_page == "main" else settings_page
        )

    def change_current_chat(e: ft.ControlEvent):
        for chat in app_state.chats:
            if re.sub(r" ", "_", e.control.text.lower()) in chat:
                app_state.current_chat = chat
                update_messages()
                page.update()

    def generate_chat_list():
        chats_path = app_state.chats_dir
        chat_paths = os.listdir(chats_path)
        response = []
        for chat_path in chat_paths:
            if chat_path != "voice_input_chat.json":
                chat_name = re.sub(r"\.json$", "", chat_path).replace("_", " ").strip().capitalize()
                response.append(ft.ElevatedButton(
                    chat_name,
                    width=364,
                    height=40,
                    color=get_theme_colors(page.theme_mode)["text"],
                    on_click=change_current_chat,
                ))

        return response

    def generate_messages(chat_name):
        messages = []
        chat_file_path = f"{app_state.chats_dir}/{chat_name}"
        if not os.path.exists(chat_file_path):
            return []
        with open(chat_file_path, "r", encoding="utf-8") as f:
            try:
                content = json.load(f)

                for message in content:
                    if message["role"] != "system":
                        if message["role"] == "user":
                            messages.append(ft.Container(
                                content=ft.Container(
                                    content=ft.Text(message["content"], no_wrap=False),
                                    padding=10,
                                    bgcolor=get_theme_colors(page.theme_mode)["background"],
                                    border_radius=10,
                                    width=375
                                ),
                                alignment=ft.alignment.center_right
                            ))
                        else:
                            for cmd in json.loads(message["content"]):
                                messages.append(ft.Container(
                                    content=ft.Container(
                                        content=ft.Text(cmd["message"], no_wrap=False),
                                        padding=10,
                                        bgcolor=get_theme_colors(page.theme_mode)["background"],
                                        border_radius=10,
                                        width=375
                                    ),
                                    alignment=ft.alignment.center_left
                                ))

            except json.JSONDecodeError:
                logger.error("Incorrect JSON in the file: " + f"{app_state.chats_dir}/{chat_name}")
                return

        return messages

    def update_messages():
        if app_state.current_chat:
            messages_box.controls.clear()
            messages_box.controls = generate_messages(app_state.current_chat)
            chat_box.content.controls[0].content = messages_box
        else:
            messages_box.controls.clear()
            chat_box.content.controls[0].content = messages_box

    def handle_theme_switch(e):
        if os.path.exists("gui/setting.json"):
            try:
                with open("gui/setting.json", "r", encoding="utf-8") as f:
                    content = json.load(f)

                content["dark_theme"] = theme_switch.value

                with open("gui/setting.json", "w", encoding="utf-8") as f:
                    json.dump(content, f, ensure_ascii=False, indent=4)

                settings_setup()
            except json.JSONDecodeError:
                return

    def update_elements_theme():
        settings_page.border = make_border()
        chat_box.border = make_border()
        chat_box.content.controls[1].border = make_border()
        chat_list.border = make_border()
        new_chat.border = make_border()
        displayed_chats_box.controls = generate_chat_list()
        if app_state.current_chat:
            messages_box.controls = generate_messages(app_state.current_chat)

    def update_language_elements():
        theme_switch.label = get_text_language(app_state.current_language)["theme_switch"]
        chat_input.label = get_text_language(app_state.current_language)["chat_input"]
        new_chat_input.label = get_text_language(app_state.current_language)["new_chat_input"]
        delete_current_chat_button.text = get_text_language(app_state.current_language)["delete_chat_button"]
        open_log_file_button.text = get_text_language(app_state.current_language)["tray_log_button"]
        voice_input_switch.label = get_text_language(app_state.current_language)["voice_input_switch"]
        tts_switch.label = get_text_language(app_state.current_language)["tts_switch"]
        assistant_name.label = get_text_language(app_state.current_language)["assistant_name"]
        page.update()
        update_menu_label()

    def settings_setup():
        try:
            if os.path.exists("gui/setting.json"):
                with open("gui/setting.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    if settings["dark_theme"]:
                        page.theme_mode = "dark"
                        theme_switch.value = True
                    else:
                        page.theme_mode = "light"
                        theme_switch.value = False
                    update_elements_theme()
                    app_state.current_language = settings["current_language"]
                    voice_input_switch.value = settings["voice_input"]
                    tts_switch.value = settings["tts"]
                    assistant_name.value = settings["assistant_name"]
                    update_language_elements()
                    page.update()
            else:
                set_default_settings()
                settings_setup()
        except json.JSONDecodeError:
            set_default_settings()
            settings_setup()

    def change_language(e):
        app_state.current_language = language_dropdown.value
        update_language_elements()
        if os.path.exists("gui/setting.json"):
            try:
                with open("gui/setting.json", "r", encoding="utf-8") as f:
                    content = json.load(f)

                content["current_language"] = language_dropdown.value

                with open("gui/setting.json", "w", encoding="utf-8") as f:
                    json.dump(content, f, ensure_ascii=False, indent=4)
            except json.JSONDecodeError:
                return

    def delete_current_chat(e):
        if app_state.current_chat:
            os.remove(f"{app_state.chats_dir}/{app_state.current_chat}")

        logger.info(f"{app_state.current_chat} is successfully deleted")

        update_chat_list()
        app_state.current_chat = get_chat_list()[0] if get_chat_list() else None
        update_messages()

    def open_log_file(e):
        log_file_path = os.path.abspath("logs/latest.log")
        logger.info(f"Opening log file at {log_file_path}")
        subprocess.run(["notepad", log_file_path])

    def handle_voice_input_switch(e):
        if os.path.exists("gui/setting.json"):
            try:
                with open("gui/setting.json", "r", encoding="utf-8") as f:
                    content = json.load(f)

                content["voice_input"] = voice_input_switch.value

                with open("gui/setting.json", "w", encoding="utf-8") as f:
                    json.dump(content, f, ensure_ascii=False, indent=4)
            except json.JSONDecodeError:
                return

    def handle_tts(e):
        if os.path.exists("gui/setting.json"):
            try:
                with open("gui/setting.json", "r", encoding="utf-8") as f:
                    content = json.load(f)

                content["tts"] = tts_switch.value

                with open("gui/setting.json", "w", encoding="utf-8") as f:
                    json.dump(content, f, ensure_ascii=False, indent=4)
            except json.JSONDecodeError:
                return

    def handle_assistant_name_change(e):
        if os.path.exists("gui/setting.json"):
            try:
                with open("gui/setting.json", "r", encoding="utf-8") as f:
                    content = json.load(f)

                content["assistant_name"] = assistant_name.value

                with open("gui/setting.json", "w", encoding="utf-8") as f:
                    json.dump(content, f, ensure_ascii=False, indent=4)
            except json.JSONDecodeError:
                return

    theme_switch = ft.Switch(
        label=get_text_language(app_state.current_language)["theme_switch"],
        on_change=handle_theme_switch,
    )

    language_dropdown = ft.Dropdown(
        editable=True,
        label="Language",
        options=[
            ft.DropdownOption(key="english", content=ft.Text("English")),
            ft.DropdownOption(key="russian", content=ft.Text("Russian"))
        ],
        on_change=change_language,
        width=150,
        enable_filter=True,
        border=ft.InputBorder.NONE
    )

    delete_current_chat_button = ft.ElevatedButton(
        get_text_language(app_state.current_language)["delete_chat_button"],
        icon=ft.Icons.DELETE,
        width=150,
        on_click=delete_current_chat,
        color="red"
    )

    open_log_file_button = ft.ElevatedButton(
        get_text_language(app_state.current_language)["tray_log_button"],
        icon=ft.Icons.ARTICLE,
        width=150,
        on_click=open_log_file
    )

    voice_input_switch = ft.Switch(
        label=get_text_language(app_state.current_language)["voice_input_switch"],
        on_change=handle_voice_input_switch
    )

    tts_switch = ft.Switch(
        label=get_text_language(app_state.current_language)["tts_switch"],
        on_change=handle_tts
    )

    assistant_name = ft.TextField(
        label=get_text_language(app_state.current_language)["assistant_name"],
        on_submit=handle_assistant_name_change
    )

    settings_page = ft.Container(
        content=ft.Row([
            ft.Column(
                [
                    theme_switch,
                    language_dropdown,
                    open_log_file_button,
                    delete_current_chat_button
                ],
                spacing=20
            ),
            ft.Column(
                [
                    voice_input_switch,
                    tts_switch,
                    assistant_name
                ],
                spacing=20
            )
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
        expand=True,
        border=make_border(),
        border_radius=10,
        padding=20
    )

    messages_box = ft.Column(generate_messages(app_state.current_chat),
         scroll=ft.ScrollMode.ALWAYS,
         spacing=10,
         auto_scroll=True
         )

    chat_input = ft.TextField(
        label=get_text_language(app_state.current_language)["chat_input"],
        border=ft.InputBorder.NONE,
        expand=True,
        on_submit=send_button_handler
    )

    chat_box = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=messages_box if app_state.current_chat else "",
                    expand=True,
                    alignment=ft.alignment.bottom_center
                ) if app_state.current_chat else ft.Container(),
                ft.Container(
                    content=ft.Row(
                        [
                            chat_input,
                            ft.IconButton(ft.Icons.ARROW_FORWARD, on_click=send_button_handler)
                        ],
                        expand=True
                    ),
                    border_radius=10,
                    border=make_border(),
                    padding=5
                ),
            ],
            alignment=ft.MainAxisAlignment.END
        ),
        expand=True,
        padding=20,
        border=make_border(),
        border_radius=10
    )

    new_chat_input = ft.TextField(
        label=get_text_language(app_state.current_language)["new_chat_input"],
        border=ft.InputBorder.NONE,
        on_submit=new_chat_button_handler
    )

    header = ft.Row(
        [
            ft.Row(
                [
                    ft.Text("Alpha", size=36, font_family="Oxanium"),
                    ft.Text("AI", size=36, color="#1FA4F6", font_family="Oxanium")
                ]
            ),
            ft.Row([
                ft.IconButton(icon=ft.Icons.HOME, on_click=handle_home_button),
                ft.IconButton(icon=ft.Icons.SETTINGS, on_click=handle_settings_button)
            ])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )

    new_chat = ft.Container(
        content=ft.Row(
            [
                new_chat_input,
                ft.IconButton(ft.Icons.ADD, on_click=new_chat_button_handler)
            ],
            width=350
        ),
        border_radius=10,
        border=make_border(),
        padding=5
    )

    displayed_chats_box = ft.Column(
        controls=generate_chat_list(),
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        tight=False,
        expand=True
    )

    chat_list = ft.Container(
        content=ft.Column(
            [
                displayed_chats_box,
                new_chat
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=20,
        border=make_border(),
        border_radius=10
    )

    main_container = ft.Container(
        content=ft.Row([
            chat_list,
            chat_box
        ]),
        expand=True
    )

    settings_setup()

    page.add(
        header,
        main_container if app_state.current_page == "main" else settings_page
    )

def get_chat_list():
    from gui import app_state
    chats_path = app_state.chats_dir
    chat_paths = os.listdir(chats_path)
    chats = []
    for chat_path in chat_paths:
        if chat_path != "voice_input_chat.json":
            chats.append(chat_path)
    return chats

def run_all():
    ft.app(target=flet_main)