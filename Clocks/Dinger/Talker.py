from gtts import gTTS
from playsound import playsound
import os
# import tempfile
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
    
    # with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:

    new_file = ""

    if not str.isalnum(text[-1]):
        text = text[:-1]

    audio_filename = text + ".mp3"
    audio_filename = audio_filename.replace(" ", "_").replace("?", "").replace("!", "").replace(":", "")

    if not os.path.exists(audio_filename):
        new_file = audio_filename
        tts = gTTS(text=text, lang=lang, slow=False, tld="co.uk")
        tts.save(audio_filename)
        
        audio_segment = AudioSegment.from_mp3(audio_filename)
        louder_audio = audio_segment + 5
        louder_audio.export(audio_filename, format="mp3")

    playsound(audio_filename)
    return new_file

if __name__ == "__main__":
    # Test the function
    text = input("Enter text to convert to speech: ")
    text_to_speech(text)