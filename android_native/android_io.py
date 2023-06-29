from kivy.logger import Logger
from android.storage import app_storage_path
from android.permissions import request_permissions, Permission
from jnius import autoclass
import time
import threading
def init_app_android():
    request_permissions([Permission.INTERNET, Permission.RECORD_AUDIO])

def get_android_storage_path():
    return app_storage_path()+"/"

def play_audio_android(audio_path):
    mplayer = MusicPlayerAndroid()
    if mplayer.load(audio_path):
        mplayer.play()
    else:
        Logger.info(f"can't load {audio_path}")

class MusicPlayerAndroid(object):
    def __init__(self):
        MediaPlayer = autoclass('android.media.MediaPlayer')
        self.mplayer = MediaPlayer()

        self.secs = 0
        self.actualsong = ''
        self.length = 0
        self.isplaying = False

    def __del__(self):
        # self.stop()
        # self.mplayer.release()
        Logger.info('mplayer: deleted')

    def load(self, filename):
        try:
            self.actualsong = filename
            self.secs = 0
            self.mplayer.setDataSource(filename)        
            self.mplayer.prepare()
            self.length = self.mplayer.getDuration() / 1000
            Logger.info('mplayer load: %s' %filename)
            Logger.info ('type: %s' %type(filename) )
            return True
        except:
            Logger.info('error in title: %s' % filename) 
            return False

    def unload(self):
            self.mplayer.reset()

    def play(self):
        self.mplayer.start()
        self.isplaying = True
        Logger.info('mplayer: play')

    def stop(self):
        self.mplayer.stop()
        self.secs=0
        self.isplaying = False
        Logger.info('mplayer: stop')

    def seek(self,timepos_secs):
        self.mplayer.seekTo(timepos_secs * 1000)
        Logger.info ('mplayer: seek %s' %int(timepos_secs))


# RECORDING
class MusicRecorderAndroid(object):
    def __init__(self, filenum):
        MediaRecorder = autoclass('android.media.MediaRecorder')
        # get the needed Java classes
        AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
        AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')

        mRecorder = MediaRecorder()
        mRecorder.setAudioSource(AudioSource.MIC)
        mRecorder.setOutputFormat(OutputFormat.MPEG_4)
        self.output_file = f'{get_android_storage_path()}temp/temp{filenum}.mp4'
        mRecorder.setOutputFile(self.output_file)
        mRecorder.setAudioEncoder(AudioEncoder.AMR_NB)
        mRecorder.setAudioEncodingBitRate(16*44100);
        mRecorder.setAudioSamplingRate(44100);
        mRecorder.prepare()
        self.mRecorder = mRecorder
    def start_recording(self):
        # record 5 seconds
        self.mRecorder.start()
    def stop_recording(self):
        self.mRecorder.stop()
    def release_recording(self):
        self.mRecorder.release()
    def record_chunk(self, seconds):
        self.start_recording()
        time.sleep(seconds)
        self.stop_recording()
        self.release_recording()
        return self.output_file

def listen_in_background_android(callback):
    history_count = 5
    running = [True]
    def threaded_listen():
        filenum = 0
        while running[0]:
            if filenum == 5:
                filenum = 0
            else:
                filenum += 1
            recorder = MusicRecorderAndroid(filenum)
            fname = recorder.record_chunk(5)
            if running[0]:
                callback(fname)
    def stopper(wait_for_stop=True):
        running[0] = False
        if wait_for_stop:
            listener_thread.join()
    listener_thread = threading.Thread(target=threaded_listen)
    listener_thread.daemon = True
    listener_thread.start()
    return stopper
