import os
import subprocess
import shutil
import sys
import util

def log(msg):
    util.log(f"[A_PROC] {msg}")

# Define the directories and paths
project_base_dir = '/mnt/c/Users/gugst/Documents/GitHub/cookie/AI/'
speech_to_text_dir = '/mnt/c/Users/gugst/Documents/GitHub/cookie/AI/speech_to_text'
text_to_speech_dir = '/mnt/c/Users/gugst/Documents/GitHub/cookie/AI/text_to_speech'
speech_to_text_env_path = '../environments/whisper/bin'
text_to_speech_env_path = '../environments/fish/bin'

def activate_env(env_path):
    """Activate the virtual environment."""
    activate_script = os.path.join(env_path, 'activate')
    subprocess.run(f"source {activate_script}", shell=True, executable="/bin/bash")

def split_audio(audio_file):
    """Split the audio into chunks."""
    log("====== SPLITTING AUDIO INTO CHUNKS")
    split_script = os.path.join(text_to_speech_env_path, 'python')
    subprocess.run([split_script, "split_reference_audio.py", audio_file])

def move_chunks(chunk_directory):
    """Move chunk directory to speech_to_text_dir."""
    dest_dir = os.path.join(speech_to_text_dir, f'cloned_voices/')
    log(f"Moving {chunk_directory} to {dest_dir}")
    shutil.move(chunk_directory, dest_dir)
    return dest_dir

def transcribe_chunks(chunk_directory):
    """Transcribe the chunks using Whisper."""
    log("====== TRANSCRIBING CHUNKS")
    
    chunks = []
    for chunk in os.listdir(chunk_directory):
      if chunk.endswith('.wav'):
        chunks.append(chunk)
    chunks.sort()

    for i, chunk in enumerate(chunks):
      chunk_path = os.path.join(chunk_directory, chunk)
      log(f"Transcribing {os.path.basename(chunk_path)} ({i+1}/{len(chunks)})")
      whisper_script = os.path.join(speech_to_text_env_path, 'python')
      subprocess.run([whisper_script, "whisper.py", chunk_path], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

def add_new_voice(audio_file):
    # Activate text-to-speech environment
    activate_env(text_to_speech_env_path)
    
    # Change directory to text_to_speech_dir
    os.chdir(text_to_speech_dir)
    
    # Split audio into chunks
    split_audio(audio_file)
    
    # Move chunks to speech_to_text_dir
    chunk_directory = f"{text_to_speech_dir}/cloned_voices/{os.path.basename(audio_file).replace('.wav', '')}"
    new_chunk_directory = move_chunks(chunk_directory)
    
    # Activate speech-to-text environment
    activate_env(speech_to_text_env_path)
    
    # Change directory to speech_to_text_dir
    os.chdir(speech_to_text_dir)
    
    # Transcribe the audio chunks
    transcribe_chunks(new_chunk_directory)
    
    log(f"Moving {new_chunk_directory} to {chunk_directory}")
    # Move the chunks back to text_to_speech_dir
    shutil.move(new_chunk_directory, chunk_directory)
    
    # Activate text-to-speech environment again
    activate_env(text_to_speech_env_path)
    
    # Change directory to text_to_speech_dir
    os.chdir(text_to_speech_dir)
    
    # Print processing complete
    log("====== PROCESSING COMPLETE")


if __name__ == "__main__":
    # Replace 'your_audio_file.wav' with your actual audio filename
    audio_file = sys.argv[1]
    add_new_voice(audio_file)
