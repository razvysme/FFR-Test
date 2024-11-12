import pyaudio
import wave
import numpy as np

# File paths
audio_stimuli = 'Stimuli/Flute208Hz_Mono_Wah.wav'
tactile_stimuli = 'Stimuli/Flute208Hz_Mono.wav'


# Set chunk size and parameters
chunk = 1024  

# Open the audio stimuli file
wf_audio = wave.open(audio_stimuli, 'rb')
wf_tactile = wave.open(tactile_stimuli, 'rb')

# Ensure both files have the same sample rate
if wf_audio.getframerate() != wf_tactile.getframerate():
    raise ValueError("Sample rates of the two files must match!")

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open stream for stereo output
stream = p.open(format=p.get_format_from_width(wf_audio.getsampwidth()),
                channels=2,  # Stereo output
                rate=wf_audio.getframerate(),
                output=True)

# Play signals simultaneously
print("Playing audio and tactile stimuli...")

data_audio = wf_audio.readframes(chunk)
data_tactile = wf_tactile.readframes(chunk)

while data_audio or data_tactile:
    # Convert byte data to numpy arrays
    audio_array = np.frombuffer(data_audio, dtype=np.int16)
    tactile_array = np.frombuffer(data_tactile, dtype=np.int16)

    # Handle end of file cases by padding with zeros
    if len(audio_array) < chunk:
        audio_array = np.pad(audio_array, (0, chunk - len(audio_array)))
    if len(tactile_array) < chunk:
        tactile_array = np.pad(tactile_array, (0, chunk - len(tactile_array)))

    # Interleave the data: Channel 1 from audio, Channel 2 from tactile
    stereo_data = np.column_stack((audio_array, tactile_array)).flatten()

    # Write interleaved data to stream
    stream.write(stereo_data.tobytes())

    # Read next frames
    data_audio = wf_audio.readframes(chunk)
    data_tactile = wf_tactile.readframes(chunk)

print("Done playing.")

# Close streams and PyAudio
stream.stop_stream()
stream.close()
p.terminate()

# Close WAV files
wf_audio.close()
wf_tactile.close()
