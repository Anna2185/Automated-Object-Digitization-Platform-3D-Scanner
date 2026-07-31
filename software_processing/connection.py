#Copyright © 2026 AM G. All rights reserved.
#Published strictly for portfolio demonstration. See README.md for details.

import serial
import serial.tools.list_ports
import time


def find_port():
    """
    Find the arduino port by listing available serial ports and prompting user selection

    Args: None

    Returns: 
        str: The selected port name (e.g., 'COM3' or '/dev/ttyUSB0')
    """
    #list available serial ports and prompt user port selection
    ports = serial.tools.list_ports.comports()
    print("\nAvailable serial devices:\n")

    #print all the ports with their index, port/device name and description
    for i, port in enumerate(ports):
        print(f"[{i}] " f"{port.device} - "f"{port.description}")
    if not ports:
        return None

    #loop until a valid selection is made
    while True:
        try:
            choice = int(
                input("\nEnter the number corresponding to your Arduino: ")
            )

            #check if the choice is valid
            if 0 <= choice < len(ports):
                selected = ports[choice]
                print(f"\nSelected: " f"{selected.device}")
                return selected.device

            print("Invalid selection.")

        except ValueError:
            print("Please enter a valid number")


def connect(port, baud_rate):
    """
    Open a serial connection to the Arduino and return the serial object
    
    Args:
        port (str): The serial port to connect to (e.g., 'COM3' or '/dev/ttyUSB0')
        baud_rate (int): The baud rate for the serial connection
        
    Returns:
            serial.Serial: The serial connection object
    """
    ser = serial.Serial(port, baud_rate, timeout=1)

    #time for the serial connection to establish
    time.sleep(2)

    #print the connected port
    print("\nConnected to:", port)

    #clear old serial data if any
    ser.reset_input_buffer()

    return ser
