import wave
import matplotlib.pyplot as plt
import numpy as np

# read the .wav file
obj = wave.open("beat.wav", "rb")

# read all the parameters
sample_freq = obj.getframerate()
n_samples = obj.getnframes()
signal_wave = obj.readframes(-1)

obj.close()

# Calculate length of signal in seconds
t_audio = n_samples / sample_freq

print(t_audio)

# create a plot
signal_array = np.frombuffer(signal_wave, dtype=np.int32)

times = np.linspace(0, t_audio, num=n_samples)

plt.figure(figsize=(15, 5))
plt.plot(times, signal_array)
plt.title("Audio Signal")
plt.ylabel("Signal Wave")
plt.xlabel("Time (s)")
plt.xlim(0, t_audio)
plt.show()