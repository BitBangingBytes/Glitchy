import time
import chipwhisperer as cw
import logging
logger = logging.getLogger(__name__)


class ChipWhisperer:
    def __init__(self):
        self.connected = False
        self.SS_VER = 'SS_VER_1_1'
        self.scope = None

    @staticmethod
    def list_devices():
        return cw.list_devices()

    def connect(self, sn=None):
        """ Pass in a serial number if multiple ChipWhisperers are connected """
        if self.connected:
            # Start fresh each time this routine is called
            self.scope.dis()
        try:
            self.scope = cw.scope(sn=sn)
        except Exception:
            raise

    def disconnect(self):
        self.scope.dis()

    def configure(self, speed, source, mosfet):
        # if self.connected:
        #     # Start fresh each time this routine is called
        #     self.scope.dis()
        # try:
        #     self.scope = cw.scope()
        # except Exception:
        #     raise

        print("INFO: Found ChipWhisperer😍")
        logger.info("Found ChipWhisperer")
        time.sleep(0.05)
        self.scope.default_setup()

        if mosfet == "High Power":
            self.scope.io.glitch_hp = True
        elif mosfet == "Low Power":
            self.scope.io.glitch_lp = True
        elif mosfet == "Both":
            self.scope.io.glitch_hp = True
            self.scope.io.glitch_lp = True

        if source == "Internal":
            self.scope.clock.clkgen_freq = speed
            self.scope.glitch.clk_src = "clkgen"
            self.scope.glitch.resetDCMs()
            self.scope.glitch.output = "enable_only"
            self.scope.glitch.trigger_src = "ext_single"
        elif source == "External":
            self.scope.clock.clkgen_freq = speed
            self.scope.glitch.clk_src = "target"
            self.scope.glitch.resetDCMs()
            self.scope.glitch.output = "enable_only"
            self.scope.glitch.trigger_src = "ext_single"
        self.connected = True
        return True

    def trigger(self, trigger_type):
        """ Uses ChipWhisperer I/O 3 to send a trigger signal """
        if trigger_type == "High, Low, HiZ":
            self.scope.io.tio3 = "gpio_high"
            time.sleep(0.01)
            self.scope.io.tio3 = "gpio_low"
            time.sleep(0.01)
            self.scope.io.tio3 = "high_z"
        elif trigger_type == "Low, High, HiZ":
            self.scope.io.tio3 = "gpio_low"
            time.sleep(0.01)
            self.scope.io.tio3 = "gpio_high"
            time.sleep(0.01)
            self.scope.io.tio3 = "high_z"
        elif trigger_type == "High, Momentary Low":
            if self.scope.io.tio3 != "gpio_high":
                self.scope.io.tio3 = "gpio_high"
                time.sleep(0.01)
            self.scope.io.tio3 = "gpio_low"
            time.sleep(0.01)
            self.scope.io.tio3 = "gpio_high"
        elif trigger_type == "Low, Momentary High":
            if self.scope.io.tio3 != "gpio_low":
                self.scope.io.tio3 = "gpio_low"
                time.sleep(0.01)
            self.scope.io.tio3 = "gpio_high"
            time.sleep(0.01)
            self.scope.io.tio3 = "gpio_low"
        else:
            self.scope.io.tio3 = "high_z"  # Set output high impedance

    def print_settings(self):
        logger.info(self.scope)

    def glitch(self, trigger_time, timeout, glitch_width):
        """ Send a single glitch

            optionally send it after a specified number of clock cycles.
            Returns True if glitch was sent and False if it timed out.
        """
        logger.debug(trigger_time, timeout)
        self.scope.glitch.repeat = glitch_width
        self.scope.adc.timeout = timeout
        self.scope.adc.samples = 0
        # Glitch and wait for a trigger if a time is provided
        if trigger_time:
            self.scope.glitch.trigger_src = "ext_single"
            self.scope.glitch.ext_offset = trigger_time
            self.scope.arm()
            # Capture() is blocking, long timeouts freeze app
            if self.scope.capture():
                return False
            return True
        # Just send a glitch if no "Time after trigger" value is provided
        else:
            self.scope.glitch.trigger_src = "manual"
            self.scope.glitch.manual_trigger()
            return True
