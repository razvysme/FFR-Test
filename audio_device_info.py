import pyaudio

p = pyaudio.PyAudio()

# List all audio devices
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']}")
    print(f"  Max input channels: {info['maxInputChannels']}")
    print(f"  Max output channels: {info['maxOutputChannels']}")
    
p.terminate()
