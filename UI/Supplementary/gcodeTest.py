import serial
import time
# Open the serial port
ser = serial.Serial('COM6', 115200, timeout=1)  # Replace 'COM3' with your actual COM port

# Wait for the Arduino to initialize
time.sleep(2)
# Send G-code command with newline character
gcode_command = b"G21G91G1X10Y10Z10F1000\r\n"  # Replace with your desired G-code command
ser.write(gcode_command)


# Close the serial port
ser.close()