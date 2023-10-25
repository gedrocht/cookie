from gtts import gTTS
from playsound import playsound
import os
import tempfile
from pydub import AudioSegment
from pydub.playback import play

def text_to_speech(text, lang='en'):
    """
    Convert text to speech and play it.

    Parameters:
    - text (str): The text to be converted to speech.
    - lang (str, optional): Language code. Default is 'en' for English.

    Returns:
    None
    """
    
    # Create a temporary file to store the generated audio
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
        tts = gTTS(text=text, lang=lang, slow=False, tld="co.uk")
        temp_filename = temp_audio_file.name + ".mp3"

        tts.save(temp_filename)
        
        audio_segment = AudioSegment.from_mp3(temp_filename)
        louder_audio = audio_segment + 7
        louder_audio.export(temp_filename, format="mp3")

        # Play the generated audio
        playsound(temp_filename)
        temp_audio_file.close()
        os.unlink(temp_filename)

if __name__ == "__main__":
    # Test the function
    text = input("Enter text to convert to speech: ")
    text_to_speech(text)