import logging
import os
import subprocess
import time

from pystray import Icon, Menu, MenuItem
from PIL import Image

from gui.quick_access_gui import run_all
from gui.ui_config import get_text_language

is_interface_open = True
icon = None
flet_page = None

logger = logging.getLogger(__name__)

def open_log_file():
    log_file_path = os.path.abspath("logs/latest.log")
    logger.info(f"Opening log file at {log_file_path}")
    subprocess.run(["notepad", log_file_path])

def update_flet_page(page):
    global flet_page
    flet_page = page

def toggle_interface():
    global is_interface_open, flet_page
    is_interface_open = not is_interface_open
    if flet_page:
        flet_page.window.visible = is_interface_open
    update_menu_label()
    flet_page.update()

def terminate_app():
    if flet_page:
        flet_page.window.visible = False
        time.sleep(0.3)
        flet_page.window.destroy()

def quit_app():
    icon.stop()
    terminate_app()

def update_menu_label():
    from gui.app_state import current_language
    global icon, is_interface_open
    label = get_text_language(current_language)["tray_hide_button"] if is_interface_open else get_text_language(current_language)["tray_open_button"]
    icon.menu = Menu(
        MenuItem(label, toggle_interface),
        MenuItem(get_text_language(current_language)["tray_log_button"], open_log_file),
        MenuItem(get_text_language(current_language)["tray_fast_access"], run_all),
        MenuItem(get_text_language(current_language)["tray_exit_button"], quit_app)
    )
    icon.update_menu()

def run_tray():
    from gui.app_state import current_language
    global icon
    icon = Icon("Alpha AI", Image.open("gui/assets/favicon.png"), menu=Menu(
        MenuItem(get_text_language(current_language)["tray_hide_button"], toggle_interface),
        MenuItem(get_text_language(current_language)["tray_log_button"], open_log_file),
        MenuItem(get_text_language(current_language)["tray_fast_access"], run_all),
        MenuItem(get_text_language(current_language)["tray_exit_button"], quit_app)
    ))
    icon.run()