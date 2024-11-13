import pyaudio
import wave
import numpy as np
import json
import random
import threading
from jitter_data import generate_normal_values
from serial_comms import read_serial_data
from gui import initialize_gui, update_sprites

################################
userID = 0
################################

# Load METADATA
with open('Presets/pilot_experiment_debug.JSON', 'r') as json_file:
    metadata = json.load(json_file)
    gap = metadata["gap"]
    repetitions = metadata["repetitions"]
    audio_stimuli = metadata["audio_stimuli"]
    tactile_stimuli = metadata["tactile_stimuli"]
    output_filename_1 = f"Results/{userID}_{metadata['output_files']['channel_1']}"
    output_filename_2 = f"Results/{userID}_{metadata['output_files']['channel_2']}"
    record = metadata["record"]

print(f"Recording: {record}")

# Setup
fs = 44800  # Sample rate
chunk = 1024
sample_format = pyaudio.paInt16  # 16-bit audio
channels = 2  # Stereo playback and recording
comport = "COM7"
baudrate = 115200
sensors = [0] * 8  # The 8 capacitive sensors
sensors_used = [0] * 7  # Used for GUI updates

pinky_finger = 0
ring_finger = 1
middle_finger = 2
index_finger = 3
thumb = 4
upper_palm = 5
lower_palm = 6

# Jitter the gaps and save them for each iteration
gap_values = generate_normal_values(mean=25, lower_bound=15, upper_bound=35, size=1000)
gap_filename = f"Results/{userID}_gaps.txt"

with open(gap_filename, 'w') as file:
    file.write(','.join(f"{gap:.2f}" for gap in gap_values))

print(f"Gap values saved in {gap_filename}")

# Open the audio stimuli files
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

# Sensors reading callback
def update_sensors(new_values):
    global sensors, sensors_used
    sensors = new_values
    sensors_used = [sensors[pinky_finger], sensors[ring_finger], sensors[middle_finger],
                    sensors[index_finger], sensors[thumb], sensors[upper_palm], sensors[lower_palm]]
    print(f"Updated sensors array: {sensors_used}")

def audio_thread():
    """Thread for handling audio playback and recording."""
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf_audio.getsampwidth()),
                    channels=2,
                    rate=wf_audio.getframerate(),
                    output=True,
                    input=True,
                    frames_per_buffer=chunk)

    frames_channel_1 = []
    frames_channel_2 = []

    print("Playing audio and tactile stimuli, and recording...")

    for rep in range(repetitions):
        print(f"Repetition {rep + 1} of {repetitions}")
        wf_audio.rewind()
        wf_tactile.rewind()

        for _ in range(int(file_length_seconds * fs / chunk)):
            data_audio = wf_audio.readframes(chunk)
            data_tactile = wf_tactile.readframes(chunk)
            stereo_data = np.column_stack((
                np.frombuffer(data_audio, dtype=np.int16),
                np.frombuffer(data_tactile, dtype=np.int16)
            )).flatten()

            stream.write(stereo_data.tobytes())

            recorded_data = np.frombuffer(stream.read(chunk), dtype=np.int16).reshape(-1, 2)
            frames_channel_1.append(recorded_data[:, 0].tobytes())
            frames_channel_2.append(recorded_data[:, 1].tobytes())

        gap_samples = int((random.choice(gap_values) / 1000.0) * fs * channels)
        stream.write(np.zeros(gap_samples, dtype=np.int16).tobytes())

    print("Done playing and recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    if record:
        # Save recordings
        with wave.open(output_filename_1, 'wb') as wf1, wave.open(output_filename_2, 'wb') as wf2:
            for wf, frames in zip([wf1, wf2], [frames_channel_1, frames_channel_2]):
                wf.setnchannels(1)
                wf.setsampwidth(p.get_sample_size(sample_format))
                wf.setframerate(fs)
                wf.writeframes(b''.join(frames))

def sensor_thread():
    """Thread for handling serial communication and updating sensors."""
    read_serial_data(comport, baudrate, callback=update_sensors)

# Main thread: Start GUI
root, sprite_ids = initialize_gui(sensors_used)

def periodic_update():
    if root.winfo_exists():  # Only update if the root window exists
        update_sprites(sensors_used, sprite_ids)
        root.after(500, periodic_update)
        
def on_closing():
    """Handle cleanup when the window is closed."""
    print("Exiting application...")
    # Here you can add cleanup code if needed
    root.destroy()

# Attach the cleanup function to the window close event
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start GUI periodic updates
periodic_update()

# Start threads for audio and sensors
audio_t = threading.Thread(target=audio_thread, daemon=True)
sensor_t = threading.Thread(target=sensor_thread, daemon=True)
audio_t.start()
sensor_t.start()

# Start Tkinter event loop (main thread)
root.mainloop()
