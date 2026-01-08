# ⚔️ WoWOBSAutoClip (Lite Version)
[![Version](https://img.shields.io/github/v/release/Flarexi/WoWOBSAutoClip?filter=*lite*)](https://github.com/Flarexi/WoWOBSAutoClip/releases)

**Automated Combat Recorder for World of Warcraft**

This is the **Lite version** of the script. It is designed to be a "plug-and-play" solution that focuses purely on **starting, stopping, and naming** your recordings based on boss encounters and Mythic+ runs. Unlike the main version, this version does not require external tools like MKVToolNix to function.


### ✨ Features

* **📦 No External Dependencies:** Does not require MKVToolNix; works purely with Python and OBS.
* **🏆 Mythic+ & Raids:** Automatically detects run starts and boss pulls across **Retail**, **Classic**, and **Anniversary** servers.
* **🚀 Auto-Naming:** Instantly renames files using the format: `YYYY-MM-DD_HH-MM-SS_[EventName]_[KILL/WIPE].mkv`.
* **🛡️ Safe Rename Logic:** Includes built-in retry logic to handle Windows file-locking errors during the renaming process.


### 📋 Prerequisites

1.  **OBS Studio (v28+):** [Download here](https://obsproject.com/download).
2.  **Python 3.10+:** [Download here](https://www.python.org/).
3.  **OBS WebSocket:** Ensure "WebSocket Server Settings" is enabled in OBS (Tools -> WebSocket Server Settings).

> [!IMPORTANT]
> You **must** enable **Advanced Combat Logging** in-game for Mythic+ data and Boss names to be captured accurately.
> *Location: Menu -> Options -> Network -> Advanced Combat Logging (Check this box).*

### 🛠️ Setup

1.  **Download** the `WoWOBSAutoClip Lite.py` and `Run_WoWOBSAutoClip Lite.bat` files.
2.  **Configure:** Open `WoWOBSAutoClip Lite.py` in a text editor and fill in your settings:
    * `OBS_PASSWORD`: Your OBS WebSocket password.
    * `WOW_LOG_DIRECTORY`: Path to your WoW Logs folder.
    * `OBS_EXE_PATH`: The full path to your `obs64.exe`.
3.  **Launch:** Double-click `Run_WoWOBSAutoClip Lite.bat`.
    * The batch file will automatically check for Python and install the required `obs-websocket-py` library if it's missing.


### 🖥️ Console Preview
````
 --------------------------------------------------
        W o W   O B S   A u t o C l i p
   [ Raids  -  Mythic+  -  Retail  -  Classic  ]
 --------------------------------------------------

[SUCCESS] Monitoring WoW Logs...
>> OBS CONNECTED successfully.
>> MONITORING: WoWCombatLog.txt (Retail)
>> MONITORING ACTIVE <<

!!! RECORDING STARTED: The Prophet Skitra
>> Waiting 5s to finalize log data...
>> FINALIZED: 2026-01-08_20-15-05_The_Prophet_Skitra_KILL.mkv
````
