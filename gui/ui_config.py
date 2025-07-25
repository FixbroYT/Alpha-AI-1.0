def get_theme_colors(theme_mode):
    return {
        "background": "#191c21" if theme_mode == "dark" else "#f2f2fa",
        "text": "#ffffff" if theme_mode == "dark" else "#000000",
        "border": "#1b1d1f" if theme_mode == "dark" else "#f2f2fa"
    }

def get_text_language(current_language):
    return {
        "theme_switch": "Тёмная тема" if current_language == "russian" else "Dark theme",
        "chat_input": "Введите ваш запрос" if current_language == "russian" else "Enter your request",
        "new_chat_input": "Введите название для нового чата" if current_language == "russian" else "Enter a name for the new chat room",
        "delete_chat_button": "Удалить текущий чат" if current_language == "russian" else "Delete current chat",
        "tray_hide_button": "Скрыть интерфейс" if current_language == "russian" else "Hide interface",
        "tray_open_button": "Открыть интерфейс" if current_language == "russian" else "Open the interface",
        "tray_exit_button": "Выход" if current_language == "russian" else "Exit",
        "tray_log_button": "Открыть лог" if current_language == "russian" else "Open log file",
        "tray_fast_access": "Открыть быстрый доступ" if current_language == "russian" else "Open quick access",
        "voice_input_switch": "Включить голосовой ввод" if current_language == "russian" else "Enable voice input",
        "tts_switch": "Включить озвучку" if current_language == "russian" else "Turn on the voiceover",
        "assistant_name": "Имя ассистента" if current_language == "russian" else "Assistant name"
    }