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
WOW_LOG_DIRECTORY = r"C:\Path\To\World of Warcraft\_classic_\Logs" 
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

# Enable Windows Terminal color support
os.system('')

# --- 3. WoW Combat Log Regex Patterns ---
REGEX_START = re.compile(r".*?ENCOUNTER_START,.*?,\"(?P<boss_name>.*?)\",.*")
REGEX_END = re.compile(r".*?ENCOUNTER_END,.*?,\"(?P<boss_name>.*?)\",.*,(?P<result>0|1)")
REGEX_UNIT_DIED = re.compile(r".*?UNIT_DIED,.*?,\"(?P<unit_name>.*?)\",.*")

# --- 4. Global Variables and Locks ---
state_lock = threading.Lock()
is_recording = False
obs_client = None
recording_start_time = 0
current_boss_name = "Unknown_Boss"
active_markers = [] 

# --- 5. Functions ---

def launch_obs():
    try:
        tasklist = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq obs64.exe'], text=True)
        if 'obs64.exe' in tasklist:
            print(f"{Color.CYAN}>> OBS is already running.{Color.END}")
        else:
            print(f"{Color.YELLOW}>> Launching OBS Studio...{Color.END}")
            obs_dir = os.path.dirname(OBS_EXE_PATH)
            subprocess.Popen([OBS_EXE_PATH], cwd=obs_dir)
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
        except Exception as e:
            print(f"{Color.YELLOW}!! Connection attempt {attempt}/3 failed...{Color.END}")
            if attempt < 3:
                time.sleep(5)
    return None

def toggle_recording(client, start=True, boss_name=""):
    global recording_start_time, active_markers, current_boss_name
    if not client: return
    try:
        if start:
            active_markers = [] 
            current_boss_name = re.sub(r'[^\w\s-]', '', boss_name).strip().replace(" ", "_")
            client.call(requests.StartRecord()) 
            recording_start_time = time.time()
            print(f"{Color.CYAN}{Color.BOLD}!!! RECORDING STARTED: {boss_name}{Color.END}")
            return None
        else:
            print(f"{Color.CYAN}!!! RECORDING STOPPED{Color.END}")
            response = client.call(requests.StopRecord())
            if hasattr(response, 'datain') and response.datain.get('outputPath'):
                return response.datain.get('outputPath')
            return None
    except Exception as e:
        print(f"{Color.RED}!! OBS COMMAND ERROR: {e}{Color.END}")
        return None

def seconds_to_mkv_timecode(total_seconds):
    td = timedelta(seconds=max(0, total_seconds))
    t_micros = td.total_seconds() * 1000000
    micros = t_micros % 1000000
    t_secs = int(t_micros // 1000000)
    mins, secs = divmod(t_secs, 60)
    hrs, mins = divmod(mins, 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}.{int(micros // 1000):03d}"

def process_and_mux_chapters(video_path):
    global active_markers
    if not active_markers:
        return video_path
    try:
        xml_path = video_path.replace(".mkv", ".chapters.xml")
        xml_content = ['<?xml version="1.0" encoding="UTF-8"?>', '<Chapters>', '<EditionEntry>']
        for offset, label in active_markers:
            xml_content.append('<ChapterAtom>')
            xml_content.append(f'<ChapterDisplay><ChapterString>{label}</ChapterString></ChapterDisplay>')
            xml_content.append(f'<ChapterTimeStart>{seconds_to_mkv_timecode(offset)}</ChapterTimeStart>')
            xml_content.append('</ChapterAtom>')
        xml_content.append('</EditionEntry></Chapters>')
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(xml_content))
        
        temp_out = video_path.replace(".mkv", "_muxing.mkv")
        subprocess.run([MKVMERGE_CMD, "-o", temp_out, "--chapters", xml_path, video_path], 
                       check=True, capture_output=True)
        os.replace(temp_out, video_path)
        os.remove(xml_path)
        return video_path
    except Exception as e:
        print(f"{Color.RED}!! MUX ERROR: {e}{Color.END}")
        return video_path

def delayed_stop(delay_time, client, result_code):
    global current_boss_name
    print(f">> Waiting {delay_time}s to finalize log data...")
    time.sleep(delay_time)
    with state_lock:
        output_path = toggle_recording(client, start=False)
        if output_path:
            time.sleep(3) 
            final_path = process_and_mux_chapters(output_path)
            
            is_kill = (result_code == '1')
            suffix = "KILL" if is_kill else "WIPE"
            result_color = Color.GREEN if is_kill else Color.YELLOW
            
            dir_name = os.path.dirname(final_path)
            file_name = os.path.basename(final_path).replace(".mkv", "")
            new_filename = f"{file_name}_{current_boss_name}_{suffix}.mkv"
            new_path = os.path.join(dir_name, new_filename)
            
            for i in range(5):
                try:
                    os.rename(final_path, new_path)
                    print(f"{result_color}{Color.BOLD}>> FINALIZED: {new_filename}{Color.END}")
                    break
                except PermissionError:
                    print(f"{Color.YELLOW}!! File busy, retrying rename ({i+1}/5)...{Color.END}")
                    time.sleep(2)

def get_latest_combat_log_path(log_directory):
    files = glob.glob(os.path.join(log_directory, "WoWCombatLog-*.txt"))
    if not files: return None
    latest_file = max(files, key=os.path.getmtime)
    file_mod_time = os.path.getmtime(latest_file)
    age_minutes = (time.time() - file_mod_time) / 60
    
    print(f"{Color.CYAN}>> FOUND: {os.path.basename(latest_file)}{Color.END}")
    
    if age_minutes > 10:
        print(f"{Color.YELLOW}!! NOTE: This log is {age_minutes:.0f} mins old. Waiting for data...{Color.END}")
    else:
        print(f"{Color.GREEN}>> Log file is fresh. Ready!{Color.END}")
    return latest_file

def start_monitor():
    global is_recording, active_markers, recording_start_time
    launch_obs()
    wow_log_path = get_latest_combat_log_path(WOW_LOG_DIRECTORY)
    if not wow_log_path: return
    client = connect_to_obs()
    if not client: return

    log_file = open(wow_log_path, 'r', encoding='utf-8', errors='ignore')
    log_file.seek(0, os.SEEK_END)
    print(f"{Color.GREEN}{Color.BOLD}>> MONITORING ACTIVE <<{Color.END}")

    try:
        while True:
            line = log_file.readline()
            if not line:
                time.sleep(0.1)
                continue
            
            m_start = REGEX_START.search(line)
            m_end = REGEX_END.search(line)
            m_died = REGEX_UNIT_DIED.search(line)

            with state_lock:
                if m_start and not is_recording:
                    toggle_recording(client, start=True, boss_name=m_start.group('boss_name'))
                    is_recording = True
                elif m_end and is_recording:
                    is_recording = False
                    threading.Thread(target=delayed_stop, args=(STOP_DELAY_SECONDS, client, m_end.group('result'))).start()
                elif m_died and is_recording:
                    name = m_died.group('unit_name')
                    if '-' in name and name.upper().endswith('-EU'):
                        offset = time.time() - recording_start_time
                        active_markers.append((offset, f"Died: {name}"))
                        print(f"{Color.RED}>> PLAYER DEATH: {name}{Color.END}")
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}>> Stopped by user.{Color.END}")
    finally:
        log_file.close()
        if client: client.disconnect()

if __name__ == '__main__':
    start_monitor()