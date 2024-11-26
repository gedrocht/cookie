from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
from utils import util
from colorama import Fore

def log(msg):
    util.log(f"[ASPLIT] {msg}")

# (input_wav, base_dir, min_silence_len=100, silence_thresh=-40, keep_silence=85, min_duration=1750, max_duration=8500)
def split_audio_on_silence(input_wav, base_dir, min_silence_len=35, silence_thresh=-12, keep_silence=85, min_duration=1750, max_duration=8500):
    """
    Splits a .wav file into smaller chunks based on silence between spoken words.

    Parameters:
    - input_wav (str): Path to the input .wav file.
    - output_dir (str): Path to the output directory to save the split files.
    - min_silence_len (int): Minimum length of silence in milliseconds to split on. Default is 500ms.
    - silence_thresh (int): Silence threshold (in dBFS). Silence quieter than this will be considered a break. Default is -40dBFS.
    - keep_silence (int): Amount of silence (in ms) to leave at the beginning and end of each chunk. Default is 150ms.
    - min_duration (int): Minimum duration for each split file in milliseconds. Default is 5000ms (5 seconds).
    - max_duration (int): Maximum duration for each split file in milliseconds. Default is 20000ms (20 seconds).
    """

    # Load the input wav file
    audio = AudioSegment.from_wav(input_wav)

    log(f"Splitting {input_wav} into chunks between {min_duration}ms and {max_duration}ms")
    # Split the audio where silence is detected
    chunks = split_on_silence(
        audio, 
        min_silence_len=min_silence_len, 
        silence_thresh=silence_thresh, 
        keep_silence=keep_silence
    )
    log(f"Split {input_wav} into {len(chunks)} chunks")

    output_dir = f"{base_dir}/{os.path.basename(input_wav.replace('.wav',''))}"

    # Create the output directory if it doesn't exist
    if not os.path.exists(f"{output_dir}"):
        log(f"Created output directory {output_dir}")
        os.makedirs(f"{output_dir}")
    else:
        log(f"Set output directory to {output_dir}")

    output_files = []
    current_chunk = AudioSegment.empty()
    chunk_number = 1

    for chunk in chunks:
        if len(current_chunk) + len(chunk) < max_duration:
            current_chunk += chunk
        else:
            # Save the current chunk if its length is within the desired range
            if len(current_chunk) >= min_duration:
                output_file = os.path.join(f"{output_dir}", f"chunk_{chunk_number}.wav")
                current_chunk.export(output_file, format="wav")
                log(f"Wrote chunk {chunk_number} to file")
                output_files.append(output_file)
                chunk_number += 1
            current_chunk = chunk  # Start a new chunk with the current one

    # Export the last chunk if it's long enough
    if len(current_chunk) >= min_duration and len(current_chunk) <= max_duration:
        output_file = os.path.join(output_dir, f"chunk_{chunk_number}.wav")
        current_chunk.export(output_file, format="wav")
        log(f"Wrote chunk {chunk_number} to file")
        output_files.append(output_file)

    return output_files