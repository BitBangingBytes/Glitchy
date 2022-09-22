"""
    Model description
"""


class GlitchyDataModel:
    def __init__(self):
        self.parameters = {
            # ------ Pre and Post glitch events ------
            'pre_event_1': '',   'pre_event_2': '',   'pre_event_3': '',
            'pre_option_1': '',  'pre_option_2': '',  'pre_option_3': '',
            'pre_delay_1': '',   'pre_delay_2': '',   'pre_delay_3': '',
            'post_event_1': '',  'post_event_2': '',  'post_event_3': '',
            'post_option_1': '', 'post_option_2': '', 'post_option_3': '',
            'post_delay_1': '',  'post_delay_2': '',  'post_delay_3': '',
            # ------ Glitching vars ------
            'GlitchTimeStart': '',     'GlitchTimeStop': '',     'GlitchTimeStepSize': '',
            'GlitchStrengthStart': '', 'GlitchStrengthStop': '', 'GlitchStrengthStepSize': '',
            # Chipwhisperer vars
            'cw_cyclesaftertrigger': '', 'cw_glitchcycles': '', 'cw_speed': '', 'cw_source': '',
            'cw_glitchtimeout': '',      'cw_mosfet': '',
            # ------ Power Supply vars ------
            'powersupply_ipaddr': '',        'powersupply_port': '',
            'powersupply_ch1_volt_meas': '', 'powersupply_ch2_volt_meas': '',
            'powersupply_ch1_curr_meas': '', 'powersupply_ch2_curr_meas': '',
            'powersupply_ch1_volt_set': '',  'powersupply_ch2_volt_set': '',
            'powersupply_ch1_curr_set': '',  'powersupply_ch2_curr_set': '',
            'powersupply_ch1_enable': '',    'powersupply_ch2_enable': '',
            'powersupply_ch1_toggle': '',    'powersupply_ch2_toggle': '',
            # ------ Serial Port vars ------
            'sp_port': '',     'sp_speed': '',  'sp_databits': '', 'sp_stopbits': '',
            'sp_parity': '', 'sp_flowcontrol': '', 'sp_rxtimeout': '',
            'sp_tx1': '', 'sp_tx2': '', 'sp_tx3': '', 'sp_tx4': '',
            'sp_rx1': '', 'sp_rx2': '', 'sp_rx3': '', 'sp_rx4': '',
            # ------ Debugger vars ------
            'debug_adaptor': '', 'debug_target': '', 'debug_halt': '', 'debug_commands': '',
            #
            # ------ This data is not saved, only used as part of displaying data ------
            #
            # ------ Glitching variables used during automated glitching ------
            'glitchtime_currentvalue': '', 'glitchstrength_currentvalue': '', 'progressbar_time': '',
            'progressbar_strength': '', 'progressbar_overall': '', 'glitchcounter_triggered': '',
            'glitchcounter_missed': ''
        }

    def load_data(self, load_data):
        try:
            for key in load_data:
                self.parameters[key] = load_data[key]
        except KeyError:
            print("Error loading a key")

    def get_parameter(self, parameter: str) -> str:
        try:
            return self.parameters[parameter]
        except KeyError:
            print(f"{parameter} not found in call to {GlitchyDataModel.__name__}:get_parameter")
            return ''

    def set_parameter(self, parameter: str, value: object) -> bool:
        try:
            self.parameters[parameter] = value
            return True
        except AttributeError:
            return False

    def all_parameters(self):
        return self.parameters
