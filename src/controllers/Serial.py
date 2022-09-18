import serial


class Serial:
    def __init__(self):
        self.serial = None
        self.connected = False
        self.port = None
        self.speed = None
        self.databits = None
        self.stopbits = None
        self.parity = None
        self.timeout = 1
        pass

    @staticmethod
    def parse(message: str) -> bytearray:
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
        return self.serial.write(tx_data)

    def receive_test_match(self, rx_match: bytearray, timeout: float, size=None) -> int:
        # Define a timeout period so we don't get stuck here
        self.serial.timeout = timeout

        # Clear the buffer and start fresh
        self.serial.reset_input_buffer()
        if __debug__:
            print(f"RX data to match is: {bytes(rx_match)}")

        # Data should already be parsed and ready to go here
        rx_data = self.serial.read_until(expected=bytes(rx_match), size=size)
        if __debug__:
            print(f"RX data received is: {bytes(rx_data)}")

        # Return -1 if no match, location of string start if match (0 or greater)
        rx_string = bytes(rx_data)
        return rx_string.find(bytes(rx_match))
