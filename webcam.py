from gtts import gTTS
from playsound import playsound
import tempfile
import os

def do_tts(text):
    tts = gTTS(text)
    temp_file = tempfile.NamedTemporaryFile(suffix= ".mp3", delete= False)
    tts.save(temp_file.name)
    return os.path.abspath(temp_file.name)
    
    
    
playsound(do_tts("No uniform detected."))