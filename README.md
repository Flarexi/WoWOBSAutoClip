# WoW Raid Recorder (OBS Auto-Record & Chaptering)

An automated tool for World of Warcraft that uses combat logs to trigger OBS recordings of boss encounters. It automatically names files by boss/result and embeds player deaths as video chapters.

## ✨ Features
- 🚀 **Auto-Start/Stop:** Records only when the boss pull starts.
- 💀 **Death Tracking:** Automatically adds chapter markers when players die.
- 🏷️ **Smart Naming:** Files are saved as `[Timestamp]_[BossName]_[WIN/WIPE].mkv`.
- 🛠️ **No OBS Plugins:** Entirely self-contained using Python and MKVToolNix.

## 📋 Prerequisites
1. [OBS Studio](https://obsproject.com/)
2. [MKVToolNix](https://mkvtoolnix.download/) (Must be installed for chapter embedding).
3. Python 3.x

## ⚙️ Setup
1. Enable **WebSocket Server** in OBS (Tools -> WebSocket Server Settings).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

   Update the Configuration section in WoWOBSAutoClip.py with your OBS password and WoW log path.

🚀 Usage

Run the script before your raid:
Bash

python WoWOBSAutoClip.py