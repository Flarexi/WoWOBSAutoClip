🛡️ WoWOBSAutoClip

WoWOBSAutoClip is a lightweight Python automation tool for World of Warcraft players. It monitors your combat logs in real-time to intelligently control OBS Studio, ensuring you only record boss encounters while automatically adding player death chapters and organized filenames.
✨ Features

    Automatic Recording: Starts recording on ENCOUNTER_START and stops on ENCOUNTER_END.

    Smart Naming: Automatically renames files to [Timestamp]_[BossName]_[WIN/WIPE].mkv.

    Player Death Chapters: Embeds video chapters at the exact second a player dies (filters for -EU realms).

    Lossless Processing: Uses mkvmerge to inject chapters instantly without re-encoding the video.

    Zero Plugins: No OBS chapter plugins required; the script handles all logic internally.

📋 Prerequisites

    OBS Studio: Must be running with the WebSocket server enabled.

    MKVToolNix: Required for the chapter embedding feature.

    Python 3.x: Ensure Python is added to your system PATH.

⚙️ Setup & Configuration
1. World of Warcraft

You must enable Advanced Combat Logging for death detection to work:

    Esc -> Options -> Search for Advanced Combat Logging -> Enable.

2. OBS WebSocket

    Go to Tools -> WebSocket Server Settings.

    Click Enable WebSocket Server.

    Note your Server Port (default 4455) and Server Password.

3. Script Configuration

Open WoWOBSAutoClip.py and update the Configuration section at the top:
Python

# --- Configuration ---
OBS_HOST = 'localhost'
OBS_PORT = 4455
OBS_PASSWORD = 'your_obs_password'
WOW_LOG_DIRECTORY = r"C:\Games\World of Warcraft\_classic_\Logs"
MKVMERGE_CMD = r"C:\Program Files\MKVToolNix\mkvmerge.exe"

🚀 How to Use

    Install dependencies:
    Bash

pip install obs-websocket-py

Run the script:
Bash

    python WoWOBSAutoClip.py

    Raid! The script will find the latest log file automatically and wait for the pull.

🛠️ Troubleshooting

    WinError 2: The script can't find mkvmerge.exe. Verify the path in the configuration.

    No Chapters: Ensure "Advanced Combat Logging" is enabled in-game.

    Filenames not changing: Ensure OBS is saving in .mkv format (Settings -> Output -> Recording).