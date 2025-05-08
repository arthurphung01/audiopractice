import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import time
import threading
import queue


def calculate_decibels(audio_data, sample_rate):
    """Calculates the decibels from the audio data.

    Args:
        audio_data (numpy.ndarray): Audio data array.
        sample_rate (int): The sampling rate of the audio data.

    Returns:
        float: The calculated decibels (dB).  Returns -100 if the amplitude is zero.
    """
    p_ref = 20e-6
    amplitude = np.sqrt(np.mean(audio_data**2))
    if amplitude == 0:
        return -100
    decibels = 20 * np.log10(amplitude /p_ref)
    return decibels


def audio_recorder(sample_rate, chunk_size, stop_event, decibel_queue, waveform_queue):
    """Records audio data from the microphone and calculates decibels.

    Args:
        sample_rate (int): The sampling rate.
        chunk_size (int): The size of the audio chunks to process.
        stop_event (threading.Event): An event to signal when to stop recording.
        decibel_queue (queue.Queue): A queue to send decibel values to the main thread.
        waveform_queue (queue.Queue): A queue to send waveform data to the main thread.
    """
    try:
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Error in audio stream: {status}")
                return

            decibels = calculate_decibels(indata, sample_rate)
            try:
                decibel_queue.put(decibels, block=False)
            except queue.Full:
                pass  # Optionally log: print("Decibel queue full")

            try:
                waveform_queue.put(indata.copy(), block=False)
            except queue.Full:
                pass  # Optionally log: print("Waveform queue full")

        with sd.InputStream(callback=audio_callback, samplerate=sample_rate, channels=1, blocksize=chunk_size):
            while not stop_event.is_set():
                time.sleep(0.1)  # Adjust for responsiveness
    except Exception as e:
        print(f"An error occurred during recording: {e}")

def create_live_plot(sample_rate, chunk_size):
    """Creates a live waveform plot using Matplotlib.

    Args:
        sample_rate (int): The sampling rate of the audio.
        chunk_size (int): The size of the audio chunks.
    """
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))  # Two subplots: waveform and decibels

    # Waveform plot setup
    ax1.set_xlim(0, chunk_size)
    ax1.set_ylim(-1, 1)
    line, = ax1.plot([], [], color='cyan', linewidth=1)
    ax1.set_xlabel("Sample")
    ax1.set_ylabel("Amplitude")
    ax1.set_title("Audio Waveform")
    ax1.grid(True)

    # Decibel plot setup
    ax2.set_xlim(0, 5)  # Show last 5 seconds of decibels
    ax2.set_ylim(0, 100)  # Adjust y-axis as needed for typical dB range
    decibel_line, = ax2.plot([], [], color='magenta', linewidth=2)
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Decibels (dB)")
    ax2.set_title("Decibel Level")
    ax2.grid(True)
    time_data = []
    decibel_data = []

    plt.ion()  # Turn on interactive mode for live updates

    stop_event = threading.Event()
    decibel_queue = queue.Queue(maxsize=10)
    waveform_queue = queue.Queue(maxsize=30)
    audio_thread = threading.Thread(
        target=audio_recorder,
        args=(sample_rate, chunk_size, stop_event, decibel_queue, waveform_queue),
        daemon=True  # Ensure thread exits when main thread exits
    )
    audio_thread.start()

    start_time = time.time() # Keep track of the starting time
    SMOOTHING_FACTOR = 0.7  # Exponential smoothing factor
    smoothed_decibels = 0

    def update_plot():
        """Updates the Matplotlib plot with new data from the queues."""
        nonlocal time_data, decibel_data, start_time, smoothed_decibels  # Access the non-local variables

        while True:
            if not waveform_queue.empty():
                try:
                    audio_data = waveform_queue.get(block=False)
                    data_normalized = audio_data / np.max(np.abs(audio_data)) if audio_data.size else np.array([])
                    line.set_data(np.arange(len(data_normalized)), data_normalized)
                    fig.canvas.draw()
                    fig.canvas.flush_events()
                except queue.Empty:
                    pass

            if not decibel_queue.empty():
                try:
                    decibels = decibel_queue.get(block=False)
                    smoothed_decibels = (SMOOTHING_FACTOR * smoothed_decibels) + ((1 - SMOOTHING_FACTOR) * decibels) #exponential smoothing
                    current_time = time.time() - start_time
                    time_data.append(current_time)
                    decibel_data.append(smoothed_decibels) #use smoothed value

                    time_data = time_data[-50:]
                    decibel_data = decibel_data[-50:]

                    decibel_line.set_data(time_data, decibel_data)
                    ax2.set_xlim(time_data[0] if time_data else 0, time_data[-1] if time_data else 5)
                    ax2.set_ylim(0, 100) #keep y axis consistent
                    fig.canvas.draw()
                    fig.canvas.flush_events()
                except queue.Empty:
                    pass
            time.sleep(0.01) # Adjust for udpate rate

    # Create a separate thread for updating the plot
    plot_thread = threading.Thread(target=update_plot, daemon=True)
    plot_thread.start()

    try:
        plt.show(block=True)  # Keep the plot window open until interrupted
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
        stop_event.set()  # Signal the audio thread to stop
        audio_thread.join()  # Wait for the audio thread to finish
        plot_thread.join() # Wait for plot thread to finish
        plt.close()

if __name__ == "__main__":
    sample_rate = 44100
    chunk_size = 2048
    create_live_plot(sample_rate, chunk_size)
