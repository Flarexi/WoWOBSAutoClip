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
REGEX_START = re.compile(r"ENCOUNTER_START,(?P<enc_id>\d+),\"(?P<boss_name>.*?)\"")
REGEX_END = re.compile(r"ENCOUNTER_END,(?P<enc_id>\d+),.*?,.*?,(?P<result>\d+)")
REGEX_M_START = re.compile(r"CHALLENGE_MODE_START,\"(?P<zone_name>.*?)\",\d+,\d+,(?P<key_level>\d+)")
REGEX_M_END = re.compile(r"CHALLENGE_MODE_END,\d+,(?P<result>\d+)")

# --- 4. Global State ---
state_lock = threading.Lock()
is_recording = is_finalizing = is_mplus_active = False
obs_client = current_enc_id = None
current_event_name = "Unknown_Event"

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
    """Attempts to rename the file with retries to handle WinError 32 (file locking)."""
    new_path = os.path.join(os.path.dirname(old_path), new_name)
    for i in range(5):
        try:
            os.rename(old_path, new_path)
            print(f"{Color.GREEN}{Color.BOLD}>> FINALIZED: {new_name}{Color.END}\n")
            return True
        except OSError:
            time.sleep(1)
    print(f"{Color.RED}!! Error: Could not rename file. It might still be in use by OBS.{Color.END}")
    return False

def delayed_stop(delay_time, client, result_code, event_name):
    """Wait for log buffer, stop recording, and rename."""
    global is_recording, is_finalizing
    is_finalizing = True
    print(f">> Waiting {delay_time}s to finalize log data...")
    time.sleep(delay_time)
    
    try:
        print(f"{Color.CYAN}!!! RECORDING STOPPED{Color.END}")
        response = client.call(requests.StopRecord())
        output_path = response.datain.get('outputPath') if hasattr(response, 'datain') else None
        
        if output_path:
            is_kill = (str(result_code) == '1')
            suffix = "KILL" if is_kill else "WIPE"
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            new_name = f"{timestamp}_{event_name}_{suffix}.mkv"
            safe_rename(output_path, new_name)
            
    except Exception as e:
        print(f"{Color.RED}!! OBS Error during stop: {e}{Color.END}")
    
    with state_lock:
        is_recording = is_finalizing = False

def start_monitor():
    global is_recording, is_finalizing, is_mplus_active, current_event_name, current_enc_id
    
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
    with open(wow_log_path, 'r', encoding='utf-8-sig', errors='ignore') as log_file:
        log_file.seek(0, os.SEEK_END)
        print(f"{Color.GREEN}{Color.BOLD}>> MONITORING ACTIVE <<{Color.END}")
        try:
            while True:
                line = log_file.readline()
                if not line:
                    time.sleep(0.01); continue
                
                m_s, m_e, m_ms, m_me = REGEX_START.search(line), REGEX_END.search(line), REGEX_M_START.search(line), REGEX_M_END.search(line)
                
                with state_lock:
                    if (m_ms or m_s) and (is_recording or is_finalizing): continue
                    
                    if m_ms and not is_recording:
                        current_event_name = f"MPlus_{m_ms.group('zone_name')}_plus{m_ms.group('key_level')}".replace(" ", "_")
                        client.call(requests.StartRecord())
                        print(f"{Color.CYAN}{Color.BOLD}!!! RECORDING STARTED: M+ {m_ms.group('zone_name')} (+{m_ms.group('key_level')}){Color.END}")
                        is_recording, is_mplus_active = True, True
                    
                    elif m_s and not is_recording:
                        current_enc_id = m_s.group('enc_id')
                        current_event_name = m_s.group('boss_name').replace(" ", "_")
                        client.call(requests.StartRecord())
                        print(f"{Color.CYAN}{Color.BOLD}!!! RECORDING STARTED: {m_s.group('boss_name')}{Color.END}")
                        is_recording, is_mplus_active = True, False
                    
                    elif m_e and is_recording and not is_mplus_active:
                        if m_e.group('enc_id') == current_enc_id:
                            is_recording = False
                            threading.Thread(target=delayed_stop, args=(STOP_DELAY_SECONDS, client, m_e.group('result'), current_event_name)).start()
                    
                    elif m_me and is_mplus_active:
                        is_recording = is_mplus_active = False
                        threading.Thread(target=delayed_stop, args=(STOP_DELAY_SECONDS, client, m_me.group('result'), current_event_name)).start()
                        
        except KeyboardInterrupt: print(f"\n{Color.YELLOW}>> Stopped by user.{Color.END}")
        finally: client.disconnect()

if __name__ == '__main__':
    start_monitor()