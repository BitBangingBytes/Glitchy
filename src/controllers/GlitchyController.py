# -*- encoding:utf-8 -*-
import json
import time
import webbrowser
import sys
import logging

from controllers.ChipWhisperer import ChipWhisperer
from controllers.EnvoxBB3 import EnvoxBB3
from controllers.PowerSupply import PowerSupply
from controllers.Serial import Serial
from core.Controller import Controller
from models.GlitchyData import GlitchyDataModel

logger = logging.getLogger(__name__)
"""
    Main controller. It will be responsible for program's main screen behavior.
"""


class GlitchyController(Controller):
    # -----------------------------------------------------------------------
    #        Constructor
    # -----------------------------------------------------------------------
    def __init__(self):
        # Data model used to house current state of all variables
        self.glitchy_data = GlitchyDataModel()
        # Power supply specific parameters, loads driver for specific supply
        self.powersupply = PowerSupply(data_model=self.glitchy_data, supply_model=EnvoxBB3())
        # Serial port specific parameters
        self.serial = Serial()
        # Glitching specific parameters
        self.cw = ChipWhisperer()
        self.glitcher_running = False
        self.glitcher_pause = False
        self.glitcher_stop = False
        self.glitcher_success = False
        self.power_toggle_config = False  # Used for one-time config loading
        # Initial view (only view at this time) to load
        self.startupView = self.loadView("Startup")

    # -----------------------------------------------------------------------
    #        Methods
    # -----------------------------------------------------------------------
    """
        @Override
    """

    def main(self):
        logger.info("Starting Glitchy")
        self.startupView.main()

    def chipwhisperer_list_devices(self):
        return self.cw.list_devices()

    def chipwhisperer_connect(self):
        pass

    def chipwhisperer_disconnect(self):
        pass

    def automated_glitch(self):

        def clear_live_values():
            self.glitchy_data.set_parameter("glitchtime_currentvalue", None)
            self.glitchy_data.set_parameter("glitchstrength_currentvalue", None)
            self.glitchy_data.set_parameter("progressbar_time", 0)
            self.glitchy_data.set_parameter("progressbar_strength", 0)
            self.glitchy_data.set_parameter("progressbar_overall", 0)
            self.glitchy_data.set_parameter("glitchcounter_triggered", None)
            self.glitchy_data.set_parameter("glitchcounter_missed", None)

        def update_live_values():
            self.glitchy_data.set_parameter("glitchtime_currentvalue", glitchtime_currentvalue)
            self.glitchy_data.set_parameter("glitchstrength_currentvalue", glitchstrength_currentvalue)
            self.glitchy_data.set_parameter("progressbar_time", progressbar_time)
            self.glitchy_data.set_parameter("progressbar_strength", progressbar_strength)
            self.glitchy_data.set_parameter("progressbar_overall", progressbar_overall)
            self.glitchy_data.set_parameter("glitchcounter_triggered", glitchcounter_triggered)
            self.glitchy_data.set_parameter("glitchcounter_missed", glitchcounter_missed)

        def trigger_power(option):
            trigger_fudge_factor = 0.25
            if option == "Toggle CH1":
                if self.power_toggle_config:
                    self.powersupply.config_toggle_time(ch1=self.glitchy_data.get_parameter("powersupply_ch1_toggle"))
                    self.powersupply.set_toggle(channel="1")
                    self.power_toggle_config = False
                self.powersupply.trigger_toggle()
                time.sleep(float(self.glitchy_data.get_parameter("powersupply_ch1_toggle")) + trigger_fudge_factor)
            elif option == "Toggle CH2":
                if self.power_toggle_config:
                    self.powersupply.config_toggle_time(ch1=self.glitchy_data.get_parameter("powersupply_ch2_toggle"))
                    self.powersupply.set_toggle(channel="2")
                    self.power_toggle_config = False
                self.powersupply.trigger_toggle()
                time.sleep(float(self.glitchy_data.get_parameter("powersupply_ch2_toggle")) + trigger_fudge_factor)
            elif option == "Toggle CH1 & CH2":
                if self.power_toggle_config:
                    self.powersupply.config_toggle_time(ch1=self.glitchy_data.get_parameter("powersupply_ch1_toggle"),
                                                        ch2=self.glitchy_data.get_parameter("powersupply_ch2_toggle"))
                    self.powersupply.set_toggle(channel="ALL")
                    self.power_toggle_config = False
                self.powersupply.trigger_toggle()
                ch1_time = float(self.glitchy_data.get_parameter("powersupply_ch1_toggle"))
                ch2_time = float(self.glitchy_data.get_parameter("powersupply_ch2_toggle"))
                if ch1_time > ch2_time:
                    time.sleep(ch1_time + trigger_fudge_factor)
                else:
                    time.sleep(ch2_time)
            else:
                pass

        def trigger_io(option):
            self.cw.trigger(trigger_type=option)

        def trigger_serial(option):
            if self.serial.connected:
                if option == "Send Message 1":
                    self.startupView.serial_transmit(event="btn_ser_send1")
                elif option == "Send Message 2":
                    self.startupView.serial_transmit(event="btn_ser_send2")
                elif option == "Send Message 3":
                    self.startupView.serial_transmit(event="btn_ser_send3")
                elif option == "Send Message 4":
                    self.startupView.serial_transmit(event="btn_ser_send4")
                elif option == "Match Message 1":
                    # Add functionality here
                    if self.startupView.serial_receive_test(widget_id="btn_ser_receive1") > -1:
                        self.glitcher_pause = True
                        self.glitcher_success = True
                elif option == "Match Message 2":
                    # Add functionality here
                    if self.startupView.serial_receive_test(widget_id="btn_ser_receive2") > -1:
                        self.glitcher_pause = True
                        self.glitcher_success = True
                elif option == "Match Message 3":
                    # Add functionality here
                    if self.startupView.serial_receive_test(widget_id="btn_ser_receive3") > -1:
                        self.glitcher_pause = True
                        self.glitcher_success = True
                elif option == "Match Message 4":
                    # Add functionality here
                    if self.startupView.serial_receive_test(widget_id="btn_ser_receive4") > -1:
                        self.glitcher_pause = True
                        self.glitcher_success = True
                elif option == "Serial Flood":
                    # self.serial.timeout = 2
                    # ser_data = self.serial.serial_flood(timeout=2)
                    timeout = float(self.startupView.v_serial_flood_timeout.get())
                    capture_size = int(self.startupView.v_serial_flood_capturesize.get())
                    datarate = int(self.startupView.v_serial_flood_datarate.get())
                    ser_data = self.serial_rx_flood(timeout=timeout, flood_rate=datarate, dump_size=capture_size)
                    if ser_data is not None:
                        logger.info(f"Read {ser_data} bytes before timeout occurred.")
                        if ser_data > capture_size:
                            self.glitcher_pause = True
                            self.glitcher_success = True
                else:
                    pass
            else:
                pass

        def trigger_openocd(option):
            if option == "Attempt Connection":
                # Just try to connect to the target device, for parts that are locked from access.
                pass
            elif option == "Run Command":
                # Connect and run a user specified command, check result against user specified data.
                pass
                # Working sample connect and command execution for AT SAM4C32-EK dev board using Atmel-ICE
                # results = subprocess.run(['openocd', '-f', '/usr/share/openocd/scripts/interface/cmsis-dap.cfg', '-f', '/usr/share/openocd/scripts/target/at91sam4c32x.cfg', '-c', 'debug_level 0', '-c', 'init', '-c', 'reset halt', '-c', 'flash probe 0', '-c', 'shutdown'], timeout=5, capture_output=True)
                # results.returncode  0 is success, 1 is failure to connect to target.
            else:
                pass

        def trigger_events(event_type: str):
            # Add code here to handle the initial trigger event's
            # event_type("pre" or "post")

            pre_event = {1: self.glitchy_data.get_parameter("pre_event_1"), 
                         2: self.glitchy_data.get_parameter("pre_event_2"), 
                         3: self.glitchy_data.get_parameter("pre_event_3")}
            pre_option = {1: self.glitchy_data.get_parameter("pre_option_1"), 
                          2: self.glitchy_data.get_parameter("pre_option_2"), 
                          3: self.glitchy_data.get_parameter("pre_option_3")}
            pre_delay = {1: self.glitchy_data.get_parameter("pre_delay_1"), 
                         2: self.glitchy_data.get_parameter("pre_delay_2"), 
                         3: self.glitchy_data.get_parameter("pre_delay_3")}
            post_event = {1: self.glitchy_data.get_parameter("post_event_1"), 
                          2: self.glitchy_data.get_parameter("post_event_2"), 
                          3: self.glitchy_data.get_parameter("post_event_3")}
            post_option = {1: self.glitchy_data.get_parameter("post_option_1"), 
                           2: self.glitchy_data.get_parameter("post_option_2"), 
                           3: self.glitchy_data.get_parameter("post_option_3")}
            post_delay = {1: self.glitchy_data.get_parameter("post_delay_1"), 
                          2: self.glitchy_data.get_parameter("post_delay_2"), 
                          3: self.glitchy_data.get_parameter("post_delay_3")}

            if event_type == "pre":
                for x in range(1, 4):
                    if event := pre_event[x]:
                        self.glitchy_data.enqueue("automated_glitch_log",
                                                  f"Pre: {event}: {pre_option[x]} \n")
                        if event == "Power":
                            trigger_power(pre_option[x])
                        elif event == "I/O":
                            trigger_io(pre_option[x])
                        elif event == "Serial":
                            trigger_serial(pre_option[x])
                        else:
                            pass
                        if delay := pre_delay[x]:
                            self.glitchy_data.enqueue("automated_glitch_log",
                                                      f"Pre: Delay: {pre_delay[x]} seconds\n")
                            time.sleep(float(delay))
            elif event_type == "post":
                for x in range(1, 4):
                    if event := post_event[x]:
                        self.glitchy_data.enqueue("automated_glitch_log",
                                                  f"Post: {event}: {post_option[x]} \n")
                        if event == "OpenOCD":
                            trigger_openocd(post_option[x])
                        elif event == "I/O":
                            trigger_io(post_option[x])
                        elif event == "Serial":
                            trigger_serial(post_option[x])
                        else:
                            pass
                        if delay := post_delay[x]:
                            self.glitchy_data.enqueue("automated_glitch_log",
                                                      f"Post: Delay: {post_delay[x]} seconds\n")
                            time.sleep(float(delay))

        def stop():
            # Cleanup when finished
            clear_live_values()
            time.sleep(0.5)
            self.startupView.update_automated_glitch_refresh = False
            self.glitcher_running = False
            self.glitcher_pause = False
            self.glitcher_stop = False
            self.power_toggle_config = True

        glitchtime_currentvalue = 0
        glitchstrength_currentvalue = 0
        progressbar_time = 0
        progressbar_strength = 0
        progressbar_overall = 0
        glitchcounter_triggered = 0
        glitchcounter_missed = 0
        update_live_values()

        self.glitcher_running = True
        self.glitcher_pause = False
        self.glitcher_stop = False
        self.glitcher_success = False
        # Start GUI refreshing from Data Model
        clear_live_values()
        self.startupView.update_automated_glitch_refresh = True
        # Config Power Supply Toggle
        self.power_toggle_config = True
        # Configure chipwhisperer
        self.cw.scope.adc.timeout = float(self.glitchy_data.get_parameter("cw_glitchtimeout"))
        self.cw.scope.adc.samples = 0
        self.cw.scope.glitch.ext_offset = int(self.glitchy_data.get_parameter("GlitchTimeStart"))
        self.cw.scope.glitch.repeat = int(self.glitchy_data.get_parameter("GlitchStrengthStart"))
        while self.cw.scope.glitch.repeat <= int(self.glitchy_data.get_parameter("GlitchStrengthStop")):
            glitchstrength_currentvalue = self.cw.scope.glitch.repeat
            strength_norm = int(self.glitchy_data.get_parameter("GlitchStrengthStop")) - \
                            int(self.glitchy_data.get_parameter("GlitchStrengthStart"))
            strength_step = (int(self.glitchy_data.get_parameter("GlitchStrengthStepSize")) /
                             (strength_norm + int(self.glitchy_data.get_parameter("GlitchStrengthStepSize")))) * 100
            while self.cw.scope.glitch.ext_offset <= int(self.glitchy_data.get_parameter("GlitchTimeStop")):
                timer_start = time.time()  # Time the glitching routine

                time_norm = int(self.glitchy_data.get_parameter("GlitchTimeStop")) - \
                            int(self.glitchy_data.get_parameter("GlitchTimeStart"))
                time_step = (int(self.glitchy_data.get_parameter("GlitchTimeStepSize")) /
                             (time_norm + int(self.glitchy_data.get_parameter("GlitchTimeStepSize")))) * 100
                total_step = ((strength_step / 100) * (time_step / 100)) * 100
                while self.glitcher_pause:
                    time.sleep(0.1)
                    if self.glitcher_stop:
                        break
                if self.glitcher_stop:
                    stop()
                    return

                trigger_events("pre")
                glitchtime_currentvalue = self.cw.scope.glitch.ext_offset

                # Update all user facing functions prior to the glitch
                self.glitchy_data.enqueue("automated_glitch_log",
                                          f"Glitching:\n"
                                          f"  Width: {glitchstrength_currentvalue}\n"
                                          f"  Offset: {glitchtime_currentvalue}\n")
                self.cw.scope.glitch.ext_offset += int(self.glitchy_data.get_parameter("GlitchTimeStepSize"))
                progressbar_time = time_step + progressbar_time
                progressbar_overall = total_step + progressbar_overall
                update_live_values()
                # Send the glitch
                self.cw.scope.arm()
                if self.cw.scope.capture():
                    glitchcounter_missed = glitchcounter_missed + 1
                else:
                    glitchcounter_triggered = glitchcounter_triggered + 1
                    trigger_events("post")  # Only running post trigger events if the trigger was successful
                # Glitch finished
                timer_stop = time.time()
                total_time = timer_stop - timer_start
                logger.info(f"Automated Glitch time: {total_time}")
                self.glitchy_data.enqueue("automated_glitch_log", "###########################\n"
                                                                  f"Total Time: {round(total_time, 2)} Seconds\n"
                                                                  "###########################\n\n")
            self.cw.scope.glitch.repeat += int(self.glitchy_data.get_parameter("GlitchStrengthStepSize"))
            self.cw.scope.glitch.ext_offset = int(self.glitchy_data.get_parameter("GlitchTimeStart"))
            # Update progress bar
            progressbar_time = 0  # Reset progress bar
            progressbar_strength = strength_step + progressbar_strength
            # End progress bar
        stop()
        self.startupView.glitch_stop()  # Reset button states after successful run

    def exit(self):
        # Call all functions to prepare for exit, close any open connections
        if self.powersupply.connected:
            self.powersupply.disconnect()
        if self.serial.connected:
            self.serial.disconnect()
        if self.cw.connected:
            self.cw.scope.dis()
        #     self.cw.stop = True
        pass

    def serial_tx(self, tx_message: str):
        byte_array_data = self.serial.parse_string(tx_message)
        self.glitchy_data.enqueue("serial", ("TX: " + tx_message + '\n'))
        self.serial.send(byte_array_data)

    def serial_rx_match(self, match_data: str = "", timeout: float = None, size: int = None) -> int:
        """ Receive data and report if there was a valid match prior to timeout.

            Return the match location in the received data, -1 for no match. """
        def calculate_highlight(byte_data, byte_len, match_loc, length):
            location_counter = match_loc
            new_loc = 0
            new_len = length
            byte_len -= 1  # Zero Ref
            exiting_special_char = False
            exiting_string = False
            if match_loc < 1:
                return new_loc, new_len
            for i in byte_data:
                logger.info(f"Location Counter: {location_counter}")
                if i < 32 or i > 126:
                    new_loc += 4
                    if exiting_string:
                        exiting_string = False
                        new_loc += 3
                        logger.info("Exited String")
                if 31 < i < 127:
                    new_loc += 1
                    exiting_string = True
                location_counter -= 1
                if location_counter == 0:
                    logger.info("Break from Location Counting")
                    break
            logger.info(f"New Loc: {new_loc}, New Len: {new_len}, Byte Data Len: {byte_len}")
            # Deal with different edge cases
            if (31 < byte_data[match_loc-1] < 127) and (byte_data[match_loc] < 32 or byte_data[match_loc] > 126):
                # String ending before special character
                new_loc += 3
            if (31 < byte_data[match_loc-1] < 127) and (31 < byte_data[match_loc] < 127):
                # String starting in the middle
                new_loc += 1
                new_len -= 1
            if (31 < byte_data[match_loc + byte_len - 1] < 127) and (31 < byte_data[match_loc + byte_len] < 127):
                # String ending in the middle
                new_len -= 1
            return new_loc, new_len

        header_len = 4
        match_data_bytes = bytes(self.serial.parse_string(match_data))
        match_data_bytes_len = len(match_data_bytes)
        rx_data = self.serial.receive(timeout, size)
        match_location = bytes(rx_data).find(match_data_bytes)
        rx_string = self.serial.parse_bytearray(rx_data)
        if match_location == -1:
            # No match
            self.glitchy_data.enqueue("serial", ("RX: " + rx_string + "\n"))
            return -1
        match_len = len(match_data)
        match_location, match_len = calculate_highlight(rx_data, match_data_bytes_len, match_location, match_len)
        self.glitchy_data.enqueue("serial", ("RX: " + rx_string + "\n"),
                                  f"Highlight,{header_len + match_location},{match_len}")
        return match_location

    def serial_rx_flood(self, timeout: float = 0, flood_rate: int = 20, dump_size: int = 1000) -> int:
        """ Detect if there is a large amount of data being sent via the serial port.

            This is indicative of a successful firmware dumping glitch.
            Return the number of bytes received in the timeout period. """

        def chunkstring(string, length):
            return (string[0 + i:length + i] for i in range(0, len(string), length))

        rx_data = bytearray()
        received_data = False
        start_time = time.time()
        timeout_val = time.time() + timeout
        dumping_flag = False
        while True:
            raw_rx = self.serial.raw_rx(timeout=0.5)
            rx_data += raw_rx
            if len(raw_rx) > flood_rate:
                if dumping_flag is False:
                    dumping_flag = True
                    self.glitchy_data.enqueue("automated_glitch_log",
                                              f"Dumping: {len(raw_rx)} Bps\n")
                timeout_val = time.time() + timeout
            if len(raw_rx) > 0:
                self.glitchy_data.enqueue("serial", ("Received: " + str(len(raw_rx)) + ' bytes\n'))
            sys.stdout.write(raw_rx.hex()[1:-1])
            # lines = (i.strip() for i in raw_rx.hex()[1:-1].splitlines())
            # for line in lines:
            #     for chunk in chunkstring(line, 80):
            #         # self.glitchy_data.enqueue("serial", (chunk + "\n"))
            #         sys.stdout.write(chunk)
            #         # This appears to take too much time and causes the app to slow down
            #         # self.startupView.serial_text_box.insert("end", chunk)
            #         # self.startupView.serial_text_box.see("end")

            if time.time() > timeout_val:
                self.glitchy_data.enqueue("automated_glitch_log",
                                          f"Dumping: Timed Out\n")
                break
            if len(rx_data) > dump_size:
                # Need to write this data to a log file
                self.glitchy_data.enqueue("automated_glitch_log",
                                          ("Successfully dumped " + str(len(rx_data)) + " bytes in " +
                                           str(int(time.time() - start_time)) + " seconds.\n"))
                # Writing to file
                with open(f"Data_Dump_{time.asctime()}.bin", "wb") as dump1:
                    # Writing data to a file
                    dump1.write(rx_data)
                break
        return len(rx_data)
        pass

    def serial_rx_stop(self):
        self.serial.stop_read = True

    @staticmethod
    def videohelp(topic=None):
        if topic == "Automated Glitch":
            webbrowser.open_new_tab("https://www.youtube.com/watch?v=TrEsTD9i0LU")
        elif topic == "Chipwhisperer":
            webbrowser.open_new_tab("https://youtu.be/TrEsTD9i0LU?t=329")
        elif topic == "Power Supply":
            webbrowser.open_new_tab("https://youtu.be/TrEsTD9i0LU?t=453")
        elif topic == "Serial":
            webbrowser.open_new_tab("https://youtu.be/TrEsTD9i0LU?t=1200")
        elif topic == "OpenOCD":
            webbrowser.open_new_tab("https://youtu.be/TrEsTD9i0LU?t=630")
        else:
            webbrowser.open_new_tab("http://www.youtube.com/c/RECESSIM")

    def open_file(self, load_file):
        # Test if load_file is a valid json file
        try:
            json_data = json.load(load_file)
        except ValueError as e:
            logger.error(f"Error: {e}")
            return None
        # Load the data into the glitchy_data object
        self.glitchy_data.load_data(json_data)

    def save_file(self, parameters, save_reference):
        json.dump(parameters, save_reference)
