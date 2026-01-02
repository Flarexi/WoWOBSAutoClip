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
REGEX_START = re.compile(r".*?ENCOUNTER_START,(\d+),\"(?P<boss_name>.*?)\",.*")
REGEX_END = re.compile(r".*?ENCOUNTER_END,(\d+),\"(?P<boss_name>.*?)\",.*?,(?P<result>\d+)")
REGEX_M_START = re.compile(r".*?CHALLENGE_MODE_START,\"(?P<zone_name>.*?)\",\d+,\d+,(?P<key_level>\d+),.*")
REGEX_M_END = re.compile(r".*?CHALLENGE_MODE_END,\d+,(?P<result>\d+),.*")
REGEX_UNIT_DIED = re.compile(r".*?UNIT_DIED,.*,\"(?P<unit_name>.*?-.*?)\"")

# --- 4. Global State ---
state_lock = threading.Lock()
is_recording = False
is_mplus_active = False
obs_client = None
recording_start_time = 0
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
            time.sleep(10)
    except Exception as e:
        print(f"{Color.RED}!! OBS Launch Error: {e}{Color.END}")

def connect_to_obs():
    global obs_client
    for attempt in range(1, 4):
        try:
            obs_client = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
            obs_client.connect()
            print(f"{Color.GREEN}>> OBS CONNECTED.{Color.END}")
            return obs_client
        except:
            print(f"{Color.YELLOW}!! Connection attempt {attempt}/3 failed...{Color.END}")
            time.sleep(5)
    return None

def toggle_recording(client, start=True, event_name=""):
    global recording_start_time, active_markers, current_event_name
    if not client: return None
    try:
        if start:
            active_markers = []
            # Filename-safe version of the event name
            current_event_name = re.sub(r'[^\w\s-]', '', event_name).strip().replace(" ", "_")
            client.call(requests.StartRecord())
            recording_start_time = time.time()
            print(f"{Color.CYAN}{Color.BOLD}!!! RECORDING STARTED: {event_name}{Color.END}")
        else:
            print(f"{Color.CYAN}!!! RECORDING STOPPED{Color.END}")
            response = client.call(requests.StopRecord())
            return response.datain.get('outputPath') if hasattr(response, 'datain') else None
    except Exception as e:
        print(f"{Color.RED}!! OBS Command Error: {e}{Color.END}")
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
    if not active_markers: return video_path
    try:
        xml_path = video_path.replace(".mkv", ".chapters.xml")
        xml_content = ['<?xml version="1.0" encoding="UTF-8"?>', '<Chapters>', '<EditionEntry>']
        for offset, label in active_markers:
            xml_content.append(f'<ChapterAtom><ChapterDisplay><ChapterString>{label}</ChapterString></ChapterDisplay>')
            xml_content.append(f'<ChapterTimeStart>{seconds_to_mkv_timecode(offset)}</ChapterTimeStart></ChapterAtom>')
        xml_content.append('</EditionEntry></Chapters>')
        
        with open(xml_path, 'w', encoding='utf-8') as f: f.write('\n'.join(xml_content))
        
        temp_out = video_path.replace(".mkv", "_mux.mkv")
        subprocess.run([MKVMERGE_CMD, "-o", temp_out, "--chapters", xml_path, video_path], check=True, capture_output=True)
        os.replace(temp_out, video_path)
        if os.path.exists(xml_path): os.remove(xml_path)
        return video_path
    except Exception as e:
        print(f"{Color.RED}!! Muxing Error: {e}{Color.END}")
        return video_path

def delayed_stop(delay_time, client, result_code):
    global current_event_name
    print(f">> Finalizing data in {delay_time}s...")
    time.sleep(delay_time)
    with state_lock:
        output_path = toggle_recording(client, start=False)
        if output_path:
            time.sleep(3) 
            final_path = process_and_mux_chapters(output_path)
            is_kill = (str(result_code) == '1')
            suffix = "SUCCESS" if is_kill else "FAILED"
            result_color = Color.GREEN if is_kill else Color.YELLOW
            
            new_name = f"{os.path.basename(final_path).replace('.mkv', '')}_{current_event_name}_{suffix}.mkv"
            new_path = os.path.join(os.path.dirname(final_path), new_name)
            
            for i in range(5):
                try:
                    os.rename(final_path, new_path)
                    print(f"{result_color}{Color.BOLD}>> FINALIZED: {new_name}{Color.END}")
                    break
                except:
                    time.sleep(2)

