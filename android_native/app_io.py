try:
    import android
except ModuleNotFoundError:
    PLATFORM = "DESKTOP"
    from desktop_io import play_audio_desktop, get_desktop_storage_path
else:
    PLATFORM = "ANDROID"
    from android_io import play_audio_android, init_app_android, get_android_storage_path, listen_in_background_android

def play_audio(audio_path):
    if PLATFORM == "ANDROID":
        play_audio_android(audio_path)
    else:
        play_audio_desktop(audio_path)

def get_storage_path():
    if PLATFORM == "ANDROID":
        return get_android_storage_path()
    else:
        return get_desktop_storage_path()

def init_platform():
    if PLATFORM == "ANDROID":
        init_app_android()
        return "ANDROID"
    else:
        return "DESKTOP"
    
def listen_in_background(callback):
    if PLATFORM == "ANDROID":
        return listen_in_background_android(callback)