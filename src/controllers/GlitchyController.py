# -*- encoding:utf-8 -*-
import json
import time
import webbrowser

from controllers.ChipWhisperer import ChipWhisperer
from controllers.EnvoxBB3 import EnvoxBB3
from controllers.PowerSupply import PowerSupply
from controllers.Serial import Serial
from core.Controller import Controller
from models.GlitchyData import GlitchyDataModel

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
        # Initial view (only view at this time) to load
        self.startupView = self.loadView("Startup")

    # -----------------------------------------------------------------------
    #        Methods
    # -----------------------------------------------------------------------
    """
        @Override
    """

    def main(self):
        self.startupView.main()

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
            if option == "Toggle CH1 0.25 Sec":
                time.sleep(0.1)
                self.powersupply.set_settings(ch1_en=False)
                time.sleep(0.25)
                self.powersupply.set_settings(ch1_en=True)
            elif option == "Toggle CH1 2 Sec":
                self.powersupply.set_settings(ch1_en=False)
                time.sleep(2)
                self.powersupply.set_settings(ch1_en=True)
            elif option == "Toggle CH2 0.25 Sec":
                self.powersupply.set_settings(ch2_en=False)
                time.sleep(0.25)
                self.powersupply.set_settings(ch2_en=True)
            elif option == "Toggle CH2 2 Sec":
                self.powersupply.set_settings(ch2_en=False)
                time.sleep(2)
                self.powersupply.set_settings(ch2_en=True)
            else:
                pass

        def trigger_io(option):
            """ Still work to do

            """
            self.cw.trigger(option)

            if option == "High to Low":
                pass
            elif option == "Low to High":
                pass
            elif option == "High Momentary Low":
                pass
            elif option == "Low Momentary High":
                pass
            else:
                pass

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
                        if event == "Power":
                            trigger_power(pre_option[x])
                        elif event == "I/O":
                            trigger_io(pre_option[x])
                        elif event == "Serial":
                            trigger_serial(pre_option[x])
                        else:
                            pass
                        if delay := pre_delay[x]:
                            time.sleep(float(delay))
            elif event_type == "post":
                for x in range(1, 4):
                    if event := post_event[x]:
                        if event == "OpenOCD":
                            trigger_openocd(post_option[x])
                        elif event == "I/O":
                            trigger_io(post_option[x])
                        elif event == "Serial":
                            trigger_serial(post_option[x])
                        else:
                            pass
                        if delay := post_delay[x]:
                            time.sleep(float(delay))

        def stop():
            # Cleanup when finished
            clear_live_values()
            time.sleep(0.5)
            self.startupView.update_automated_glitch_refresh = False
            self.glitcher_running = False
            self.glitcher_pause = False
            self.glitcher_stop = False

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
                # Send the Glitch
                self.cw.scope.arm()
                if self.cw.scope.capture():
                    glitchcounter_missed = glitchcounter_missed + 1
                else:
                    glitchcounter_triggered = glitchcounter_triggered + 1
                    trigger_events("post")  # Only running post trigger events if the trigger was successful
                #
                self.cw.scope.glitch.ext_offset += int(self.glitchy_data.get_parameter("GlitchTimeStepSize"))
                progressbar_time = time_step + progressbar_time
                progressbar_overall = total_step + progressbar_overall

                update_live_values()
                timer_stop = time.time()
                print(timer_stop - timer_start)
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

    @staticmethod
    def videohelp(topic=None):
        if topic == "Automated Glitch":
            webbrowser.open_new_tab("http://www.youtube.com/c/RECESSIM")
        elif topic == "Chipwhisperer":
            webbrowser.open_new_tab("http://www.youtube.com/c/RECESSIM")
        elif topic == "Power Supply":
            webbrowser.open_new_tab("http://www.youtube.com/c/RECESSIM")
        elif topic == "Serial":
            webbrowser.open_new_tab("http://www.youtube.com/c/RECESSIM")
        elif topic == "OpenOCD":
            webbrowser.open_new_tab("http://www.youtube.com/c/RECESSIM")
        else:
            webbrowser.open_new_tab("http://www.youtube.com/c/RECESSIM")

    def open_file(self, load_file):
        # Add code here to verify load file integrity
        checked_data = load_file
        # Add code here to call data model
        self.glitchy_data.load_data(json.load(checked_data))

    def save_file(self, parameters, save_reference):
        json.dump(parameters, save_reference)
