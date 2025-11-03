# mp4Downloader

Desktop application for Windows, developed in Python, that allows you to safely download videos and audio from platforms like YouTube, X (Twitter), and Instagram without ads.

This application was born as a learning project for a 2nd-year Software Development student (DAM in Spain). The goal was to create a useful tool while reinforcing knowledge in software development, GUIs, and process management.

## ✨ Features

* **Video & Audio Downloads:** Easily download videos in MP4 format or extract audio-only MP3s.
* **Multi-Platform Support:** Works with URLs from YouTube, X (Twitter), Instagram, and hundreds of other sites (thanks to `yt-dlp`).
* **Auto-Updating Engine:** The download engine (`yt-dlp.exe`) updates itself automatically in the background to prevent becoming obsolete.
* **Destination Selector:** Lets you choose any folder to save your files, defaulting to your system's "Downloads" folder.
* **Detailed Progress:** Displays real-time download progress (e.g., `15.2 MB / 78.4 MB`).
* **Authentication Support:** Can use a `cookies_x.txt` file to download content from X (Twitter) that requires a login.
* **Clean Interface:** A simple, responsive GUI built with PyQt6, with no UI freezing thanks to multithreading.
* **Fast Startup:** Built in `onedir` mode for an instant-on application launch.

## 🛠️ Tech Stack

* **Language:** Python 3.13
* **Graphical User Interface (GUI):** PyQt6
* **Download Engine:** `yt-dlp` (using a hybrid engine: the internal library with an external `.exe` fallback)
* **Web Requests:** `requests` (for the auto-updater)
* **Multithreading:** `QThread` (to keep the UI responsive)
* **File/Path Handling:** `pathlib`, `os`
* **Packaging:** `PyInstaller` (in `onedir` mode)

## 📄 License

This project is licensed under the MIT License.
