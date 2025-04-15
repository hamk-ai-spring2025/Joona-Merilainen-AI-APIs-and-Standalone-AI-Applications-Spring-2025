from openai import OpenAI
from pathlib import Path
import keyboard
import pyaudio
import wave
import time
import sys
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame

client = OpenAI()

keskustelu = [
    {
        "role": "system",
        "content": (
            "You are a friendly and interactive English teacher who helps students improve their spoken English. "
            "Keep your messages short and engaging. Use simple language. "
            "Ask the student questions to keep the conversation going and give them chances to speak. "
            "Correct mistakes gently and clearly, but don't over-explain. "
            "Use examples when helpful, but focus on getting the student to talk more. "
            "Prioritize natural, everyday spoken English. "
            "Your tone is friendly, casual, and supportive — like a teacher who's excited to help."
        )
    }
]

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
FILENAME = "output.wav"

def lopeta():
    print("Ohjelma lopetetaan!")
    return False

def clear_last_line():
    # Siirtyy rivin alkuun, tyhjentää ja palaa alkuun
    sys.stdout.write('\r' + ' ' * 100 + '\r')
    sys.stdout.flush()


def aloita_ajastus():
    return time.time()


def lopeta_ajastus():
    return time.time()


def laske_viive(alku, loppu):
    viive = loppu - alku
    print(f"Viive: {viive:.2f} sekuntia")




def aanittaja():
    print("Press 'a' to start recording, 's' to stop, and 'x' to exit the program.")



    while True:
        event = keyboard.read_event()

        if keyboard.is_pressed('x'):
            lopeta()
        if event.event_type == keyboard.KEY_DOWN and event.name == 'a':
            break

    print("Record is starting...")
    time.sleep(0.3)

    start = time.time()
    frames = []

    p = pyaudio.PyAudio()
    stream = None

    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        time.sleep(0.2)
        print("Microphone ready, speak now!")

        while True:
            if keyboard.is_pressed('s'):
                print("Recording stopped.")
                time.sleep(0.3)
                break

            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

    except Exception as e:
        print(f"An error occurred during recording: {e}")

    finally:
        if stream is not None:
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
        if p is not None:
            try:
                p.terminate()
            except Exception:
                pass

    end = time.time()
    duration = end - start

    if duration < 0.5:
        print("The recording was too short. Please try again.")
        return

    with wave.open(FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    #print(f"✅ Tiedosto tallennettu: {FILENAME} ({duration:.2f} s)")
    tekstittaja("english", start)




def tekstittaja(kieli, start):
    with open("output.wav", "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file
        )
    print("You said:")
    print(transcription.text)
    teksti = transcription.text
    kaantaja(teksti, kieli, start)


def kaantaja(teksti, kieli, start):
    global keskustelu

    keskustelu.append({"role": "user", "content": teksti})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=keskustelu
    )

    reply = response.choices[0].message.content
    keskustelu.append({"role": "assistant", "content": reply})
    print("Teacher's answer")
    print(reply)
    puhegeneraattori(reply, start)


def puhegeneraattori(kaannos, start):
    speech_file_path = Path(__file__).parent / "translated.mp3"

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=kaannos,
        instructions="Speak in a cheerful and positive tone.",
    ) as response:
        response.stream_to_file(speech_file_path)

    pygame.mixer.init()
    pygame.mixer.music.load(str(speech_file_path))
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.music.unload()

    end = lopeta_ajastus()
    #laske_viive(start, end)


def main():
    print("Welcome to speech practice.")
    while True:
        aanittaja()


if __name__ == "__main__":
    main()
