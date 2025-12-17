import time
import re
import os
import glob
import threading 
import subprocess
from datetime import datetime, timedelta
from obswebsocket import obsws, requests 

# --- 1. Configuration ---
OBS_HOST = '111.222.3.444' 
OBS_PORT = 1122
OBS_PASSWORD = 'OBS_PASSWORD'
WOW_LOG_DIRECTORY = r"P:\World of Warcraft\_classic_\Logs" 
STOP_DELAY_SECONDS = 5
MKVMERGE_CMD = r"C:\Program Files\MKVToolNix\mkvmerge.exe" 

# --- 2. WoW Combat Log Regex Patterns ---
REGEX_START = re.compile(r".*?ENCOUNTER_START,.*?,\"(?P<boss_name>.*?)\",.*")
REGEX_END = re.compile(r".*?ENCOUNTER_END,.*?,\"(?P<boss_name>.*?)\",.*,(?P<result>0|1)")
REGEX_UNIT_DIED = re.compile(r".*?UNIT_DIED,.*?,\"(?P<unit_name>.*?)\",.*")

# --- 3. Global Variables and Locks ---
state_lock = threading.Lock()
is_recording = False
obs_client = None
recording_start_time = 0
current_boss_name = "Unknown_Boss" # Tracked for filename
active_markers = [] 

# --- 4. Functions ---

def connect_to_obs():
    global obs_client 
    try:
        obs_client = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        obs_client.connect() 
        print(">> OBS CONNECTED successfully.")
        return obs_client
    except Exception as e:
        print(f"!! OBS ERROR: {e}") 
        return None

def toggle_recording(client, start=True, boss_name=""):
    global recording_start_time, active_markers, current_boss_name
    if not client: return
    try:
        if start:
            active_markers = [] 
            # Clean boss name for filename (remove spaces and invalid chars)
            current_boss_name = re.sub(r'[^\w\s-]', '', boss_name).strip().replace(" ", "_")
            
            client.call(requests.StartRecord()) 
            recording_start_time = time.time()
            print(f"!!! LOG MATCH: ENCOUNTER_START - BOSS: {boss_name}")
            print(f">> OBS COMMAND SUCCESS: Recording started.")
            return None
        else:
            print(f"!!! LOG MATCH: ENCOUNTER_END")
            response = client.call(requests.StopRecord())
            if hasattr(response, 'datain') and response.datain.get('outputPath'):
                return response.datain.get('outputPath')
            return None
    except Exception as e:
        print(f"!! OBS COMMAND ERROR: {e}")
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

        for i, (offset, label) in enumerate(active_markers):
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
        print(f"!! MUX ERROR: {e}")
        return video_path

def delayed_stop(delay_time, client, result_code):
    global current_boss_name
    print(f">> Waiting {delay_time}s to finalize recording...")
    time.sleep(delay_time)
    with state_lock:
        output_path = toggle_recording(client, start=False)
        if output_path:
            # 1. Embed chapters
            final_path = process_and_mux_chapters(output_path)
            
            # 2. Rename with Boss Name and Result
            suffix = "WIN" if result_code == '1' else "WIPE"
            
            # Get the directory and the original timestamp-based filename
            dir_name = os.path.dirname(final_path)
            file_name = os.path.basename(final_path).replace(".mkv", "")
            
            # Construct the new filename: [Timestamp]_[BossName]_[Status].mkv
            new_filename = f"{file_name}_{current_boss_name}_{suffix}.mkv"
            new_path = os.path.join(dir_name, new_filename)
            
            try:
                os.rename(final_path, new_path)
                print(f">> FINALIZED: {new_filename}")
            except Exception as e:
                print(f"!! RENAME ERROR: {e}")

def get_latest_combat_log_path(log_directory):
    files = glob.glob(os.path.join(log_directory, "WoWCombatLog-*.txt"))
    if not files: return None
    return max(files, key=os.path.getmtime)

def start_monitor():
    global is_recording, active_markers, recording_start_time
    wow_log_path = get_latest_combat_log_path(WOW_LOG_DIRECTORY)
    if not wow_log_path: return
    client = connect_to_obs()
    if not client: return

    log_file = open(wow_log_path, 'r', encoding='utf-8', errors='ignore')
    log_file.seek(0, os.SEEK_END)
    print(f">> MONITORING STARTED: {os.path.basename(wow_log_path)}")

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
                    
                if m_died and is_recording:
                    name = m_died.group('unit_name')
                    if '-' in name and name.upper().endswith('-EU'):
                        offset = time.time() - recording_start_time
                        active_markers.append((offset, f"Died: {name}"))
                        print(f">> PLAYER DEATH: {name} at {offset:.2f}s")

    except KeyboardInterrupt:
        print(">> Stopped by user.")
    finally:
        log_file.close()
        if client: client.disconnect()

if __name__ == '__main__':
    start_monitor()