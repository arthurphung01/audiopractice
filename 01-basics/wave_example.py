import wave

# rb is read binary
obj = wave.open("beat.wav", "rb")

print("Number of channels: ", obj.getnchannels())
print("Sample Width: ", obj.getsampwidth())
print("Frame rate: ", obj.getframerate())
print("Number of frames: ", obj.getnframes())
print("Parameters: ", obj.getparams())

# Calculate the time of the audio in seconds
t_audio = obj.getnframes() / obj.getframerate()
print(f"Time of .wav file is {t_audio} seconds")

# Calculate frames
frames = obj.readframes(-1)
print(type(frames), type(frames[0]))
print(len(frames))

obj.close()

# wb is write binary
obj_new = wave.open("beat_new.wav", "wb")

obj_new.setnchannels(2)
obj_new.setsampwidth(2)
obj_new.setframerate(44100.0)

obj_new.writeframes(frames)

obj_new.close()