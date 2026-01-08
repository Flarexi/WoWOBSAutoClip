import time
import re
import os
import glob
import threading
import subprocess
from datetime import datetime, timedelta
from obswebsocket import obsws, requests

# --- 1. Configuration ---
OBS_HOST = 'localhost'
OBS_PORT = 4455
OBS_PASSWORD = 'your_obs_password'
WOW_LOG_DIRECTORY = r"C:\Path\To\World of Warcraft\_retail_\Logs"
STOP_DELAY_SECONDS = 5
MKVMERGE_CMD = r"C:\Program Files\MKVToolNix\mkvmerge.exe"
OBS_EXE_PATH = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"

# --- 2. ANSI Colors ---
class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

os.system('') 

# --- 3. Regex Patterns ---
REGEX_START = re.compile(r".*?ENCOUNTER_START,(?P<enc_id>\d+),\"(?P<boss_name>.*?)\",.*")
REGEX_END = re.compile(r"ENCOUNTER_END,(?P<enc_id>\d+),.*,(?P<result>\d+)\s*$")
REGEX_M_START = re.compile(r".*?CHALLENGE_MODE_START,\"(?P<zone_name>.*?)\",\d+,\d+,(?P<key_level>\d+),.*")
REGEX_M_END = re.compile(r".*?CHALLENGE_MODE_END,\d+,(?P<result>\d+),.*")
REGEX_UNIT_DIED = re.compile(r".*?UNIT_DIED,.*?(?P<guid>Player-[\w-]+),\"(?P<unit_name>.*?)\"")

# --- 4. Global State ---
state_lock = threading.Lock()
is_recording = is_finalizing = is_mplus_active = False
obs_client = recording_start_time = current_enc_id = None
current_event_name = "Unknown_Event"
active_markers = []

# --- 5. Functions ---

def launch_obs():
    try:
        tasklist = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq obs64.exe'], text=True)
        if 'obs64.exe' in tasklist:
            print(f"{Color.CYAN}>> OBS is already running.{Color.END}")
        else:
            print(f"{Color.YELLOW}>> Launching OBS Studio...{Color.END}")
            subprocess.Popen([OBS_EXE_PATH], cwd=os.path.dirname(OBS_EXE_PATH))
            print(">> Waiting 10 seconds for OBS to initialize...")
            time.sleep(10)
    except Exception as e:
        print(f"{Color.RED}!! Warning during OBS check: {e}{Color.END}")

def connect_to_obs():
    global obs_client
    for attempt in range(1, 4):
        try:
            obs_client = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
            obs_client.connect()
            print(f"{Color.GREEN}>> OBS CONNECTED successfully.{Color.END}")
            return obs_client
        except:
            print(f"{Color.YELLOW}!! Connection attempt {attempt}/3 failed...{Color.END}")
            if attempt < 3: time.sleep(5)
    return None

def safe_rename(old_path, new_name):
    new_path = os.path.join(os.path.dirname(old_path), new_name)
    for i in range(5): # 5 Retries
        try:
            os.rename(old_path, new_path)
            return True
        except OSError:
            time.sleep(1)
    return False

def toggle_recording(client, start=True, event_name=""):
    global recording_start_time, active_markers, current_event_name
    if not client: return None
    try:
        if start:
            active_markers = []
            current_event_name = re.sub(r'[^\w\s-]', '', event_name).strip().replace(" ", "_")
            client.call(requests.StartRecord())
            recording_start_time = time.time()
            print(f"{Color.CYAN}{Color.BOLD}!!! RECORDING STARTED: {event_name}{Color.END}")
        else:
            print(f"{Color.CYAN}!!! RECORDING STOPPED{Color.END}")
            response = client.call(requests.StopRecord())
            return response.datain.get('outputPath') if hasattr(response, 'datain') else None
    except Exception as e: print(f"{Color.RED}!! OBS Error: {e}{Color.END}")
    return None

def process_and_mux_chapters(video_path):
    if not active_markers: return video_path
    try:
        xml_path = video_path.replace(".mkv", ".chapters.xml")
        xml_content = ['<?xml version="1.0" encoding="UTF-8"?>', '<Chapters>', '<EditionEntry>']
        for offset, label in active_markers:
            td = timedelta(seconds=max(0, offset))
            timecode = f"{int(td.total_seconds()//3600):02d}:{int((td.total_seconds()%3600)//60):02d}:{int(td.total_seconds()%60):02d}.{int(td.microseconds//1000):03d}"
            xml_content.append(f'<ChapterAtom><ChapterDisplay><ChapterString>{label}</ChapterString></ChapterDisplay><ChapterTimeStart>{timecode}</ChapterTimeStart></ChapterAtom>')
        xml_content.append('</EditionEntry></Chapters>')
        with open(xml_path, 'w', encoding='utf-8') as f: f.write('\n'.join(xml_content))
        temp_out = video_path.replace(".mkv", "_mux.mkv")
        subprocess.run([MKVMERGE_CMD, "-o", temp_out, "--chapters", xml_path, video_path], check=True, capture_output=True)
        os.replace(temp_out, video_path)
        if os.path.exists(xml_path): os.remove(xml_path)
    except Exception as e:
        print(f"{Color.RED}!! Muxing Error: {e}{Color.END}")
    return video_path

