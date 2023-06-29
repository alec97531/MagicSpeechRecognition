from pydub import AudioSegment
from pydub.playback import play
def play_audio_desktop(audio_path):
    voiceover = AudioSegment.from_mp3(audio_path)
    play(voiceover)

def get_desktop_storage_path():
    return ""