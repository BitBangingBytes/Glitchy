import time
from threading import Thread
import logging
logger = logging.getLogger(__name__)


class PowerSupply:
    def __init__(self, data_model=None, supply_model=None):
        self.polling = None
        self.ps_measurements = None
        self.glitchy_data = data_model
        self.powersupply = supply_model
        self.ps_polling = None
        self.connected = False
        self.ps_measurements = {'powersupply_ch1_volt_meas': '', 'powersupply_ch2_volt_meas': '',
                                'powersupply_ch1_curr_meas': '', 'powersupply_ch2_curr_meas': ''}
        self.ps_settings = {'powersupply_ch1_volt_set': '', 'powersupply_ch2_volt_set': '',
                            'powersupply_ch1_curr_set': '', 'powersupply_ch2_curr_set': '',
                            'powersupply_ch1_enable': False, 'powersupply_ch2_enable': False}
        self.settings_changed = False

    def connect(self, ipaddress, port):
        try:
            self.powersupply.connect(ipaddress, port)
        except Exception:
            raise
        self.connected = True
        self.get_settings()
        self.settings_changed = True
        self.ps_polling = Thread(target=self.get_measurements)
        self.ps_polling.daemon = True
        self.ps_polling.start()
        return True

    def disconnect(self):
        self.powersupply.disconnect()
        self.connected = False
        for key in self.ps_settings:
            self.ps_settings[key] = None
            self.glitchy_data.set_parameter(key, None)
        for key in self.ps_measurements:
            self.ps_settings[key] = None
            self.glitchy_data.set_parameter(key, None)

    def set_settings(self, ch1_en=None, ch2_en=None, ch1_volt='', ch1_curr='', ch2_volt='', ch2_curr=''):
        # Write to Power Supply
        self.settings_changed = True
        self.ps_settings['powersupply_ch1_enable'] = ch1_en
        self.ps_settings['powersupply_ch2_enable'] = ch2_en
        self.ps_settings['powersupply_ch1_volt_set'] = ch1_volt
        self.ps_settings['powersupply_ch2_volt_set'] = ch2_volt
        self.ps_settings['powersupply_ch1_curr_set'] = ch1_curr
        self.ps_settings['powersupply_ch2_curr_set'] = ch2_curr
        self.powersupply.set_settings(self.ps_settings)
        # Update Data Model
        for key in self.ps_settings:
            self.glitchy_data.set_parameter(key, self.ps_settings[key])
        self.get_settings()

    def is_changed(self):
        if self.settings_changed:
            self.settings_changed = False
            return True
        else:
            return False

    def get_settings(self):
        self.powersupply.get_settings(self.ps_settings)
        for key in self.ps_settings:
            self.glitchy_data.set_parameter(key, self.ps_settings[key])

    def get_measurements(self):
        while True:
            run_once = True
            timeout = 0
            while not self.powersupply.refresh:
                time.sleep(0.1)
                timeout += 1
                # Delay for 1 second before clearing power supply display
                if timeout > 20 and run_once:
                    for key in self.ps_measurements:
                        self.glitchy_data.set_parameter(key, None)
                    run_once = False
            if not self.powersupply.connected:
                break

            self.powersupply.get_measurement(self.ps_measurements)
            for key in self.ps_measurements:
                self.glitchy_data.set_parameter(key, self.ps_measurements[key])

    def config_toggle_time(self, ch1=None, ch2=None):
        """ Load all toggle data into power supply but don't trigger.

            This will be useful for the automated glitch to load once then trigger on each pass.
        """
        if ch1:
            self.glitchy_data.set_parameter('powersupply_ch1_toggle', str(ch1))
            self.powersupply.config_toggle_time(
                channel=1,
                voltage=float(self.glitchy_data.get_parameter("powersupply_ch1_volt_set")),
                current=float(self.glitchy_data.get_parameter("powersupply_ch1_curr_set")),
                toggle_time=float(ch1))
        if ch2:
            self.glitchy_data.set_parameter('powersupply_ch2_toggle', str(ch2))
            self.powersupply.config_toggle_time(
                channel=2,
                voltage=float(self.glitchy_data.get_parameter("powersupply_ch2_volt_set")),
                current=float(self.glitchy_data.get_parameter("powersupply_ch2_curr_set")),
                toggle_time=float(ch2))

    def trigger_toggle(self):
        self.powersupply.trigger_toggle()

    def set_toggle(self, channel: str):
        """Send ABORt command to power supply to exit trigger mode"""
        self.powersupply.set_toggle(channel)