def start_monitor():
    global is_recording, is_mplus_active, active_markers, recording_start_time, current_event_name
    launch_obs()
    
    # Locate the latest log file
    files = glob.glob(os.path.join(WOW_LOG_DIRECTORY, "WoWCombatLog-*.txt"))
    if not files: 
        return print(f"{Color.RED}!! No logs found in: {WOW_LOG_DIRECTORY}{Color.END}")
    
    wow_log_path = max(files, key=os.path.getmtime)
    log_filename = os.path.basename(wow_log_path)

    # Detect Expansion Folder for the UI
    path_parts = WOW_LOG_DIRECTORY.lower().split(os.sep)
    expansion = "Unknown"
    for part in ["_retail_", "_classic_", "_classic_era_", "_classic_anniversary_"]:
        if part in path_parts:
            expansion = part.strip("_").upper()
            break

    client = connect_to_obs()
    if not client: return

    with open(wow_log_path, 'r', encoding='utf-8', errors='ignore') as log_file:
        log_file.seek(0, os.SEEK_END)
        # --- REFINED OUTPUT ---
        print(f"{Color.GREEN}{Color.BOLD}>> MONITORING ACTIVE [{expansion}]{Color.END}")
        print(f"{Color.CYAN}>> LOG FILE: {log_filename}{Color.END}\n")

        try:
            while True:
                line = log_file.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                
                m_s = REGEX_START.search(line)
                m_e = REGEX_END.search(line)
                m_ms = REGEX_M_START.search(line)
                m_me = REGEX_M_END.search(line)
                m_d = REGEX_UNIT_DIED.search(line)

                with state_lock:
                    if m_ms and not is_recording:
                        zone, lvl = m_ms.group('zone_name'), m_ms.group('key_level')
                        display_name = f"M+ {zone} (+{lvl})"
                        toggle_recording(client, start=True, event_name=display_name)
                        # Re-set current_event_name for the file rename suffix specifically
                        current_event_name = f"MPlus_{zone}_plus{lvl}".replace(" ", "_")
                        is_recording = True
                        is_mplus_active = True

                    elif m_s:
                        boss_name = m_s.group('boss_name')
                        if not is_recording:
                            toggle_recording(client, start=True, event_name=boss_name)
                            is_recording = True
                            is_mplus_active = False
                        elif is_mplus_active:
                            active_markers.append((time.time() - recording_start_time, f"Boss Start: {boss_name}"))
                            print(f"{Color.CYAN}>> BOSS START: {boss_name}{Color.END}")

                    elif m_e and is_mplus_active:
                        boss_name = m_e.group('boss_name')
                        res = "Defeated" if m_e.group('result') == '1' else "Wipe"
                        active_markers.append((time.time() - recording_start_time, f"Boss {res}: {boss_name}"))
                        print(f"{Color.CYAN}>> BOSS {res.upper()}: {boss_name}{Color.END}")

                    elif m_d and is_recording:
                        name = m_d.group('unit_name')
                        active_markers.append((time.time() - recording_start_time, f"Died: {name}"))
                        print(f"{Color.RED}>> PLAYER DEATH: {name}{Color.END}")

                    elif (m_e and not is_mplus_active) or m_me:
                        is_recording = False
                        is_mplus_active = False
                        res = m_e.group('result') if m_e else m_me.group('result')
                        threading.Thread(target=delayed_stop, args=(STOP_DELAY_SECONDS, client, res)).start()
                        
        except KeyboardInterrupt:
            print(f"\n{Color.YELLOW}>> Monitor Stopped.{Color.END}")
        finally:
            if client: client.disconnect()

if __name__ == '__main__':
    start_monitor()