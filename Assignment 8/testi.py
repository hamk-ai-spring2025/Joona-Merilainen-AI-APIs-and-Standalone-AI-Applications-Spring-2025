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
