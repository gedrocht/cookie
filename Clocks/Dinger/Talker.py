from gtts import gTTS
from playsound import playsound
import os
import tempfile

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
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_audio_file.name + ".mp3")
        
        # Play the generated audio
        playsound(temp_audio_file.name + ".mp3")
        temp_audio_file.close()
        os.unlink(temp_audio_file.name + ".mp3")

if __name__ == "__main__":
    # Test the function
    text = input("Enter text to convert to speech: ")
    text_to_speech(text)