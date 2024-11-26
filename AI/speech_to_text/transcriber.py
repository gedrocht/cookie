import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
import sounddevice as sd
import numpy as np
import scipy
import queue
import time

_DEBUG_MESSAGES = True

# Initialize variables
device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
model_id = "openai/whisper-large-v3"

# Load the model and processor
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

# Parameters for audio recording
sample_rate = 16000
chunk_duration = 10  # Collect up to 10 seconds of audio
chunk_size = sample_rate * chunk_duration
audio_queue = queue.Queue()

# Parameters for VAD
silence_threshold = 0.01  # Adjust this value for sensitivity (lower is more sensitive)
silence_duration = 2.0    # Time in seconds to consider as silence
min_active_duration = 0.5 # Minimum duration of speech to start recording
silence_counter = 0       # Counter for detecting silence

# Function to process and transcribe audio
def callback(indata, frames, time, status):
    if status:
        if _DEBUG_MESSAGES:
            print(status)
    audio_queue.put(indata.copy())

def rms_energy(audio):
    """ Calculate Root Mean Square (RMS) Energy of the audio """
    return np.sqrt(np.mean(np.square(audio)))

def process_audio(audio_buffer):
    """ Function to process accumulated audio chunks """
    # Resample and convert audio to 16-bit PCM format
    audio_chunk = np.squeeze(audio_buffer)
    audio_chunk = np.int16(audio_chunk * 32767)
    
    # Process the audio through the whisper model
    inputs = processor(audio_chunk, return_tensors="pt", sampling_rate=sample_rate)
    inputs = {key: inputs[key].to(device) for key in inputs}
    
    with torch.no_grad():
        generated_ids = model.generate(inputs["input_features"])
    transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)
    
    return transcription[0]

def record_and_transcribe():
    # Create an empty buffer to accumulate audio data
    audio_buffer = np.zeros(0, dtype=np.float32)
    recording_active = False
    silence_counter = 0

    with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback):
        if _DEBUG_MESSAGES:
            print("Monitoring for speech... Press Ctrl+C to stop.")
        try:
            while True:
                # Get audio from queue and append to buffer
                while not audio_queue.empty():
                    data = audio_queue.get()
                    audio_buffer = np.append(audio_buffer, data)
                    
                    # Calculate the energy (RMS) of the current audio chunk
                    energy = rms_energy(data)

                    if energy > silence_threshold:
                        # Start recording when energy exceeds threshold (i.e., speech starts)
                        if not recording_active:
                            if _DEBUG_MESSAGES:
                                print("Speech detected, recording started...")
                            recording_active = True
                            silence_counter = 0

                        # Continue recording
                        audio_buffer = np.append(audio_buffer, data)

                    elif recording_active:
                        # Count silence periods once speech ends
                        silence_counter += len(data) / sample_rate
                        if silence_counter > silence_duration:
                            # Process the audio chunk if silence exceeds threshold
                            if _DEBUG_MESSAGES:
                                print("Silence detected, processing chunk...")
                            transcription = process_audio(audio_buffer)
                            if _DEBUG_MESSAGES:
                                print("Transcription:", transcription)
                            audio_buffer = np.zeros(0, dtype=np.float32)  # Reset buffer
                            recording_active = False
                            silence_counter = 0
                            if _DEBUG_MESSAGES:
                                print("Monitoring for speech...")

                # Process accumulated audio once we reach the target chunk size (to avoid memory overflow)
                if recording_active and len(audio_buffer) >= chunk_size:
                    if _DEBUG_MESSAGES:
                        print("Processing chunk due to size limit...")
                    transcription = process_audio(audio_buffer[:chunk_size])
                    if _DEBUG_MESSAGES:
                        print("Transcription:", transcription)
                    else:
                        print(transcription)
                    audio_buffer = audio_buffer[chunk_size:]  # Keep any leftover audio

        except KeyboardInterrupt:
            if _DEBUG_MESSAGES:
                print("Recording stopped.")

# Start the recording and transcription loop
record_and_transcribe()
