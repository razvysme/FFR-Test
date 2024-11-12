import serial

def read_serial_data(port='COM3', baudrate=9600):
    """
    Read and parse serial data from an Arduino sending an array of 8 integers.
    
    Parameters:
    - port (str): The serial port to connect to (e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux).
    - baudrate (int): The baud rate for the serial connection.
    
    Returns:
    - list[int]: A list of integers received from the Arduino.
    """
    # Open the serial connection
    ser = serial.Serial(port, baudrate, timeout=1)
    
    try:
        while True:
            # Read a line of data from the serial port
            line = ser.readline().decode('utf-8').strip()
            
            if line:
                # Split the comma-separated values and convert them to integers
                data = list(map(int, line.split(',')))
                print(f"Received: {data}")
    except KeyboardInterrupt:
        print("Stopping serial read.")
    finally:
        ser.close()

