import time
import json
PLATFORM = "ANDROID"
if PLATFORM == "ANDROID":
    import android
from gtts import gTTS

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.logger import Logger
import os
from prepare_card_names import prepare_card_names
import speech_recognition as sr
import platform
from app_io import play_audio, get_storage_path, init_platform, listen_in_background
from integrations import await_assemblyai_recognition
def read_key(secrets_fpath):
    with open(secrets_fpath, "r") as fi:
        key = fi.read()
    return key

Builder.load_string('''
<MainLayout>:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: 0.2
        Button:
            id: settings_button
            text: 'Settings'
            on_release: app.open_settings()
        Button:
            id: reload_button
            text: 'reload cards'
            on_release: app.reload_cards()
        ToggleButton:
            id: mute_button
            text: 'Microphone Muted'
            on_state: app.toggle_microphone(self.state)
            size_hint_x: 0.4
            background_color: 1, 0, 0, 1
    TextInput:
        id: log_label
        readonly: True
''')


class MainLayout(BoxLayout):
    pass


class SpeechRecognitionApp(App):
    def build(self):
        self.platform = init_platform()
        self.microphone_muted = True
        self.storage_path = get_storage_path()
        self.assemblyai_key = read_key(self.storage_path+"app/secrets/assemblyai_api_key.txt")
        self.listen_stopper = None
        print(f"storage path: {self.storage_path}")
        # prepare_card_names(path=self.storage_path)
        try:
            self.cardnames = self.load_cardnames()
        except FileNotFoundError:
            print("cardnames file not found, preparing one...")
            prepare_card_names(path=self.storage_path)
            self.cardnames = self.load_cardnames()

        self.recognizer = sr.Recognizer()
        if self.platform == "DESKTOP":
            self.microphone = sr.Microphone()

        layout = MainLayout()
        self.log_label = layout.ids.log_label

        return layout
    def load_cardnames(self):
        with open(f'{self.storage_path}data/cardnames.json', 'r') as file:
            return json.load(file)

    def check_for_cardname(self, text_in):
        start = time.time()
        for name in self.cardnames:
            if name in text_in:
                return self.cardnames[name]
        self.schedule_log(f"No match found in {time.time() - start}")
        return False

    def berate_match(self, card_name):
        self.schedule_stop_listening()
        fpath = self.storage_path+"temp/"
        if not os.path.exists(fpath):
            os.mkdir(fpath)
        message = f"You just said {card_name}"
        soundbite = gTTS(text=message, lang='en', slow=False)
        soundbite_path =f"{fpath}temp.mp3" 
        soundbite.save(soundbite_path)
        time.sleep(0.1)
        play_audio(soundbite_path)


    
    def handle_recognition_desktop(self, recognizer, audio):
        # replace this from master's version
        pass

    def toggle_microphone(self, state):
        mute_button = self.root.ids.mute_button
        if self.microphone_muted:
            self.microphone_muted = False
            mute_button.text = "Microphone Listening"
            mute_button.background_color = (0, 1, 0, 1)  # Red color
            self.start_listening()
        else:
            self.stop_listening()

    def handle_audio_chunk(self, filename):
        if self.microphone_muted:
            return
        text = await_assemblyai_recognition(filename, self.recognizer, self.assemblyai_key)
        try:
            self.schedule_log("I: " + text)
            card_match = self.check_for_cardname(text.lower())
            if card_match:
                self.schedule_log(f"Detected {card_match['name']}: {card_match['url']}")
                self.berate_match(card_match['name'])
        except sr.UnknownValueError:
            self.schedule_log("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            self.schedule_log("Could not request results from Speech Recognition service; {0}".format(e))
 
    def start_listening(self):
        if self.platform == "ANDROID":
            self.listen_stopper = listen_in_background(self.handle_audio_chunk)
            self.schedule_log("began listening")
        else:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
            self.recognizer_callback = self.recognizer.listen_in_background(self.microphone, self.handle_recognition)

    def schedule_stop_listening(self):
        Clock.schedule_once(lambda dt: self.stop_listening())
    def stop_listening(self):
        mute_button = self.root.ids.mute_button
        self.microphone_muted = True
        mute_button.text = "Microphone Muted"
        mute_button.background_color = (1, 0, 0, 1)  # Red color
        if self.listen_stopper is not None:
            self.listen_stopper()
            self.schedule_log("stopped listening")
            self.listen_stopper = None

    def on_stop(self):
        self.recognizer_callback(wait_for_stop=False)

    def schedule_log(self, message):
        Clock.schedule_once(lambda dt: self.log(message))

    def log(self, message):
        self.log_label.text += message + '\n'


    def build_config(self, config):
        config.setdefaults('Card Settings', {'filter_by_format': 'legacy'})

    def build_settings(self, settings):
        settings.add_json_panel('Card Settings', self.config, "settings.json")


    def reload_cards(self):
        VALID_FORMATS = ["legacy", "standard", "vintage", "commander", "pioneer", "modern"]
        format_filter = self.config.get("Card Settings", 'filter_by_format')
        if format_filter not in VALID_FORMATS:
            format_filter = None
        prepare_card_names(path=self.storage_path, format_filter=format_filter)
        self.cardnames = self.load_cardnames()
if __name__ == '__main__':
    print(f"system : {platform.system()}")
    print(f"machine : {platform.machine()}")

    SpeechRecognitionApp().run()