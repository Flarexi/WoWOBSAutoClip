# 🛡️ WoWOBSAutoClip

**WoWOBSAutoClip** is a lightweight Python automation tool for World of Warcraft. It monitors combat logs in real-time to control OBS Studio, ensuring you only record boss encounters while automatically adding player death chapters and organized filenames.



---

## ✨ Features
* **🚀 Auto-Launch:** Automatically starts OBS Studio if it isn't running.
* **⏺️ Auto-Recording:** Starts on `ENCOUNTER_START` and stops on `ENCOUNTER_END`.
* **🏷️ Smart Naming:** Saves files as `[Timestamp]_[BossName]_[KILL/WIPE].mkv`.
* **💀 Death Chapters:** Embeds markers at the exact second players die (filters for `-EU` realms).
* **⚡ Lossless Muxing:** Uses `mkvmerge` to inject chapters without re-encoding.
* **🔒 File Safety:** Built-in retry logic to prevent "File in Use" errors during renaming.

---

## 📋 Prerequisites
1. **[OBS Studio](https://obsproject.com/)**: Must have WebSocket enabled (Tools -> WebSocket Server Settings).
2. **[MKVToolNix](https://mkvtoolnix.download/)**: Required for chapter embedding.
3. **Python 3.x**: Added to Windows PATH.

---

## ⚙️ Setup
1. **Enable Advanced Combat Logging** in WoW (Options -> Network).
2. **Configure `WoWOBSAutoClip.py`**: Open the script and update your OBS password and file paths.

## 🚀 Usage
Simply double-click `Run_WoWOBSAutoClip.bat`. The script will launch OBS, connect, and begin monitoring your latest WoW log automatically.

---