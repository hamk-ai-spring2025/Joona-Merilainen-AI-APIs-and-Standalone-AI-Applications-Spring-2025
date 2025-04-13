from openai import OpenAI
from pathlib import Path
from pynput import keyboard as pynput_keyboard
import time
import keyboard
import pyaudio
import wave
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"  # Tämä estää viestin

import pygame  # Nyt viesti ei näy


client = OpenAI()

def aloita_ajastus():
    return time.time()

def lopeta_ajastus():
    return time.time()

def laske_viive(alku, loppu):
    viive = loppu - alku
    print(f"Viive: {viive:.2f} sekuntia")

from pynput import keyboard as pynput_keyboard

def aanittaja():
    import pyaudio
    import wave
    from pynput import keyboard
    import threading

    # Äänityksen asetukset
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    FILENAME = "output.wav"
    start = aloita_ajastus()

    # Tilamuuttujat
    start_recording = threading.Event()
    stop_recording = threading.Event()

    def on_press(key):
        try:
            if key.char == 'a':
                start_recording.set()
                print("🎙️ Nauhoitus käynnistyy...")
            elif key.char == 's':
                stop_recording.set()
                print("🛑 Nauhoitus pysäytetty.")
                return False  # Pysäyttää näppäinkuuntelijan
        except AttributeError:
            pass

    def record_audio():
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []

        print("Paina 'a' aloittaaksesi ja 's' lopettaaksesi nauhoituksen.")

        # Kuuntele näppäimiä säikeessä
        listener = keyboard.Listener(on_press=on_press)
        listener.start()

        # Odota että käyttäjä painaa 'a'
        start_recording.wait()

        while not stop_recording.is_set():
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Tallenna tiedosto
        wf = wave.open(FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        print("✅ Tiedosto tallennettu: output.wav")

    # Käynnistä
    record_audio()

    kieli = "english"
    tekstittaja(kieli, start)
           
    
def tekstittaja(kieli,start):
    with open("output.wav", "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-transcribe", 
            file=audio_file
        )
    print("Tiedoston tekstivastike:")
    print(transcription.text)
    teksti = transcription.text
    kaantaja(teksti, kieli,start)
    
def kaantaja(teksti, kieli,start):

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a friendly and interactive English teacher who helps students improve their spoken English."
                    "Keep your messages short and engaging. Use simple language."
                    "Ask the student questions to keep the conversation going and give them chances to speak."
                    "Correct mistakes gently and clearly, but don't over-explain."
                    "Use examples when helpful, but focus on getting the student to talk more."
                    "Prioritize natural, everyday spoken English."
                    "Your tone is friendly, casual, and supportive — like a teacher who's excited to help."
                )
            },
            {
                "role": "user",
                "content": f"{teksti}"
            }
        ]
    )

    print(response.choices[0].message.content)


    kaannos = response.choices[0].message.content
    puhegeneraattori(kaannos,start)

def puhegeneraattori(kaannos,start):
    speech_file_path = Path(__file__).parent / "translated.mp3"
    #print("\nLähetetään generoitavaksi!")
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=f"{kaannos}",
        instructions="Speak in a cheerful and positive tone.",
    ) as response:
        response.stream_to_file(speech_file_path)
    #print("Teksti on generoitu puheeksi")
    #print(f"Toistetaan käännös!")

    pygame.mixer.init()
    pygame.mixer.music.load("translated.mp3")
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    end = lopeta_ajastus()
    laske_viive(start, end)


def main():
    print("Kielenkääntäjä")
    while True:
        aanittaja()
        #jatketaanko = input("Jatkatko ohjelman käyttöä? (k) kyllä ja (e) ei: ")
        #if jatketaanko.lower() != "k":
         #   print("Ohjelma lopetetaan, kiitos käytöstä!")
          #  break


main()
