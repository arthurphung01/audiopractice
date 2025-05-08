import sounddevice as sd
import numpy as np

def print_audio_data(indata, frames, time, status):
    if status:
        print("Error:", status)
        return
    max_amplitude = np.max(np.abs(indata))
    print(f"Max amplitude: {max_amplitude:.4f}, Shape: {indata.shape}")

try:
    with sd.InputStream(callback=print_audio_data, channels=1, dtype='float32'):
        input("Press Enter to stop recording and check audio data...")
except Exception as e:
    print(f"Error: {e}")