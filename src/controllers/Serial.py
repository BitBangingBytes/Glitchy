import serial
import time
from threading import Thread


class Serial:
    def __init__(self):
        self.serial = None
        self.connected = False
        self.port = None
        self.speed = None
        self.databits = None
        self.stopbits = None
        self.parity = None
        self.rx_data = None
        self.stop_read = False

    @staticmethod
    def parse_string(message: str) -> bytearray:
        """ Takes a string, parses it for hex and strings and returns a bytearray

            Hex data and strings can be mixed and entered like this:
            Input String:       $31 $32 $33 $20 "four five six." $0D $0A
            Output Byte Array:  "123 four five six." <CR> <LF>
        """
        byte_array = bytearray()
        if message != "":
            i = 0
            while i < len(message):
                if message[i] == "$":  # Caught Hex value
                    hex_str = message[i + 1:i + 3]
                    byte_array.append(int(hex_str, base=16))
                    i = i + 2
                elif message[i] == '"':  # Caught String
                    inside_string = True
                    i = i + 1  # Move to next character
                    while inside_string:  # and (i < len(tx_string)):
                        if i == len(message):
                            return byte_array  # String composition error, return what we have
                        if (i + 1 < len(message)) and (message[i] == '"') and (message[i + 1] == '"'):
                            byte_array.append(0x22)  # Add a single " since we caught "" in the string
                            i = i + 2
                        elif message[i] == '"':  # End of string
                            i = i + 1
                            inside_string = False
                        else:
                            byte_array.append(ord(message[i]))
                            i = i + 1
                else:
                    i = i + 1

            return byte_array
        else:
            return bytearray(0)

    @staticmethod
    def parse_bytearray(data: bytearray) -> str:
        parsed_message = ""
        previous_string = False
        for i in data:
            if i < 32 or i > 126:
                # Parse as raw hex character
                if previous_string:
                    parsed_message += '" '
                parsed_message += "${:02x} ".format(i).upper()
                previous_string = False
            else:
                # Parse as string
                if previous_string:
                    parsed_message += f"{chr(i)}"
                else:
                    parsed_message += f'"{chr(i)}'
                previous_string = True
        if previous_string:
            parsed_message += '"'
        return parsed_message

    def connect(self, port, baudrate, bytesize, stopbits, parity, timeout):
        try:
            self.serial = serial.Serial(port=port, baudrate=int(baudrate),
                                        bytesize=int(bytesize), stopbits=int(stopbits),
                                        parity=parity, timeout=timeout)
            self.connected = True
            return True
        except serial.SerialException as err:
            if __debug__:
                print(err)
            self.connected = False
            return False

    def disconnect(self):
        self.serial.close()
        self.connected = False
        return True

    def send(self, tx_data: bytearray):
        # Return the number of bytes sent
        self.serial.reset_output_buffer()
        nbytes = self.serial.write(tx_data)
        return nbytes

    def receive(self, timeout: float = None, size: int = None) -> bytearray:
        def receive_loop():
            timeout_val = time.time() + timeout
            while True:
                if self.serial.in_waiting > 0:
                    # read the bytes and convert from binary array to ASCII
                    self.rx_data += self.serial.read(self.serial.in_waiting)
                time.sleep(0.01)
                if time.time() > timeout_val:
                    break
                if self.stop_read:
                    self.stop_read = False
                    break

        self.rx_data = bytearray()
        # Define a timeout period so we don't get stuck here
        self.serial.timeout = timeout
        # Clear the buffer and start fresh
        self.serial.reset_input_buffer()
        # Old method using read_until which returns immediately on data match, freezes app while running
        # rx_data = self.serial.read_until(expected=bytes(rx_match), size=size)

        # New method which also freezes the app but receives data the whole time specified regardless of a match
        receive_loop()
        return self.rx_data
