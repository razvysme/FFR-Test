import pyaudio
import wave
import numpy as np
import json
import random
A
from jitter_data import generate_normal_values
from serial_comms import read_serial_data

################################
userID = 0
################################

#Loading METADATA
with open('Presets\pilot_experiment_debug.JSON', 'r') as json_file:
    metadata = json.load(json_file)
    gap = metadata["gap"]
    repetitions = metadata["repetitions"]
    audio_stimuli = metadata["audio_stimuli"]
    tactile_stimuli = metadata["tactile_stimuli"]
    output_filename_1 = f"Results\{userID}_{metadata['output_files']['channel_1']}"
    output_filename_2 = f"Results\{userID}_{metadata['output_files']['channel_2']}"
    record = metadata["record"]
      
print(f"Recording: {record}")

# Setup
fs = 44800  # Sample rate
chunk = 1024  
sample_format = pyaudio.paInt16  # 16-bit audio
channels = 2  # Stereo playback and recording
comport = "COM3"
baudrate = 115200

# Open the audio stimuli file
wf_audio = wave.open(audio_stimuli, 'rb')
wf_tactile = wave.open(tactile_stimuli, 'rb')

# Ensure both files have the same sample rate
if wf_audio.getframerate() != wf_tactile.getframerate():
    raise ValueError("Sample rates of the two files must match!")

# Calculate the total experiment length
num_frames_audio = wf_audio.getnframes()
file_length_seconds = num_frames_audio / wf_audio.getframerate()
gap_seconds = gap / 1000.0  # Convert gap from ms to seconds
total_recording_length = repetitions * (file_length_seconds + gap_seconds)
print(f"Experiment length is : {total_recording_length:.2f} seconds")


#THIS IS WHERE I*M AT
#touch_points = read_serial_data(port=comport, baudrate=baudrate)

#Jitter the gaps and save them for each iteration
gap_values = generate_normal_values(mean=25, lower_bound=15, upper_bound=35, size=1000)
gap_filename = f"Results\{userID}_gaps.txt"

# Save gap values to the text file
with open(gap_filename, 'w') as file:
    file.write(','.join(f"{gap:.2f}" for gap in gap_values))

print(f"Gap values saved in {gap_filename}")

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open stream for stereo output and input
stream = p.open(format=p.get_format_from_width(wf_audio.getsampwidth()),
                channels=2,  # Stereo output and input
                rate=wf_audio.getframerate(),
                output=True,
                input=True,
                frames_per_buffer=chunk)

# Prepare for recording
frames_channel_1 = []
frames_channel_2 = []

print("Playing audio and tactile stimuli, and recording...")

# Calculate the number of chunks per file
num_chunks_per_file = int(file_length_seconds * fs / chunk)

# Loop for the required number of repetitions
for rep in range(repetitions):
    print(f"Repetition {rep + 1} of {repetitions}")
    
    # Reset file pointers for each repetition
    wf_audio.rewind()
    wf_tactile.rewind()

    # Play each file completely in chunks
    for _ in range(num_chunks_per_file):
        # Read audio and tactile chunks
        data_audio = wf_audio.readframes(chunk)
        data_tactile = wf_tactile.readframes(chunk)

        # Convert byte data to numpy arrays
        audio_array = np.frombuffer(data_audio, dtype=np.int16)
        tactile_array = np.frombuffer(data_tactile, dtype=np.int16)

        # Pad with zeros if one file ends early
        if len(audio_array) < chunk:
            audio_array = np.pad(audio_array, (0, chunk - len(audio_array)))
        if len(tactile_array) < chunk:
            tactile_array = np.pad(tactile_array, (0, chunk - len(tactile_array)))

        # Interleave data for stereo playback
        stereo_data = np.column_stack((audio_array, tactile_array)).flatten()

        # Play interleaved data
        stream.write(stereo_data.tobytes())

        # Record audio
        recorded_data = stream.read(chunk)
        recorded_data_array = np.frombuffer(recorded_data, dtype=np.int16).reshape(-1, 2)

        # Separate into two channels
        channel1_data = recorded_data_array[:, 0]  # Channel 1
        channel2_data = recorded_data_array[:, 1]  # Channel 2

        # Store recorded data
        frames_channel_1.append(channel1_data.tobytes())
        frames_channel_2.append(channel2_data.tobytes())

    # Wait for the gap duration in seconds
    random_gap = random.choice(gap_values)  # Select a random value from gap_values

    # Convert the random gap from milliseconds to seconds
    gap_seconds = random_gap / 1000.0

    # Calculate the number of samples for the gap
    gap_samples = int(gap_seconds * fs * channels)  # Gap length in stereo

    # Use gap_samples to introduce the gap in your loop
    stream.write(np.zeros(gap_samples, dtype=np.int16).tobytes())

print("Done playing and recording.")

# Stop and close the stream
stream.stop_stream()
stream.close()
p.terminate()

if record:
    # Save the recorded audio for channel 1
    wf_output_1 = wave.open(output_filename_1, 'wb')
    wf_output_1.setnchannels(1)  # Mono file for channel 1
    wf_output_1.setsampwidth(p.get_sample_size(sample_format))
    wf_output_1.setframerate(fs)
    wf_output_1.writeframes(b''.join(frames_channel_1))
    wf_output_1.close()
    print(f"Channel 1 recording saved as {output_filename_1}")

    # Save the recorded audio for channel 2
    wf_output_2 = wave.open(output_filename_2, 'wb')
    wf_output_2.setnchannels(1)  # Mono file for channel 2
    wf_output_2.setsampwidth(p.get_sample_size(sample_format))
    wf_output_2.setframerate(fs)
    wf_output_2.writeframes(b''.join(frames_channel_2))
    wf_output_2.close()
    print(f"Channel 2 recording saved as {output_filename_2}")
    