import pyaudio
import wave
import numpy as np
import json
import random
import threading
import sys
import os
from jitter_data import generate_normal_values
from serial_comms import read_serial_data
from gui import initialize_gui, update_sprites

################################
userID = 0
# Check if a user ID argument was passed
if len(sys.argv) > 1:
    try:
        userID = int(sys.argv[1])  # Convert the argument to an integer
        print(f"User ID set to: {userID}")
    except ValueError:
        print("Invalid user ID. Please provide a numeric value.")
        sys.exit(1)
################################

# Load METADATA
with open('Presets/pilot_experiment_debug.JSON', 'r') as json_file:
    metadata = json.load(json_file)
    gap = metadata["gap"]
    repetitions = metadata["repetitions"]
    batches = metadata["batches"]
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
playback_done = threading.Event()
tactile_amplitudes = [0, 0.5, 1]

pinky_finger = 1
ring_finger = 5
middle_finger = 3
index_finger = 6
thumb = 2
upper_palm = 0
lower_palm = 4

# Jitter the gaps and save them for each iteration
gap_values = generate_normal_values(mean=25, lower_bound=15, upper_bound=35, size=1000)

def get_unique_filename(base_filename):
    """Check if a file exists and append '!' to the name if it does."""
    filename, extension = os.path.splitext(base_filename)
    
    # Keep appending '!' until the filename is unique
    while os.path.exists(base_filename):
        filename += "!"  # Append '!' to the filename
        base_filename = f"{filename}{extension}"
    
    return base_filename

# Create and save the jittered gap length file with unique name - redundancy if i forget to set the name correctly
gap_filename_temp = f"Results/{userID}_gaps.txt"
gap_filename = get_unique_filename(gap_filename_temp)
with open(gap_filename, 'w') as file:
    file.write(','.join(f"{gap:.2f}" for gap in gap_values))
print(f"Gap values saved in {gap_filename}")

# Create a touch log file witch unique name(if i'm silly and forget to set the correct participant name)
touch_log_filename_temp = f"Results/{userID}_touch_log.txt"
touch_log_filename = get_unique_filename(touch_log_filename_temp)

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
    # print(f"Updated sensors array: {sensors_used}")
  
 # create order of conditions   
def create_conditions_order(num_reps=repetitions, condition=tactile_amplitudes):
    reps_per_case = int(num_reps // len(condition))
    reps_per_case = reps_per_case // 3 #this is some weird hack that makes it work. No idea why if i divide in the line above i get 10
    #print(reps_per_case)
    # Randomize the order of condition
    randomized_condition = random.sample(condition, len(condition))
    
    # Create the order list based on the randomized case order
    order = []
    for case in randomized_condition:
        order.extend([case] * reps_per_case)
    #print(order)
    return order

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

    for i in range(len(tactile_amplitudes)):
        print(f"Starting batch: {i}")  
        order = create_conditions_order()
 
        for rep in range(len(order)):
            #print(f"Repetition {rep + 1} of {len(order)} with amplitude {order[rep]}")
            wf_audio.rewind()
            wf_tactile.rewind()

            for _ in range(int(file_length_seconds * fs / chunk)):
                data_audio = wf_audio.readframes(chunk)
                data_tactile = wf_tactile.readframes(chunk)
                
                # Convert data to NumPy arrays
                audio_array = np.frombuffer(data_audio, dtype=np.int16)
                tactile_array = np.frombuffer(data_tactile, dtype=np.int16)

                # Scale tactile channel
                tactile_array = (tactile_array * order[rep]).astype(np.int16)
                # Combine audio and scaled tactile into stereo        
                stereo_data = np.column_stack((
                                audio_array,
                                tactile_array  # Use the scaled tactile_array here
                            )).flatten()
                
                # Update and Log sensors_used values before writing to stream
                update_sensors(sensors)  
                with open(touch_log_filename, 'a') as log_file:
                    log_file.write(f"{sensors_used}\n")

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
                  
    playback_done.set()

def sensor_thread():
    """Thread for handling serial communication and updating sensors."""
    read_serial_data(comport, baudrate, callback=update_sensors)

# Main thread: Start GUI
root, sprite_ids = initialize_gui(sensors_used)

def periodic_update():
    if playback_done.is_set():  # Check if playback is done
        print("Playback complete. Closing application.")
        on_closing()  # Close the GUI
    elif root.winfo_exists():  # Continue updating if window exists
        update_sprites(sensors_used, sprite_ids)
        root.after(30, periodic_update)

        
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