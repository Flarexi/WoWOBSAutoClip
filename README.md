# 🛡️ WoWOBSAutoClip

**WoWOBSAutoClip** is a lightweight Python automation tool for World of Warcraft players. It monitors combat logs in real-time to control OBS Studio, ensuring you only record boss encounters while automatically adding player death chapters and organized filenames.



---

## ✨ Features
* **Automatic Recording:** Starts recording on `ENCOUNTER_START` and stops on `ENCOUNTER_END`.
* **Smart Naming:** Automatically renames files to `[Timestamp]_[BossName]_[WIN/WIPE].mkv`.
* **Player Death Chapters:** Embeds video chapters at the exact second a player dies (filters for players on `-EU` realms).
* **Lossless Processing:** Uses `mkvmerge` to inject chapters instantly without re-encoding the video.
* **Zero Plugins:** No OBS chapter plugins required; the script handles all logic internally.

---

## 📋 Prerequisites
1.  **[OBS Studio](https://obsproject.com/)**: Must be running with the WebSocket server enabled.
2.  **[MKVToolNix](https://mkvtoolnix.download/)**: Required for the chapter embedding feature.
3.  **Python 3.x**: Ensure Python is added to your system PATH.

---

## ⚙️ Setup & Configuration

### 1. World of Warcraft
You **must** enable Advanced Combat Logging for death detection to work:
* `Esc` -> `Options` -> Search for **Advanced Combat Logging** -> **Enable**.

### 2. OBS WebSocket
* Go to `Tools` -> `WebSocket Server Settings`.
* Click **Enable WebSocket Server**.
* Note your **Server Port** (default 4455) and **Server Password**.

### 3. Script Configuration
Open `WoWOBSAutoClip.py` and update the `Configuration` section at the top:

```python
# --- Configuration ---
OBS_HOST = 'localhost'
OBS_PORT = 4455
OBS_PASSWORD = 'your_obs_password'
WOW_LOG_DIRECTORY = r"C:\Path\To\WoW\_classic_\Logs"
MKVMERGE_CMD = r"C:\Program Files\MKVToolNix\mkvmerge.exe"