def delayed_stop(delay_time, client, result_code):
    """Wait for log buffer, stop recording, mux chapters, and rename."""
    global current_event_name, is_recording, is_finalizing
    is_finalizing = True
    print(f">> Waiting {delay_time}s to finalize log data...")
    time.sleep(delay_time)
    
    output_path = toggle_recording(client, start=False)
    
    if output_path:
        # Give Windows a moment to stabilize the file handle
        time.sleep(2) 
        final_path = process_and_mux_chapters(output_path)
        
        is_kill = (str(result_code) == '1')
        suffix = "KILL" if is_kill else "WIPE"
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        new_name = f"{timestamp}_{current_event_name}_{suffix}.mkv"
        
        # Use safe_rename to handle file locking issues
        if safe_rename(final_path, new_name):
            print(f"{(Color.GREEN if is_kill else Color.YELLOW)}{Color.BOLD}>> FINALIZED: {new_name}{Color.END}\n")
        else:
            print(f"{Color.RED}!! Error: Could not rename {os.path.basename(final_path)} (File Locked){Color.END}")

    with state_lock:
        is_recording = is_finalizing = False

def start_monitor():
    global is_recording, is_finalizing, is_mplus_active, active_markers, recording_start_time, current_event_name, current_enc_id
    
    print(f"{Color.GREEN}{Color.BOLD}[SUCCESS] Monitoring WoW Logs...{Color.END}")
    print(f"(Keep this window open while playing!)\n")
    
    launch_obs()
    
    # 1. Path & Expansion Detection
    files = glob.glob(os.path.join(WOW_LOG_DIRECTORY, "WoWCombatLog-*.txt"))
    if not files: return print(f"{Color.RED}!! No logs found.{Color.END}")
    wow_log_path = max(files, key=os.path.getmtime)
    
    path_norm = WOW_LOG_DIRECTORY.lower()
    expansion = "World of Warcraft Retail"
    if "_classic_era_" in path_norm: expansion = "World of Warcraft Classic Era"
    elif "_classic_anniversary_" in path_norm: expansion = "World of Warcraft Anniversary"
    elif "_classic_" in path_norm: expansion = "World of Warcraft Classic"

    # 2. Information Display
    print(f"{Color.CYAN}>> FULL LOG PATH: {wow_log_path}{Color.END}")
    print(f"{Color.CYAN}>> {expansion}{Color.END}")

    # 3. Freshness Check
    age_minutes = (time.time() - os.path.getmtime(wow_log_path)) / 60
    if age_minutes > 10:
        print(f"{Color.YELLOW}!! NOTE: This log is {age_minutes:.0f} mins old. Waiting for data...{Color.END}")

    # 4. OBS Connection
    client = connect_to_obs()
    if not client: return

    # 5. Final Active Signal
    with open(wow_log_path, 'r', encoding='utf-8', errors='ignore') as log_file:
        log_file.seek(0, os.SEEK_END)
        print(f"{Color.GREEN}{Color.BOLD}>> MONITORING ACTIVE <<{Color.END}")
        try:
            while True:
                line = log_file.readline()
                if not line:
                    time.sleep(0.01); continue
                m_s, m_e, m_ms, m_me, m_d = REGEX_START.search(line), REGEX_END.search(line), REGEX_M_START.search(line), REGEX_M_END.search(line), REGEX_UNIT_DIED.search(line)
                with state_lock:
                    if (m_ms or m_s) and (is_recording or is_finalizing): continue
                    if m_ms and not is_recording:
                        toggle_recording(client, start=True, event_name=f"M+ {m_ms.group('zone_name')} (+{m_ms.group('key_level')})")
                        current_event_name, is_recording, is_mplus_active = f"MPlus_{m_ms.group('zone_name')}_plus{m_ms.group('key_level')}".replace(" ", "_"), True, True
                    elif m_s and not is_recording:
                        current_enc_id = m_s.group('enc_id')
                        toggle_recording(client, start=True, event_name=m_s.group('boss_name'))
                        is_recording, is_mplus_active = True, False
                    elif m_d and is_recording:
                        active_markers.append((time.time() - recording_start_time, f"Died: {m_d.group('unit_name')}"))
                        print(f"{Color.RED}>> PLAYER DEATH: {m_d.group('unit_name')}{Color.END}")
                    elif m_e and is_recording and not is_mplus_active:
                        if m_e.group('enc_id') == current_enc_id:
                            is_recording = False
                            threading.Thread(target=delayed_stop, args=(STOP_DELAY_SECONDS, client, m_e.group('result'))).start()
                    elif m_me and is_mplus_active:
                        is_recording = is_mplus_active = False
                        threading.Thread(target=delayed_stop, args=(STOP_DELAY_SECONDS, client, m_me.group('result'))).start()
        except KeyboardInterrupt: print(f"\n{Color.YELLOW}>> Stopped by user.{Color.END}")
        finally: client.disconnect()

if __name__ == '__main__':
    start_monitor()