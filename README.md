# 🛡️ WoWOBSAutoClip
![Version](https://img.shields.io/github/v/release/Flarexi/WoWOBSAutoClip)

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

### 🖥️ Console Preview
```
============================================
      WoWOBSAutoClip - Raid Monitor
============================================

>> OBS is already running.
>> FOUND: WoWCombatLog-010226_1800.txt
>> Log file is fresh. Ready!
>> OBS CONNECTED successfully.
>> MONITORING ACTIVE <<

!!! RECORDING STARTED: Jin'rokh the Breaker
>> PLAYER DEATH: Playerone-EU
>> PLAYER DEATH: Playertwo-EU
!!! RECORDING STOPPED
>> Waiting 5s to finalize log data...
>> Giving OBS 3s to release file handle...
>> FINALIZED: 2026-01-02 18-09-55_Jinrokh_the_Breaker_KILL.mkv
```
---
