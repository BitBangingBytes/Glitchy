# -*- encoding:utf-8 -*-
import telnetlib
import time
import logging
logger = logging.getLogger(__name__)


class EnvoxBB3:
    def __init__(self):
        self.refresh = True  # Flag to enable polling loop
        self.polling = None  # Flag to show whether the power supply is being read or not
        # self.queue = message_queue
        self.connected = False
        self.ipaddress = None
        self.port = None
        self.tn = None

    def connect(self, ipaddress: str, port: str) -> (bool, str):
        try:
            self.ipaddress = ipaddress
            self.port = int(port)
            self.tn = telnetlib.Telnet(self.ipaddress, self.port, timeout=2)
        except Exception:
            raise

        self.tn.write(b"\n")
        self.tn.read_very_eager()  # Get rid of any issues before we start
        self.connected = True
        return True

    def disconnect(self):
        self.connected = False
        while self.polling:
            time.sleep(0.1)
        self.tn.close()

    def get_settings(self, settings: dict):
        # Load current values from power supply
        self.refresh = False
        while self.polling:  # Wait until refresh cycle completes
            pass
        self.tn.write(b"INST CH1\n")
        self.tn.write(str.encode('VOLT?\n'))
        settings['powersupply_ch1_volt_set'] = \
            float(self.tn.read_until(match=b'\n').replace(b'\r\n', b'').decode("utf-8"))
        self.tn.write(str.encode('CURR?\n'))
        settings['powersupply_ch1_curr_set'] = \
            float(self.tn.read_until(match=b'\n').replace(b'\r\n', b'').decode("utf-8"))
        self.tn.write(str.encode('OUTP?\n'))
        if (self.tn.read_until(match=b'\n').replace(b'\r\n', b'')) == b'1':
            settings['powersupply_ch1_enable'] = True
        else:
            settings['powersupply_ch1_enable'] = False
        self.tn.write(b"INST CH2\n")
        self.tn.write(str.encode('VOLT?\n'))
        settings['powersupply_ch2_volt_set'] = \
            float(self.tn.read_until(match=b'\n').replace(b'\r\n', b'').decode("utf-8"))
        self.tn.write(str.encode('CURR?\n'))
        settings['powersupply_ch2_curr_set'] = \
            float(self.tn.read_until(match=b'\n').replace(b'\r\n', b'').decode("utf-8"))
        self.tn.write(str.encode('OUTP?\n'))
        if (self.tn.read_until(match=b'\n').replace(b'\r\n', b'')) == b'1':
            settings['powersupply_ch2_enable'] = True
        else:
            settings['powersupply_ch2_enable'] = False
        self.refresh = True

    def set_settings(self, settings: dict):
        """ Command used to set power supply values

            Voltage and current are set, outputs are enabled/disabled.
        """

        self.refresh = False
        while self.polling:  # Wait until refresh cycle completes
            pass
        # Setup channel 1
        self.tn.write(b'INST CH1\n')
        if settings['powersupply_ch1_volt_set'] != '':
            self.tn.write(str.encode('VOLT {}\n'.format(settings['powersupply_ch1_volt_set'])))
        if settings['powersupply_ch1_curr_set'] != '':
            self.tn.write(str.encode('CURR {}\n'.format(settings['powersupply_ch1_curr_set'])))
        if settings['powersupply_ch1_enable'] is True:
            self.tn.write(b'OUTP 1\n')
        elif settings['powersupply_ch1_enable'] is False:
            self.tn.write(b'OUTP 0\n')

        # Setup channel 2
        self.tn.write(b'INST CH2\n')
        if settings['powersupply_ch2_volt_set'] != '':
            self.tn.write(str.encode('VOLT {}\n'.format(settings['powersupply_ch2_volt_set'])))
        if settings['powersupply_ch2_curr_set'] != '':
            self.tn.write(str.encode('CURR {}\n'.format(settings['powersupply_ch2_curr_set'])))
        if settings['powersupply_ch2_enable'] is True:
            self.tn.write(b'OUTP 1\n')
        elif settings['powersupply_ch2_enable'] is False:
            self.tn.write(b'OUTP 0\n')

        self.refresh = True

    def get_measurement(self, measurements: dict):
        self.polling = True
        self.tn.write(b"INST CH1\n")
        self.tn.write(str.encode('MEAS:VOLT?\n'))
        measurements['powersupply_ch1_volt_meas'] = \
            float(self.tn.read_until(match=b'\n', timeout=0.5).replace(b'\r\n', b''))
        self.tn.write(str.encode('MEAS:CURR?\n'))
        measurements['powersupply_ch1_curr_meas'] = \
            float(self.tn.read_until(match=b'\n', timeout=0.5).replace(b'\r\n', b''))
        self.tn.write(b"INST CH2\n")
        self.tn.write(str.encode('MEAS:VOLT?\n'))
        measurements['powersupply_ch2_volt_meas'] = \
            float(self.tn.read_until(match=b'\n', timeout=0.5).replace(b'\r\n', b''))
        self.tn.write(str.encode('MEAS:CURR?\n'))
        measurements['powersupply_ch2_curr_meas'] = \
            float(self.tn.read_until(match=b'\n', timeout=0.5).replace(b'\r\n', b''))
        self.polling = False

    def config_toggle_time(self, channel: int, voltage: float, current: float, toggle_time: float):
        """ Take the current voltage and current settings for a given channel and load into power supply toggle list"""
        logger.info(f"Envox BB3 config toggle time, channel = {channel}, toggle time = {toggle_time}")

        self.refresh = False
        while self.polling:  # Wait until refresh cycle completes
            pass

        if channel == 1:
            self.tn.write(b'INST CH1\n')
        elif channel == 2:
            self.tn.write(b'INST CH2\n')
        else:
            return

        self.tn.write(str.encode(f"VOLT:MODE LIST\nLIST:VOLT 0, {voltage}\nCURR:MODE LIST\nLIST:CURR {current}\n"
                                 f"LIST:DWEL {toggle_time}\nLIST:COUN 1\nTRIG:SOUR IMM\nTRIG:EXIT:COND LAST\n"))
        self.refresh = True

    def trigger_toggle(self):
        self.refresh = False
        while self.polling:  # Wait until refresh cycle completes
            pass
        self.tn.write(b'INIT\n')
        self.refresh = True

    def set_toggle(self, channel: str):
        """ Set which channel should toggle when a trigger is sent """
        self.refresh = False
        while self.polling:  # Wait until refresh cycle completes
            pass
        match channel:
            case "1":
                # Enable toggle on channel 1
                self.tn.write(b'INST CH1\n')
                self.tn.write(b'VOLT:MODE LIST\nCURR:MODE LIST\n')
                # Disable toggle on channel 2
                self.tn.write(b'INST CH2\n')
                self.tn.write(b'VOLT:MODE FIX\nCURR:MODE FIX\n')
            case "2":
                # Enable toggle on channel 2
                self.tn.write(b'INST CH2\n')
                self.tn.write(b'VOLT:MODE LIST\nCURR:MODE LIST\n')
                # Disable toggle on channel 1
                self.tn.write(b'INST CH1\n')
                self.tn.write(b'VOLT:MODE FIX\nCURR:MODE FIX\n')
            case "ALL":
                # Enable toggle on channel 1
                self.tn.write(b'INST CH1\n')
                self.tn.write(b'VOLT:MODE LIST\nCURR:MODE LIST\n')
                # Enable toggle on channel 2
                self.tn.write(b'INST CH2\n')
                self.tn.write(b'VOLT:MODE LIST\nCURR:MODE LIST\n')
        self.refresh = True
