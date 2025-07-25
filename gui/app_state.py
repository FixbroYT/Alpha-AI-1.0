from gui.main_gui import get_chat_list

chats_dir = "core/web_ai/chats"

current_language = "english"
chats = get_chat_list()

if chats:
    current_chat = chats[0]
else:
    current_chat = None
current_page = "main"