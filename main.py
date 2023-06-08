import time
import json
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
from gtts import gTTS

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock


from prepare_card_names import prepare_card_names

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
            text: 'Microphone Listening'
            on_state: app.toggle_microphone(self.state)
            size_hint_x: 0.4
            background_color: 0, 1, 0, 1
    TextInput:
        id: log_label
        readonly: True
''')

class MainLayout(BoxLayout):
    pass


class SpeechRecognitionApp(App):
    def build(self):
        prepare_card_names()
        self.microphone_muted = False
        self.cardnames = self.load_cardnames()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognizer_callback = None
        self.start_listening()

        layout = MainLayout()
        self.log_label = layout.ids.log_label

        return layout
    def load_cardnames(self):
        with open('data/cardnames.json', 'r') as file:
            return json.load(file)

    def check_for_cardname(self, text_in):
        start = time.time()
        for name in self.cardnames:
            if name in text_in:
                return self.cardnames[name]
        self.schedule_log(f"No match found in {time.time() - start}")
        return False

    def berate_match(self, card_name):
        message = f"You just said {card_name}"
        soundbite = gTTS(text=message, lang='en', slow=False)
        soundbite.save("temp/temp.mp3")
        time.sleep(0.1)
        voiceover = AudioSegment.from_mp3("temp/temp.mp3")
        play(voiceover)

    def handle_recognition(self, recognizer, audio):
        if self.microphone_muted:
            return
        try:
            text = recognizer.recognize_google(audio)
            self.schedule_log("I: " + text)
            card_match = self.check_for_cardname(text.lower())
            if card_match:
                self.schedule_log(f"Detected {card_match['name']}: {card_match['url']}")
                self.berate_match(card_match['name'])
        except sr.UnknownValueError:
            self.schedule_log("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            self.schedule_log("Could not request results from Google Speech Recognition service; {0}".format(e))
        except Exception as e:
            self.schedule_log(f"Hit: {e}")

    def toggle_microphone(self, state):
        mute_button = self.root.ids.mute_button
        if state == 'down':
            self.microphone_muted = True
            mute_button.text = "Microphone Muted"
            mute_button.background_color = (1, 0, 0, 1)  # Red color
        else:
            self.microphone_muted = False
            mute_button.text = "Microphone Listening"
            mute_button.background_color = (0, 1, 0, 1)  # Red color

    def start_listening(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        self.recognizer_callback = self.recognizer.listen_in_background(self.microphone, self.handle_recognition)

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
        prepare_card_names(format_filter=format_filter)
        self.cardnames = self.load_cardnames()
import os
if __name__ == '__main__':
    if not os.path.exists('data'):
        os.mkdir('data')
    SpeechRecognitionApp().run()