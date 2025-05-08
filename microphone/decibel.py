import sounddevice as sd
import numpy as np
import time

def calculate_decibels(audio_data, sample_rate):
    """
    Calculates the decibels from the audio data.

    Args:
        audio_data (numpy.ndarray): Audio data array.
        sample_rate (int): The sampling rate of the audio data.

    Returns:
        float: The calculated decibels (dB).  Returns -100 if the amplitude is zero.
    """
    # Avoid taking the log of zero.  Add a tiny value.
    p_ref = 20e-6
    amplitude = np.sqrt(np.mean(audio_data**2))
    if amplitude == 0:
        return -100  # Return a very low dB value for silence
    decibels = 20 * np.log10(amplitude / p_ref)
    return decibels

def decibel_reader(duration=5, sample_rate=44100, chunk_size=1024, delay=0.1):
    """
    Reads audio data from the microphone and calculates decibels.

    Args:
        duration (int, optional): The duration of the recording in seconds. Defaults to 5.
        sample_rate (int, optional): The sampling rate. Defaults to 44100.
        chunk_size (int, optional): The size of the audio chunks to process. Defaults to 1024.
        delay (float, optional):  Delay in seconds after each calculation. Defaults to 0.1
    """
    try:
        print("Starting decibel reader...")
        print(f"Duration: {duration} seconds")
        print(f"Sample Rate: {sample_rate} Hz")
        print(f"Chunk Size: {chunk_size}")

        # Function to process audio chunks
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Error in audio stream: {status}")
                return

            # Calculate decibels
            decibels = calculate_decibels(indata, sample_rate)
            print(f"Decibels: {decibels:.2f} dB")

            ## print("indata shape:", indata.shape)
            ## print("indata[0:20]:", indata[0:20])  # Print more values

        # Start the audio stream
        with sd.InputStream(callback=audio_callback, samplerate=sample_rate, channels=1, blocksize=chunk_size):
            time.sleep(duration)  # Keep the stream open for the specified duration

        print("Decibel reader stopped.")

    except Exception as e:
        print(f"An error occurred: {e}")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")

if __name__ == "__main__":
    # You can change the duration, sample rate, and chunk size here.
    decibel_reader(duration=10, sample_rate=44100, chunk_size=2048, delay=0.2)
