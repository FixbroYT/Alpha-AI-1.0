# Alpha AI 1.0

Alpha AI is a **desktop voice assistant** for Windows.  
It helps with daily tasks like opening applications, sending messages, managing music, and searching online — all through **voice or text commands**.

---

## ⚙️ Features

- 🎙️ **Voice input** — use your microphone to issue commands *(Russian only)*.
- 🗣️ **Voice responses** — assistant speaks back to you *(Russian only)*.
- 🖥️ Open, close, and manage desktop applications.
- 🌐 Perform Google web searches.
- 🌤️ Check real-time weather.
- 📰 Read the latest news (from Google News).
- 🔊 Media controls — play, pause, next, previous, volume control.
- 🔐 No cloud dependency for speech — supports offline voice recognition.
- 📄 Customizable protocols — save command sequences and replay them.

---

## 🚨 Requirements

- Python 3.10+
- Windows OS
- Microphone & Speakers (for voice interaction)

---

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/FixbroYT/Alpha-AI-1.0.git
   cd Alpha-AI-1.0

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your API keys:

   ```
   GROQ_API_KEY=your_groq_key_here
   OPENWEATHER_API_KEY=your_openweather_key_here
   ```

---

## 🚀 Usage

Run the application:

```bash
python main.py
```

* Use **tray icon** to open settings or interface.
* Speak commands starting with **wake word**, e.g., “Джарвис открой Дискорд”.
* Or use the **text input** interface to interact manually.

---

## 📌 Limitations

* **Voice input and speech output are available only in Russian**.
* Some features use online APIs (optional).
* Windows-only application.

---

## 🛠 Tech Stack

* Python + Flet (GUI)
* Vosk (offline speech recognition)
* Silero TTS (offline text-to-speech)
* Groq / OpenAI API (for AI processing)
* Logging system with rotation for debug/info/error output

---

## 📂 Project Structure (key folders)

```
Alpha-AI-1.0/
│
├── core/              # Core AI logic, speech, commands
├── gui/               # Interface, tray, settings
├── logs/              # Auto-generated logs
├── .env               # API keys
└── main.py            # Main launcher
```

---

## 📄 License

MIT License — free to use and modify.