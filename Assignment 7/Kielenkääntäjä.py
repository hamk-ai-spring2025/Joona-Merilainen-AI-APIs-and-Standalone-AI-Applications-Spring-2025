from openai import OpenAI
from pathlib import Path
import time
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

def aanittaja():
    sekunnit = int(input("Kuinka monta sekuntia haluat nauhoittaa puhetta? "))
    kieli = str(input("Mille kielelle haluat kääntää tiedoston? "))

    start = aloita_ajastus()

    chunk = 1024
    sample_format = pyaudio.paInt16  
    channels = 2
    fs = 44100  
    seconds = sekunnit
    filename = "output.wav"

    p = pyaudio.PyAudio()  

    print('Nauhoitus aloitettu')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  
    
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

  
    stream.stop_stream()
    stream.close()
    
    p.terminate()

    print('Nauhoitus lopetettu')

    
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    tekstittaja(kieli,start)            
    
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
    
    response = client.responses.create(
        model="gpt-4o",
       input=f"Käännä seuraava teksti kielelle {kieli}: \"{teksti}\""
    )
    print(f"Tiedoston  käännetty tekstivastike kielellä {kieli}:")
    print(response.output_text)
    kaannos = response.output_text
    puhegeneraattori(kaannos,start)

def puhegeneraattori(kaannos,start):
    speech_file_path = Path(__file__).parent / "translated.mp3"
    print("\nLähetetään generoitavaksi!")
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=f"{kaannos}",
        instructions="Speak in a cheerful and positive tone.",
    ) as response:
        response.stream_to_file(speech_file_path)
    print("Teksti on generoitu puheeksi")
    print(f"Toistetaan käännös!")

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
        jatketaanko = input("Jatkatko ohjelman käyttöä? (k) kyllä ja (e) ei: ")
        if jatketaanko.lower() != "k":
            print("Ohjelma lopetetaan, kiitos käytöstä!")
            break


main()
