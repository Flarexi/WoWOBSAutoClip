# ⚔️ WoWOBSAutoClip
![Version](https://img.shields.io/github/v/release/Flarexi/WoWOBSAutoClip)

**Automated Combat Recorder for World of Warcraft**

This version of the script focuses purely on **starting and stopping** your recordings based on boss encounters and Mythic+ runs. It does not require external tools like MKVToolNix.

## ✨ Features

* **📦 Universal Support:** Works with **Retail**, **Classic (Cata/MoP)**, **TBC Anniversary**, and **Classic Era**.
* **🏆 Mythic+:** Detects run start, extracts the **Key Level** for the filename, and records the entire run as one file.
* **🚀 Auto-Naming:** Files are saved with timestamps, boss names, key levels, and result (**KILL/WIPE**).

## 📋 Prerequisites
1. **OBS Studio** (v28+).
2. **Python 3.10+**.
*Note: MKVToolNix is NOT required for this version.*

> [!IMPORTANT]
> You **must** enable **Advanced Combat Logging** in-game for Mythic+ data and Boss names to be captured accurately.
> *Location: Menu -> Options -> Network -> Advanced Combat Logging (Check this box).*

## 🛠️ Setup

1.  **Download** this repository and extract it to a folder.
2.  **Configure the Script:** Open `WoWOBSAutoClip.py` in a text editor and update the entire `--- 1. Configuration ---` section:
    * `OBS_PASSWORD`: Your OBS WebSocket password.
    * `WOW_LOG_DIRECTORY`: Path to your WoW Logs folder (e.g., `_retail_\Logs`).
    * `STOP_DELAY_SECONDS`: How long to keep recording after a boss dies (default: 5).
    * `MKVMERGE_CMD`: The full path to your `mkvmerge.exe`.
    * `OBS_EXE_PATH`: The full path to your `obs64.exe`.
3.  **Run the Recorder:** Simply double-click `Run_WoWOBSAutoClip.bat`. It will automatically install the required libraries on the first run.

## 🎮 Supported Content

| Content Type | Start Trigger | End Trigger | Markers |
| :--- | :--- | :--- | :--- |
| **Raid Bosses** | Encounter Start | Encounter End | Deaths |
| **Mythic+** | Key Inserted | Dungeon End | Bosses & Deaths |
| **Anniversary** | Encounter Start | Encounter End | Deaths |

### 🖥️ Console Preview
````
 --------------------------------------------------
        W o W   O B S   A u t o C l i p
   [ Raids  -  Mythic+  -  Retail  -  Classic  ]
 --------------------------------------------------

[SUCCESS] Monitoring WoW Logs...
(Keep this window open while playing!)

>> OBS CONNECTED successfully.
>> FULL LOG PATH: P:\World of Warcraft\_retail_\Logs\WoWCombatLog.txt
>> MONITORING ACTIVE <<

!!! RECORDING STARTED: M+ The Necrotic Wake (+15)
>> Waiting 5s to finalize log data...
!!! RECORDING STOPPED
>> FINALIZED: 2026-01-04 18-30-05_MPlus_The_Necrotic_Wake_plus15_KILL.mkv
````
## ⚖️ License
This project is open-source and free to use for the WoW community.
