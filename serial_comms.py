import serial

def read_serial_data(port='COM7', baudrate=115200, interval=50, callback=None):
    """
    Reads serial data and passes the parsed sensor values to a callback function.
    
    Parameters:
    - port (str): Serial port to which the Arduino is connected.
    - baudrate (int): Baud rate of the serial connection.
    - interval (int): Timeout interval in milliseconds.
    - callback (function): A function to handle the sensor data.
    """
    ser = serial.Serial(port, baudrate, timeout=interval / 1000)

    try:
        while True:
            data = ser.readline().decode().strip()
            if data:
                # Ignore non-numeric lines
                if "mpr121 init OK!" not in data:
                    sensors = list(map(int, data.split(',')))
                    if callback:
                        callback(sensors)
    except KeyboardInterrupt:
        print("Stopping serial read.")
    finally:
        ser.close()
