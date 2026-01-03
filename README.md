# ⚔️ WoWOBSAutoClip
![Version](https://img.shields.io/github/v/release/Flarexi/WoWOBSAutoClip)

**Automated Combat Recorder for World of Warcraft**

WoWOBSAutoClip is a lightweight Python utility that monitors your World of Warcraft combat log and automatically triggers OBS Studio to record your boss encounters and Mythic+ runs. It handles the "boring" parts—starting, stopping, and naming files—so you can focus on the game and analyze later.



## ✨ Features

* **📦 Universal Support:** Works with **Retail**, **Classic (Cata/MoP)**, **TBC Anniversary**, and **Classic Era**.
* **🏆 Mythic+:** Detects run start, extracts the **Key Level** for the filename, and records the entire run as one file.
* **📍 Smart Chapters:** Automatically adds MKV chapter markers for Boss Pulls (inside M+), Boss Defeated/Wipes, and Player Deaths.
* **🌍 Region Agnostic:** Handles player names and realms globally (US, EU, KR, TW, OCE).
* **🚀 Auto-Naming:** Files are saved with timestamps, boss names, key levels, and result (KILL/WIPE/SUCCESS).

## 📋 Prerequisites

1.  **OBS Studio:** [Download here](https://obsproject.com/download).
2.  **OBS WebSocket:** Ensure "WebSocket Server Settings" is enabled in OBS (Tools menu).
3.  **MKVToolNix:** Required for injecting chapters. [Download here](https://mkvtoolnix.download/).
4.  **Python 3.x:** [Download here](https://www.python.org/).

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
3.  **Run the Recorder:** * Simply double-click `Run_WoWOBSAutoClip.bat`. It will automatically install the required libraries on the first run.

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

>> OBS is already running.
>> OBS CONNECTED.
>> MONITORING ACTIVE [RETAIL]
>> LOG FILE: WoWCombatLog-010326_1430.txt

!!! RECORDING STARTED: M+ The Necrotic Wake (+15)
>> BOSS START: Blightbone
>> PLAYER DEATH: Healername-Illidan-US
>> BOSS DEFEATED: Blightbone
>> Finalizing data in 5s...
!!! RECORDING STOPPED
>> FINALIZED: 2026-01-03 14-30-05_MPlus_The_Necrotic_Wake_plus15_SUCCESS.mkv
````
## ⚖️ License
This project is open-source and free to use for the WoW community.
