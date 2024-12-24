import os
import subprocess
import time
import re

def get_audio_duration(file_path):
    try:
        result = subprocess.run(
            ['ffmpeg', '-i', file_path],
            stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
        )
        output = result.stderr
        # Look for the "Duration: " line in the ffmpeg output
        for line in output.split('\n'):
            if "Duration" in line:
                duration_str = line.split(",")[0].split("Duration:")[1].strip()
                # Convert duration from HH:MM:SS format to seconds
                h, m, s = duration_str.split(':')
                return int(h) * 3600 + int(m) * 60 + float(s)
    except Exception as e:
        print(f"Error retrieving duration: {e}")
        return None

def speak(text):
    print(f"speaking text with length {len(text)}")
    escaped_text = re.sub(r"'", r"'\"'\"'", text)
    print("generating audio")
    os.system(f"curl -G --data-urlencode 'text={escaped_text}' -o ~/tts.wav '192.168.0.7:5000'")
#    print("playing audio")
    os.system(f"ffplay -autoexit -nodisp ~/tts.wav")

def real_speak(text):
    print("starting echo process")
    echo_text = f"text='..., ...', {text.replace('. ', '....')}"
    echo_process = subprocess.Popen(['echo', echo_text], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Ensure the stdout is flushed
    echo_process.stdout.flush()
    print("starting piper process")
    piper_process = subprocess.Popen(
        ['curl', '-X', 'POST', '--data-urlencode', '@-', '-o', '~/tts_output_tmp.wav', '192.168.0.7:5000'],
        stdin=echo_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("waiting for piper...")
    piper_process.communicate()
    print("starting mv process")
    cp_process = None
    try:
        cp_process = subprocess.Popen(['mv', '/home/user/tts_output_tmp.wav', '/home/user/tts_output.wav'])
        cp_process.communicate()
    except Exception as e:
        print(str(e[0:10]) + "...")
        pass
    cp_process.communicate()
    duration_in_seconds = get_audio_duration("/home/user/tts_output.wav")
    print("starting ffplay process")
    time_started = time.time()
    ffplay_process = subprocess.Popen(
        ['ffplay', '-f', 's16le', '-ar', '22050', '-ac', '1', '-nodisp', '-autoexit', '-i', '/home/user/tts_output.wav'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    echo_process.stdout.close()
#    piper_process.stdin.close()

    return (tts_process, duration_in_seconds, time_started)

def speak_tts_queue(tts_queue):
    print("speaking tts queue")
    global tts_duration
    global tts_time_started
    global tts_queue_empty
    global tts_process
    tts_queue_empty = False
    for text in tts_queue:
      if not tts_process is None and \
         tts_duration > 0 and \
         not tts_time_started is None:
        while (time.time() - tts_time_started) < tts_duration:
            time.sleep(0.1)
        tts_process.terminate()
      # tts_process, tts_duration, tts_time_started = \
        print("speaking text")
        speak(text.replace("LET","let")
                    .replace("IT","it")
                    .replace("911","nine one one")
                )
    tts_queue_empty = True

def is_speaking(process):
    return False
    global tts_time_started
    global tts_duration
    return (time.time() - tts_time_started) < tts_duration