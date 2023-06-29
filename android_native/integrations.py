import time
from speech_recognition.exceptions import TranscriptionNotReady
def await_assemblyai_recognition(audio_path, recognizer, key):
    retries = 0
    job_name = None
    _audio_path = audio_path
    while(True):
        try:
            text, confidence = recognizer.recognize_assemblyai(_audio_path, key, job_name=job_name)
        except TranscriptionNotReady as e:
            time.sleep(0.5)
            _audio_path = None
            if not job_name:
                job_name = e.job_name
        else:
            break
    return text
