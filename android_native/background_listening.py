#!/usr/bin/env python3

import time
import json
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play

from gtts import gTTS
print("imports")

with open('data/cardnames.json', 'r') as fi:
    cardnames = json.load(fi)

def check_for_cardname(text_in):
    start = time.time()
    for name in cardnames:
        if name in text_in:
            return cardnames[name]
    print(f"no match found in {time.time()-start}")
    return False

def berate_match(card_name):
    message = f"You just said {card_name}"
    soundbite = gTTS(text=message, lang='en', slow=False)
    soundbite.save("temp/temp.mp3")
    time.sleep(0.1)
    voiceover = AudioSegment.from_mp3("temp/temp.mp3")
    play(voiceover)

def callback(recognizer, audio):
    print("entered callback")
    try:
        text = recognizer.recognize_google(audio)
        print("I: " + text)
        card_match = check_for_cardname(text.lower())
        if card_match:
            print(f"detected {card_match['name']} : {card_match['url']}")
            berate_match(card_match['name'])
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    except Exception as e:
        print(f"hit: {e}")

r = sr.Recognizer()
m = sr.Microphone()

with m as source:
    r.adjust_for_ambient_noise(source) 
stop_listening = r.listen_in_background(m, callback)


print("ready to listen:")
while True: time.sleep(0.1)  