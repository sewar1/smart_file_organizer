# 📁 File Organizer (Python Automation Tool)

A real-time file organization tool that automatically sorts files in your Downloads folder into categorized directories.

---

## 🚀 Features

- Real-time file monitoring
- Automatic file categorization
- Handles existing files (initial cleanup)
- Prevents incomplete downloads
- Configurable via JSON file
- Logging system for tracking actions

---

## 🧠 How It Works

- Watches your Downloads folder using `watchdog`
- Detects new or modified files
- Waits until file download is complete
- Moves file to correct category folder

---

## 📂 Categories

- Images
- Videos
- Audio
- Documents
- Archives
- Executables
- Code
- Others

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
