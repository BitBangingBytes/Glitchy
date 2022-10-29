import os
import pathlib
import time
from threading import Thread
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfile, asksaveasfile
from tkinter.messagebox import showerror

from PIL import Image, ImageTk
from quantiphy import Quantity
from tktooltip import ToolTip

import pygubu
from views.Events import Events
from views.FieldValidate import FieldValidate
from views.View import View

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "pygubu" / "Glitchy_v0.2.ui"


class StartupView(View, Events, FieldValidate):
    # -----------------------------------------------------------------------
    #        Constructor
    # -----------------------------------------------------------------------
    def __init__(self, controller):
        super().__init__()
        self.update_automated_glitch_refresh = False
        self.master = None
        self.glitcher = None
        self.queue = None
        self.powersupply = None
        self.parameters = None
        self.com_port = None
        self.splash = None
        self.height = 0

        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)

        # Main widget
        self.mainwindow = builder.get_object("toplevel1", self.master)

        self._initialize_variables()
        builder.import_variables(
            self,
            [
                "glitchtime_startvalue",
                "glitchtime_stopvalue",
                "glitchstrength_startvalue",
                "glitchstrength_stopvalue",
                "glitchtime_stepvalue",
                "glitchstrength_stepvalue",
                "progressbar_time",
                "progressbar_strength",
                "progressbar_overall",
                "v_pre_delay_1",
                "v_pre_delay_2",
                "v_pre_delay_3",
                "v_post_delay_1",
                "v_post_delay_2",
                "v_post_delay_3",
                "glitchcounter_triggered",
                "glitchcounter_missed",
                "glitchtime_currentvalue",
                "glitchstrength_currentvalue",
                "v_cw_cyclesaftertrigger",
                "v_cw_trigger_calctime",
                "v_cw_glitch_calctime",
                "v_cw_glitchstatus",
                "v_cw_glitchcycles",
                "v_cw_glitchtimeout",
                "v_cw_speed",
                "v_cw_source",
                "v_cw_mosfet",
                "v_powersupply_ipaddr",
                "v_powersupply_port",
                "v_powersupply_startingvoltage1",
                "v_powersupply_startingvoltage2",
                "v_powersupply_startingcurrent1",
                "v_powersupply_startingcurrent2",
                "v_powersupply_ch1_enable",
                "v_powersupply_ch2_enable",
                "v_powersupply_toggle1",
                "v_powersupply_toggle2",
                "v_powersupply_measuredvoltage1",
                "v_powersupply_measuredvoltage2",
                "v_powersupply_measuredcurrent1",
                "v_powersupply_measuredcurrent2",
                "v_serialport_serialport",
                "v_serialport_speed",
                "v_serialport_databits",
                "v_serialport_stopbits",
                "v_serialport_parity",
                "v_serialport_flowcontrol",
                "v_serial_txmsg1",
                "v_serial_txmsg2",
                "v_serial_txmsg3",
                "v_serial_txmsg4",
                "v_serial_rxmsg1",
                "v_serial_rxmsg2",
                "v_serial_rxmsg3",
                "v_serial_rxmsg4",
                "v_serial_rx_test_timeout",
                "v_serial_rx_test_status",
                "v_serial_flood_datarate",
                "v_serial_flood_capturesize",
                "v_serial_flood_timeout",
                "v_debug_adaptor",
                "v_debug_target",
                "v_debug_halt",
                "v_debug_commands",
            ],
        )
        self._setup_buttons()
        self._setup_textboxes()
        self._setup_ttk_styles()
        # Add all hover tips in here
        self.hover_tips()
        builder.connect_callbacks(self)

        # Set default combobox values
        self.builder.get_object('c_cw_mosfet').current(0)
        self.builder.get_object('c_cw_source').current(0)

        # Configure Input fields in GUI
        self.v_cw_speed.set("100")
        self.v_cw_glitchtimeout.set("1")

        # Load image and resize for About page
        self.canvas = builder.get_object("c_about_logo")
        self.logo_file = Image.open(str(PROJECT_PATH) + "/media/" + "Glitchy.png")
        # self.resized_logo = self.logo_file.resize((200, 200), resample=Image.LANCZOS)
        self.logo = ImageTk.PhotoImage(self.logo_file)
        self.canvas.create_image(0, 0, image=self.logo, anchor="nw")

        self.glitchyController = controller
        self.glitchy_data = self.glitchyController.glitchy_data

    def _initialize_variables(self):
        self.glitchtime_startvalue = None
        self.glitchtime_stopvalue = None
        self.glitchstrength_startvalue = None
        self.glitchstrength_stopvalue = None
        self.glitchtime_stepvalue = None
        self.glitchstrength_stepvalue = None
        self.progressbar_time = None
        self.progressbar_strength = None
        self.progressbar_overall = None
        self.v_pre_delay_1 = None
        self.v_pre_delay_2 = None
        self.v_pre_delay_3 = None
        self.v_post_delay_1 = None
        self.v_post_delay_2 = None
        self.v_post_delay_3 = None
        self.glitchcounter_triggered = None
        self.glitchcounter_missed = None
        self.glitchtime_currentvalue = None
        self.glitchstrength_currentvalue = None
        self.v_cw_cyclesaftertrigger = None
        self.v_cw_trigger_calctime = None
        self.v_cw_glitch_calctime = None
        self.v_cw_glitchstatus = None
        self.v_cw_glitchcycles = None
        self.v_cw_glitchtimeout = None
        self.v_cw_speed = None
        self.v_cw_source = None
        self.v_cw_mosfet = None
        self.v_powersupply_ipaddr = None
        self.v_powersupply_port = None
        self.v_powersupply_startingvoltage1 = None
        self.v_powersupply_startingvoltage2 = None
        self.v_powersupply_startingcurrent1 = None
        self.v_powersupply_startingcurrent2 = None
        self.v_powersupply_ch1_enable = None
        self.v_powersupply_ch2_enable = None
        self.v_powersupply_toggle1 = None
        self.v_powersupply_toggle2 = None
        self.v_powersupply_measuredvoltage1 = None
        self.v_powersupply_measuredvoltage2 = None
        self.v_powersupply_measuredcurrent1 = None
        self.v_powersupply_measuredcurrent2 = None
        self.v_serialport_serialport = None
        self.v_serialport_speed = None
        self.v_serialport_databits = None
        self.v_serialport_stopbits = None
        self.v_serialport_parity = None
        self.v_serialport_flowcontrol = None
        self.v_serial_txmsg1 = None
        self.v_serial_txmsg2 = None
        self.v_serial_txmsg3 = None
        self.v_serial_txmsg4 = None
        self.v_serial_rxmsg1 = None
        self.v_serial_rxmsg2 = None
        self.v_serial_rxmsg3 = None
        self.v_serial_rxmsg4 = None
        self.v_serial_rx_test_timeout = None
        self.v_serial_rx_test_status = None
        self.v_serial_flood_datarate = None
        self.v_serial_flood_capturesize = None
        self.v_serial_flood_timeout = None
        self.v_debug_adaptor = None
        self.v_debug_target = None
        self.v_debug_halt = None
        self.v_debug_commands = None

    def _setup_buttons(self):
        # Assign buttons for control over status (normal vs disabled)
        self.btn_ser_disconnect = self.builder.get_object('btn_serial_disconnect')
        self.btn_ser_connect = self.builder.get_object('btn_serial_connect')
        self.btn_ser_send1 = self.builder.get_object('btn_ser_send1')
        self.btn_ser_send2 = self.builder.get_object('btn_ser_send2')
        self.btn_ser_send3 = self.builder.get_object('btn_ser_send3')
        self.btn_ser_send4 = self.builder.get_object('btn_ser_send4')
        self.btn_ser_receive1 = self.builder.get_object('btn_ser_receive1')
        self.btn_ser_receive2 = self.builder.get_object('btn_ser_receive2')
        self.btn_ser_receive3 = self.builder.get_object('btn_ser_receive3')
        self.btn_ser_receive4 = self.builder.get_object('btn_ser_receive4')
        self.btn_ps_disconnect = self.builder.get_object('btn_powersupply_disconnect')
        self.btn_ps_connect = self.builder.get_object('btn_powersupply_connect')
        self.btn_ps_set1 = self.builder.get_object('btn_powersupply_set1')
        self.btn_ps_set2 = self.builder.get_object('btn_powersupply_set2')
        self.btn_ps_toggle1 = self.builder.get_object('btn_powersupply_toggle1')
        self.btn_ps_toggle2 = self.builder.get_object('btn_powersupply_toggle2')
        self.run_button = self.builder.get_object('Run')
        self.pause_button = self.builder.get_object('Pause')
        self.stop_button = self.builder.get_object('Stop')
        self.glitch_button = self.builder.get_object('b_cw_glitch')
        self.io_button = self.builder.get_object('b_cw_io')
        self.print_settings_button = self.builder.get_object('b_cw_printsettings')

        self.pre_event_1 = self.builder.get_object('pre_event_1')
        self.pre_event_2 = self.builder.get_object('pre_event_2')
        self.pre_event_3 = self.builder.get_object('pre_event_3')
        self.pre_option_1 = self.builder.get_object('pre_option_1')
        self.pre_option_2 = self.builder.get_object('pre_option_2')
        self.pre_option_3 = self.builder.get_object('pre_option_3')
        self.pre_delay_1 = self.builder.get_object('pre_delay_1')
        self.pre_delay_2 = self.builder.get_object('pre_delay_2')
        self.pre_delay_3 = self.builder.get_object('pre_delay_3')
        self.post_event_1 = self.builder.get_object('post_event_1')
        self.post_event_2 = self.builder.get_object('post_event_2')
        self.post_event_3 = self.builder.get_object('post_event_3')
        self.post_option_1 = self.builder.get_object('post_option_1')
        self.post_option_2 = self.builder.get_object('post_option_2')
        self.post_option_3 = self.builder.get_object('post_option_3')
        self.post_delay_1 = self.builder.get_object('post_delay_1')
        self.post_delay_2 = self.builder.get_object('post_delay_2')
        self.post_delay_3 = self.builder.get_object('post_delay_3')

    def _setup_textboxes(self):
        self.serial_text_box = self.builder.get_object('t_serialport_text_box')
        self.serial_text_scrollbar = self.builder.get_object('serial_scrollbar')
        #  communicate back to the scrollbar
        self.serial_text_scrollbar['command'] = self.serial_text_box.yview
        self.serial_text_box['yscrollcommand'] = self.serial_text_scrollbar.set

        self.automated_glitch_text_box = self.builder.get_object('t_automated_glitch_text_box')
        self.automated_glitch_text_scrollbar = self.builder.get_object('log_scrollbar')
        #  communicate back to the scrollbar
        self.automated_glitch_text_scrollbar['command'] = self.automated_glitch_text_box.yview
        self.automated_glitch_text_box['yscrollcommand'] = self.automated_glitch_text_scrollbar.set

    def _setup_ttk_styles(self):
        # ttk styles configuration
        self.style = style = ttk.Style()
        optiondb = style.master
        # --------------------
        # This file is used for defining Ttk styles.
        # Use the 'style' object to define styles.

        # Pygubu Designer will need to know which style definition file
        # you wish to use in your project.

        # To specify a style definition file in Pygubu Designer:
        # Go to: Edit -> Preferences -> Ttk Styles -> Browse (button)

        # In Pygubu Designer:
        # Assuming that you have specified a style definition file,
        # - Use the 'style' combobox drop-down menu in Pygubu Designer
        #   to select a style that you have defined.
        # - Changes made to the chosen style definition file will be
        #   automatically reflected in Pygubu Designer.
        # --------------------

        # Example code:
        style.configure(
            "GreenButton.TButton",
            font=("Segoe UI", 10, "bold"),
            background="green",
            foreground="white",
        )

        style.map('GreenButton.TButton',
                  foreground=[('active', 'black')],
                  background=[('active', 'green'), ('disabled', 'grey')])

        style.configure(
            "RedButton.TButton",
            font=("Segoe UI", 10, "bold"),
            background="red",
            foreground="white",
        )

        style.map('RedButton.TButton',
                  foreground=[('active', 'black')],
                  background=[('active', 'red'), ('disabled', 'grey')])

    def hover_tips(self):
        ToolTip(self.builder.get_object('Run'),
                msg="Hella informative tip.", delay=1.0)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.glitchyController.exit()
            self.mainwindow.destroy()

    # -----------------------------------------------------------------------
    #        Methods
    # -----------------------------------------------------------------------
    """
    @Override
    """
    def main(self):
        def unroll_app():
            # height = 0  # self.mainwindow.attributes("height")
            if self.height < 885:
                self.height += 5
                self.mainwindow.geometry("750x" + str(self.height))
                self.mainwindow.after(5, unroll_app)
            else:
                self.mainwindow.resizable(False, False)

        def fade_away():
            alpha = self.splash.attributes("-alpha")
            if alpha > 0:
                alpha -= .006
                self.splash.attributes("-alpha", alpha)
                self.splash.after(10, fade_away)
            else:
                self.splash.destroy()

        def splash_screen():
            self.splash = tk.Toplevel()
            self.splash.overrideredirect(True)
            base_folder = os.path.dirname(__file__)
            image_path = base_folder + '/media/' + 'Glitchy.png'
            logo = tk.PhotoImage(file=image_path)
            w, h = logo.width(), logo.height()
            screen_width = self.splash.winfo_screenwidth()
            screen_height = self.splash.winfo_screenheight()
            x = (screen_width / 2) - (w / 2)
            y = (screen_height / 2) - (h / 2)
            self.splash.geometry(f'{w}x{h}+{int(x)}+{int(y)}')
            canvas = tk.Canvas(self.splash, highlightthickness=0)
            canvas.create_image(0, 0, image=logo, anchor='nw')
            canvas.pack(expand=1, fill='both')
            self.splash.after(1000, fade_away)
            self.splash.mainloop()

        self.mainwindow.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.mainwindow.eval(f'tk::PlaceWindow . center')
        self.update_values()
        # Uncomment this for app animation on load
        # self.mainwindow.geometry("750x20")
        # unroll_app()
        self.mainwindow.geometry("750x885")  # Comment this out if using the app unroll feature
        self.mainwindow.resizable(False, False)

        splash_screen()
        self.mainwindow.mainloop()

    def update_values(self):
        def update_serial_logging():
            while self.glitchyController.glitchy_data.is_empty("serial") is False:
                data, command = self.glitchyController.glitchy_data.dequeue("serial")
                if command != "":
                    command = command.split(",")
                else:
                    self.serial_text_box.insert(tk.END, data)
                    self.serial_text_box.see(tk.END)
                    return

                if command[0] == "Highlight":
                    # print(f"Command: {command}")
                    highlight_start = command[1]
                    highlight_len = command[2]
                    highlight_end = str(int(highlight_start) + int(highlight_len))
                    current_line, current_pos = self.serial_text_box.index('end - 1 line').split(".")
                    # print(f"Current Line: {current_line}, Current Position: {current_pos} and Tk.END: {tk.END}")
                    # print(f"Highlight start: {highlight_start}, Highlight Length: {highlight_len}")
                    self.serial_text_box.insert(tk.END, data)
                    self.serial_text_box.tag_add('start', str(current_line + "." + highlight_start),
                                                 str(current_line + "." + highlight_end))
                    self.serial_text_box.tag_config("start", background="black", foreground="white")

        def update_powersupply_measurements():
            if (value := self.glitchy_data.get_parameter('powersupply_ch1_volt_meas')) is not None:
                self.v_powersupply_measuredvoltage1.set(str(value))
            else:
                self.v_powersupply_measuredvoltage1.set("---------")

            if (value := self.glitchy_data.get_parameter('powersupply_ch2_volt_meas')) is not None:
                self.v_powersupply_measuredvoltage2.set(str(value))
            else:
                self.v_powersupply_measuredvoltage2.set("---------")

            if (value := self.glitchy_data.get_parameter('powersupply_ch1_curr_meas')) is not None:
                self.v_powersupply_measuredcurrent1.set(str(value))
            else:
                self.v_powersupply_measuredcurrent1.set("---------")

            if (value := self.glitchy_data.get_parameter('powersupply_ch2_curr_meas')) is not None:
                self.v_powersupply_measuredcurrent2.set(str(value))
            else:
                self.v_powersupply_measuredcurrent2.set("---------")

        def update_powersupply_setvalues():
            if self.v_powersupply_startingvoltage1.get() != self.glitchy_data.get_parameter('powersupply_ch1_volt_set'):
                self.v_powersupply_startingvoltage1.set(self.glitchy_data.get_parameter('powersupply_ch1_volt_set'))
            if self.v_powersupply_startingvoltage2.get() != self.glitchy_data.get_parameter('powersupply_ch2_volt_set'):
                self.v_powersupply_startingvoltage2.set(self.glitchy_data.get_parameter('powersupply_ch2_volt_set'))
            if self.v_powersupply_startingcurrent1.get() != self.glitchy_data.get_parameter('powersupply_ch1_curr_set'):
                self.v_powersupply_startingcurrent1.set(self.glitchy_data.get_parameter('powersupply_ch1_curr_set'))
            if self.v_powersupply_startingcurrent2.get() != self.glitchy_data.get_parameter('powersupply_ch2_curr_set'):
                self.v_powersupply_startingcurrent2.set(self.glitchy_data.get_parameter('powersupply_ch2_curr_set'))
            if self.v_powersupply_ch1_enable != self.glitchy_data.get_parameter('powersupply_ch1_enable'):
                self.v_powersupply_ch1_enable.set(self.glitchy_data.get_parameter('powersupply_ch1_enable'))
            if self.v_powersupply_ch2_enable != self.glitchy_data.get_parameter('powersupply_ch2_enable'):
                self.v_powersupply_ch2_enable.set(self.glitchy_data.get_parameter('powersupply_ch2_enable'))

        def update_chipwhisperer_calculated_fields():
            speed = self.v_cw_speed.get()
            glitch_cycles = self.v_cw_glitchcycles.get()
            cycles_after_trigger = self.v_cw_cyclesaftertrigger.get()

            # Exit if non-digits in the speed field
            if speed.replace('.', '', 1).isdigit() is False:
                return
            # Exit if speed evaluates to zero, div by zero error below
            if int(speed.replace('.', '', 1)) == 0:
                return

            if glitch_cycles.isnumeric() is False:
                glitch_cycles = ''

            if cycles_after_trigger.isnumeric() is False:
                cycles_after_trigger = ''

            if glitch_cycles == '':
                self.v_cw_glitch_calctime.set("-------")
                self.v_cw_trigger_calctime.set("-------")
                self.builder.get_object('e_cw_cyclesaftertrigger')['state'] = 'disabled'
                return
            else:
                self.builder.get_object('e_cw_cyclesaftertrigger')['state'] = 'normal'

            if cycles_after_trigger == '':
                self.v_cw_trigger_calctime.set("-------")
            else:
                trigger_time = str(((1 / (float(speed) * 1000000)) * (int(cycles_after_trigger) + 7)))
                self.v_cw_trigger_calctime.set(str(Quantity(trigger_time, 's')))

            glitch_time = str(((1 / (float(speed) * 1000000)) * int(glitch_cycles)))
            self.v_cw_glitch_calctime.set(str(Quantity(glitch_time, 's')))

        def update_automated_glitch():
            # Add code here to refresh data on automated glitch screen from Data Model
            # automated_glitch() will be changing values and updating Data Model
            while self.glitchyController.glitchy_data.is_empty("automated_glitch_log") is False:
                data, command = self.glitchyController.glitchy_data.dequeue("automated_glitch_log")
                if command != "":
                    command = command.split(",")
                else:
                    self.automated_glitch_text_box.insert(tk.END, data)
                    self.automated_glitch_text_box.see(tk.END)
                    return

            if self.glitchy_data.get_parameter("glitchtime_currentvalue") is not None:
                self.glitchtime_currentvalue.set(self.glitchy_data.get_parameter("glitchtime_currentvalue"))
            else:
                self.glitchtime_currentvalue.set("---------")

            if self.glitchy_data.get_parameter("glitchstrength_currentvalue") is not None:
                self.glitchstrength_currentvalue.set(self.glitchy_data.get_parameter("glitchstrength_currentvalue"))
            else:
                self.glitchstrength_currentvalue.set("---------")

            if self.glitchy_data.get_parameter("glitchcounter_triggered") is not None:
                self.glitchcounter_triggered.set(self.glitchy_data.get_parameter("glitchcounter_triggered"))
            else:
                self.glitchcounter_triggered.set("---------")

            if self.glitchy_data.get_parameter("glitchcounter_missed") is not None:
                self.glitchcounter_missed.set(self.glitchy_data.get_parameter("glitchcounter_missed"))
            else:
                self.glitchcounter_missed.set("---------")

            self.progressbar_time.set(self.glitchy_data.get_parameter("progressbar_time"))
            self.progressbar_strength.set(self.glitchy_data.get_parameter("progressbar_strength"))
            self.progressbar_overall.set(self.glitchy_data.get_parameter("progressbar_overall"))

        # -----------------------------------------------------
        # If we are running an automated glitch then don't read from the power supply,
        # this delays the glitching routine and could cause other issues.
        if self.glitchyController.glitcher_running:
            update_automated_glitch()
            update_serial_logging()
            if self.glitchyController.glitcher_success is True:
                self.glitchyController.glitcher_success = False
                print("Glitcher Success!!")
                messagebox.showinfo(title="SUCCESS!", message="Post-Glitch Event Found!\nGlitching Paused.")
        # -----------------------------------------------------
        else:
            update_serial_logging()
            update_automated_glitch()
            update_chipwhisperer_calculated_fields()
            update_powersupply_measurements()
            if self.glitchyController.powersupply.is_changed():
                update_powersupply_setvalues()
        self.mainwindow.after(200, self.update_values)

    def update_data_model(self):
        parameters = {
            # 'v_GlitchTriggerName': self.v_GlitchTriggerName.get(),
            'pre_event_1': self.pre_event_1.get(),
            'pre_event_2': self.pre_event_2.get(),
            'pre_event_3': self.pre_event_3.get(),
            'pre_option_1': self.pre_option_1.get(),
            'pre_option_2': self.pre_option_2.get(),
            'pre_option_3': self.pre_option_3.get(),
            'pre_delay_1': self.pre_delay_1.get(),
            'pre_delay_2': self.pre_delay_2.get(),
            'pre_delay_3': self.pre_delay_3.get(),
            'GlitchTimeStart': self.glitchtime_startvalue.get(),
            'GlitchTimeStop': self.glitchtime_stopvalue.get(),
            'GlitchTimeStepSize': self.glitchtime_stepvalue.get(),
            'GlitchStrengthStart': self.glitchstrength_startvalue.get(),
            'GlitchStrengthStop': self.glitchstrength_stopvalue.get(),
            'GlitchStrengthStepSize': self.glitchstrength_stepvalue.get(),
            'post_event_1': self.post_event_1.get(),
            'post_event_2': self.post_event_2.get(),
            'post_event_3': self.post_event_3.get(),
            'post_option_1': self.post_option_1.get(),
            'post_option_2': self.post_option_2.get(),
            'post_option_3': self.post_option_3.get(),
            'post_delay_1': self.post_delay_1.get(),
            'post_delay_2': self.post_delay_2.get(),
            'post_delay_3': self.post_delay_3.get(),
            'cw_cyclesaftertrigger': self.v_cw_cyclesaftertrigger.get(),
            'cw_glitchcycles': self.v_cw_glitchcycles.get(),
            'cw_speed': self.v_cw_speed.get(),
            'cw_source': self.v_cw_source.get(),
            'cw_glitchtimeout': self.v_cw_glitchtimeout.get(),
            'cw_mosfet': self.v_cw_mosfet.get(),
            'powersupply_ipaddr': self.v_powersupply_ipaddr.get(),
            'powersupply_port': self.v_powersupply_port.get(),
            'powersupply_ch1_volt_set': self.v_powersupply_startingvoltage1.get(),
            'powersupply_ch2_volt_set': self.v_powersupply_startingvoltage2.get(),
            'powersupply_ch1_curr_set': self.v_powersupply_startingcurrent1.get(),
            'powersupply_ch2_curr_set': self.v_powersupply_startingcurrent2.get(),
            'powersupply_ch1_enable': self.v_powersupply_ch1_enable.get(),
            'powersupply_ch2_enable': self.v_powersupply_ch2_enable.get(),
            'sp_port': self.v_serialport_serialport.get(),
            'sp_speed': self.v_serialport_speed.get(),
            'sp_databits': self.v_serialport_databits.get(),
            'sp_stopbits': self.v_serialport_stopbits.get(),
            'sp_parity': self.v_serialport_parity.get(),
            'sp_flowcontrol': self.v_serialport_flowcontrol.get(),
            "sp_tx1": self.v_serial_txmsg1.get(),
            "sp_tx2": self.v_serial_txmsg2.get(),
            "sp_tx3": self.v_serial_txmsg3.get(),
            "sp_tx4": self.v_serial_txmsg4.get(),
            "sp_flood_timeout": self.v_serial_flood_timeout.get(),
            "sp_flood_capturesize": self.v_serial_flood_capturesize.get(),
            "sp_flood_datarate": self.v_serial_flood_datarate.get(),
            'debug_adaptor': self.v_debug_adaptor.get(),
            'debug_target': self.v_debug_target.get(),
            'debug_halt': self.v_debug_halt.get(),
            'debug_commands': self.v_debug_commands.get()}
        for key in parameters:
            self.glitchy_data.set_parameter(key, parameters[key])
        # print(self.glitchy_data.parameters)

    def close(self):
        return

    def videohelp_automatedglitch(self, event=None):
        messagebox.showinfo(title="Coming Soon",
                            message="Videos will be released after a few more features are implemented.")
        # self.glitchyController.videohelp(topic="Automated Glitch")

    def videohelp_chipwhisperer(self, event=None):
        messagebox.showinfo(title="Coming Soon",
                            message="Videos will be released after a few more features are implemented.")
        # self.glitchyController.videohelp(topic="Chipwhisperer")

    def videohelp_powersupply(self, event=None):
        messagebox.showinfo(title="Coming Soon",
                            message="Videos will be released after a few more features are implemented.")
        # self.glitchyController.videohelp(topic="Power Supply")

    def videohelp_serial(self, event=None):
        messagebox.showinfo(title="Coming Soon",
                            message="Videos will be released after a few more features are implemented.")
        # self.glitchyController.videohelp(topic="Serial")

    def videohelp_debugger(self, event=None):
        messagebox.showinfo(title="Coming Soon",
                            message="Videos will be released after a few more features are implemented.")
        # self.glitchyController.videohelp(topic="JTAG")

    def save_file(self):
        parameters = {
            # 'v_GlitchTriggerName': self.v_GlitchTriggerName.get(),
            'pre_event_1': self.pre_event_1.get(),
            'pre_event_2': self.pre_event_2.get(),
            'pre_event_3': self.pre_event_3.get(),
            'pre_option_1': self.pre_option_1.get(),
            'pre_option_2': self.pre_option_2.get(),
            'pre_option_3': self.pre_option_3.get(),
            'pre_delay_1': self.pre_delay_1.get(),
            'pre_delay_2': self.pre_delay_2.get(),
            'pre_delay_3': self.pre_delay_3.get(),
            'GlitchTimeStart': self.glitchtime_startvalue.get(),
            'GlitchTimeStop': self.glitchtime_stopvalue.get(),
            'GlitchTimeStepSize': self.glitchtime_stepvalue.get(),
            'GlitchStrengthStart': self.glitchstrength_startvalue.get(),
            'GlitchStrengthStop': self.glitchstrength_stopvalue.get(),
            'GlitchStrengthStepSize': self.glitchstrength_stepvalue.get(),
            'post_event_1': self.post_event_1.get(),
            'post_event_2': self.post_event_2.get(),
            'post_event_3': self.post_event_3.get(),
            'post_option_1': self.post_option_1.get(),
            'post_option_2': self.post_option_2.get(),
            'post_option_3': self.post_option_3.get(),
            'post_delay_1': self.post_delay_1.get(),
            'post_delay_2': self.post_delay_2.get(),
            'post_delay_3': self.post_delay_3.get(),
            'cw_cyclesaftertrigger': self.v_cw_cyclesaftertrigger.get(),
            'cw_glitchcycles': self.v_cw_glitchcycles.get(),
            'cw_speed': self.v_cw_speed.get(),
            'cw_source': self.v_cw_source.get(),
            'cw_glitchtimeout': self.v_cw_glitchtimeout.get(),
            'cw_mosfet': self.v_cw_mosfet.get(),
            'powersupply_ipaddr': self.v_powersupply_ipaddr.get(),
            'powersupply_port': self.v_powersupply_port.get(),
            'powersupply_ch1_volt_set': self.v_powersupply_startingvoltage1.get(),
            'powersupply_ch2_volt_set': self.v_powersupply_startingvoltage2.get(),
            'powersupply_ch1_curr_set': self.v_powersupply_startingcurrent1.get(),
            'powersupply_ch2_curr_set': self.v_powersupply_startingcurrent2.get(),
            'powersupply_ch1_enable': self.v_powersupply_ch1_enable.get(),
            'powersupply_ch2_enable': self.v_powersupply_ch2_enable.get(),
            'powersupply_ch1_toggle': self.v_powersupply_toggle1.get(),
            'powersupply_ch2_toggle': self.v_powersupply_toggle2.get(),
            'sp_port': self.v_serialport_serialport.get(),
            'sp_speed': self.v_serialport_speed.get(),
            'sp_databits': self.v_serialport_databits.get(),
            'sp_stopbits': self.v_serialport_stopbits.get(),
            'sp_parity': self.v_serialport_parity.get(),
            'sp_flowcontrol': self.v_serialport_flowcontrol.get(),
            "sp_tx1": self.v_serial_txmsg1.get(),
            "sp_tx2": self.v_serial_txmsg2.get(),
            "sp_tx3": self.v_serial_txmsg3.get(),
            "sp_tx4": self.v_serial_txmsg4.get(),
            "sp_rx1": self.v_serial_rxmsg1.get(),
            "sp_rx2": self.v_serial_rxmsg2.get(),
            "sp_rx3": self.v_serial_rxmsg3.get(),
            "sp_rx4": self.v_serial_rxmsg4.get(),
            "sp_rxtimeout": self.v_serial_rx_test_timeout.get(),
            "sp_flood_timeout": self.v_serial_flood_timeout.get(),
            "sp_flood_capturesize": self.v_serial_flood_capturesize.get(),
            "sp_flood_datarate": self.v_serial_flood_datarate.get(),
            'debug_adaptor': self.v_debug_adaptor.get(),
            'debug_target': self.v_debug_target.get(),
            'debug_halt': self.v_debug_halt.get(),
            'debug_commands': self.v_debug_commands.get()}

        file_data = asksaveasfile(initialfile='Config.glitchy', defaultextension=".glitchy",
                                  filetypes=[("Glitchy Config Files", "*.glitchy"), ("All Files", "*.*")])
        if file_data is not None:
            self.glitchyController.save_file(parameters, file_data)

    def open_file(self):
        def load_values_into_interface():
            # Load saved values into pre-glitch boxes and populate their options
            self.pre_event_1.set(self.glitchy_data.get_parameter("pre_event_1"))
            self.triggering_events_handler(1)
            self.pre_option_1.set(self.glitchy_data.get_parameter("pre_option_1"))
            self.v_pre_delay_1.set(self.glitchy_data.get_parameter("pre_delay_1"))

            self.pre_event_2.set(self.glitchy_data.get_parameter("pre_event_2"))
            self.triggering_events_handler(2)
            self.pre_option_2.set(self.glitchy_data.get_parameter("pre_option_2"))
            self.v_pre_delay_2.set(self.glitchy_data.get_parameter("pre_delay_2"))

            self.pre_event_3.set(self.glitchy_data.get_parameter("pre_event_3"))
            self.triggering_events_handler(3)
            self.pre_option_3.set(self.glitchy_data.get_parameter("pre_option_3"))
            self.v_pre_delay_3.set(self.glitchy_data.get_parameter("pre_delay_3"))
            # ---------------------------------------------------------------------

            # Load saved values into post-glitch boxes and populate their options
            self.post_event_1.set(self.glitchy_data.get_parameter("post_event_1"))
            self.post_glitch_handler(1)
            self.post_option_1.set(self.glitchy_data.get_parameter("post_option_1"))
            self.v_post_delay_1.set(self.glitchy_data.get_parameter("post_delay_1"))

            self.post_event_2.set(self.glitchy_data.get_parameter("post_event_2"))
            self.post_glitch_handler(2)
            self.post_option_2.set(self.glitchy_data.get_parameter("post_option_2"))
            self.v_post_delay_2.set(self.glitchy_data.get_parameter("post_delay_2"))

            self.post_event_3.set(self.glitchy_data.get_parameter("post_event_3"))
            self.post_glitch_handler(3)
            self.post_option_3.set(self.glitchy_data.get_parameter("post_option_3"))
            self.v_post_delay_3.set(self.glitchy_data.get_parameter("post_delay_3"))
            # ---------------------------------------------------------------------

            self.glitchtime_startvalue.set(self.glitchy_data.get_parameter("GlitchTimeStart"))
            self.glitchtime_stopvalue.set(self.glitchy_data.get_parameter("GlitchTimeStop"))
            self.glitchstrength_startvalue.set(self.glitchy_data.get_parameter("GlitchStrengthStart"))
            self.glitchstrength_stopvalue.set(self.glitchy_data.get_parameter("GlitchStrengthStop"))
            self.glitchtime_stepvalue.set(self.glitchy_data.get_parameter("GlitchTimeStepSize"))
            self.glitchstrength_stepvalue.set(self.glitchy_data.get_parameter("GlitchStrengthStepSize"))
            self.v_cw_cyclesaftertrigger.set(self.glitchy_data.get_parameter("cw_cyclesaftertrigger"))
            self.v_cw_glitchcycles.set(self.glitchy_data.get_parameter("cw_glitchcycles"))
            self.v_cw_glitchtimeout.set(self.glitchy_data.get_parameter("cw_glitchtimeout"))
            self.v_cw_speed.set(self.glitchy_data.get_parameter("cw_speed"))
            self.v_cw_source.set(self.glitchy_data.get_parameter("cw_source"))
            self.v_cw_mosfet.set(self.glitchy_data.get_parameter("cw_mosfet"))
            self.v_powersupply_ipaddr.set(self.glitchy_data.get_parameter("powersupply_ipaddr"))
            self.v_powersupply_port.set(self.glitchy_data.get_parameter("powersupply_port"))
            self.v_powersupply_startingvoltage1.set(self.glitchy_data.get_parameter("powersupply_ch1_volt_set"))
            self.v_powersupply_startingvoltage2.set(self.glitchy_data.get_parameter("powersupply_ch2_volt_set"))
            self.v_powersupply_startingcurrent1.set(self.glitchy_data.get_parameter("powersupply_ch1_curr_set"))
            self.v_powersupply_startingcurrent2.set(self.glitchy_data.get_parameter("powersupply_ch2_curr_set"))
            self.v_powersupply_ch1_enable.set(bool(self.glitchy_data.get_parameter("powersupply_ch1_enable")))
            self.v_powersupply_ch2_enable.set(bool(self.glitchy_data.get_parameter("powersupply_ch2_enable")))
            self.v_powersupply_toggle1.set(self.glitchy_data.get_parameter("powersupply_ch1_toggle"))
            self.v_powersupply_toggle2.set(self.glitchy_data.get_parameter("powersupply_ch2_toggle"))
            self.v_serialport_serialport.set(self.glitchy_data.get_parameter("sp_port"))
            self.v_serialport_speed.set(self.glitchy_data.get_parameter("sp_speed"))
            self.v_serialport_databits.set(self.glitchy_data.get_parameter("sp_databits"))
            self.v_serialport_stopbits.set(self.glitchy_data.get_parameter("sp_stopbits"))
            self.v_serialport_parity.set(self.glitchy_data.get_parameter("sp_parity"))
            self.v_serialport_flowcontrol.set(self.glitchy_data.get_parameter("sp_flowcontrol"))
            self.v_serial_txmsg1.set(self.glitchy_data.get_parameter("sp_tx1"))
            self.v_serial_txmsg2.set(self.glitchy_data.get_parameter("sp_tx2"))
            self.v_serial_txmsg3.set(self.glitchy_data.get_parameter("sp_tx3"))
            self.v_serial_txmsg4.set(self.glitchy_data.get_parameter("sp_tx4"))
            self.v_serial_rxmsg1.set(self.glitchy_data.get_parameter("sp_rx1"))
            self.v_serial_rxmsg2.set(self.glitchy_data.get_parameter("sp_rx2"))
            self.v_serial_rxmsg3.set(self.glitchy_data.get_parameter("sp_rx3"))
            self.v_serial_rxmsg4.set(self.glitchy_data.get_parameter("sp_rx4"))
            self.v_serial_rx_test_timeout.set(self.glitchy_data.get_parameter("sp_rxtimeout"))
            self.v_serial_flood_datarate.set(self.glitchy_data.get_parameter("sp_flood_datarate"))
            self.v_serial_flood_capturesize.set(self.glitchy_data.get_parameter("sp_flood_capturesize"))
            self.v_serial_flood_timeout.set(self.glitchy_data.get_parameter("sp_flood_timeout"))
            self.v_debug_adaptor.set(self.glitchy_data.get_parameter("debug_adaptor"))
            self.v_debug_target.set(self.glitchy_data.get_parameter("debug_target"))
            self.v_debug_halt.set(self.glitchy_data.get_parameter("debug_halt"))
            self.v_debug_commands.set(self.glitchy_data.get_parameter("debug_commands"))
        file_data = askopenfile(defaultextension=".json",
                                filetypes=[("Glitchy Config Files", "*.glitchy"), ("All Files", "*.*")])
        if file_data is not None:
            self.glitchyController.open_file(load_file=file_data)
            load_values_into_interface()
        else:
            return

    def powersupply_connect(self):
        try:
            self.glitchyController.powersupply.connect(self.v_powersupply_ipaddr.get(),
                                                       self.v_powersupply_port.get())
        except Exception as e:
            if e.__class__.__name__ == 'timeout':
                showerror(title='Power Supply', message="Connection timed out.")
            elif e.__class__.__name__ == 'gaierror':
                showerror(title='Power Supply', message="Invalid IP address.")
            else:
                showerror(title='Power Supply', message=e.__class__.__name__)
            return
        self.btn_ps_disconnect['state'] = 'normal'
        self.btn_ps_connect['state'] = 'disabled'
        self.btn_ps_set1['state'] = 'normal'
        self.btn_ps_set2['state'] = 'normal'
        self.btn_ps_toggle1['state'] = 'normal'
        self.btn_ps_toggle2['state'] = 'normal'

    def powersupply_disconnect(self):
        self.glitchyController.powersupply.disconnect()
        self.btn_ps_disconnect['state'] = 'disabled'
        self.btn_ps_connect['state'] = 'normal'
        self.btn_ps_set1['state'] = 'disabled'
        self.btn_ps_set2['state'] = 'disabled'
        self.btn_ps_toggle1['state'] = 'disabled'
        self.btn_ps_toggle2['state'] = 'disabled'

    def powersupply_set_button(self, widget_id):
        if widget_id == 'btn_powersupply_set1':
            self.glitchyController.powersupply.set_settings(
                ch1_en=self.v_powersupply_ch1_enable.get(), ch2_en=None,
                ch1_volt=self.v_powersupply_startingvoltage1.get(), ch2_volt='',
                ch1_curr=self.v_powersupply_startingcurrent1.get(), ch2_curr='')
        elif widget_id == 'btn_powersupply_set2':
            self.glitchyController.powersupply.set_settings(
                ch1_en=None, ch2_en=self.v_powersupply_ch2_enable.get(),
                ch1_volt='', ch2_volt=self.v_powersupply_startingvoltage2.get(),
                ch1_curr='', ch2_curr=self.v_powersupply_startingcurrent2.get())
        else:
            return

    def powersupply_toggle_button(self, widget_id):
        if widget_id == 'btn_powersupply_toggle1':
            self.btn_ps_toggle1['state'] = 'disabled'
            toggle1_time = self.v_powersupply_toggle1.get()
            self.glitchyController.powersupply.config_toggle_time(ch1=toggle1_time)
            self.glitchyController.powersupply.set_toggle(channel="1")
            self.glitchyController.powersupply.trigger_toggle()
            time.sleep(float(toggle1_time)+2.0)
            self.btn_ps_toggle1['state'] = 'normal'
        elif widget_id == 'btn_powersupply_toggle2':
            print("Toggle 2 pressed")
            self.btn_ps_toggle2['state'] = 'disabled'
            toggle2_time = self.v_powersupply_toggle2.get()
            self.glitchyController.powersupply.config_toggle_time(ch2=toggle2_time)
            self.glitchyController.powersupply.set_toggle(channel="2")
            self.glitchyController.powersupply.trigger_toggle()
            time.sleep(float(toggle2_time)+2.0)
            print("Toggle 2 complete")
            self.btn_ps_toggle2['state'] = 'normal'

    def serial_connect(self):
        if self.glitchyController.serial.connect(
                port=self.v_serialport_serialport.get(),
                baudrate=int(self.v_serialport_speed.get()),
                bytesize=int(self.v_serialport_databits.get()),
                stopbits=int(self.v_serialport_stopbits.get()),
                parity='N', timeout=1):
            if __debug__:
                print("Serial Port Connected.")
            # Connected, setup buttons
            self.btn_ser_disconnect['state'] = 'normal'
            self.btn_ser_connect['state'] = 'disabled'
            self.btn_ser_send1['state'] = 'normal'
            self.btn_ser_send2['state'] = 'normal'
            self.btn_ser_send3['state'] = 'normal'
            self.btn_ser_send4['state'] = 'normal'
            self.btn_ser_receive1['state'] = 'normal'
            self.btn_ser_receive2['state'] = 'normal'
            self.btn_ser_receive3['state'] = 'normal'
            self.btn_ser_receive4['state'] = 'normal'
        else:
            messagebox.showerror(title="Serial Error")

    def serial_disconnect(self):
        if self.glitchyController.serial.disconnect():
            self.btn_ser_disconnect['state'] = 'disabled'
            self.btn_ser_connect['state'] = 'normal'
            self.btn_ser_send1['state'] = 'disabled'
            self.btn_ser_send2['state'] = 'disabled'
            self.btn_ser_send3['state'] = 'disabled'
            self.btn_ser_send4['state'] = 'disabled'
            self.btn_ser_receive1['state'] = 'disabled'
            self.btn_ser_receive2['state'] = 'disabled'
            self.btn_ser_receive3['state'] = 'disabled'
            self.btn_ser_receive4['state'] = 'disabled'

    def serial_transmit(self, event=None):
        tx_message = None
        if event == 'btn_ser_send1':
            tx_message = self.v_serial_txmsg1.get()
        elif event == 'btn_ser_send2':
            tx_message = self.v_serial_txmsg2.get()
        elif event == 'btn_ser_send3':
            tx_message = self.v_serial_txmsg3.get()
        elif event == 'btn_ser_send4':
            tx_message = self.v_serial_txmsg4.get()
        else:
            print("Don't know how we got here...")

        if tx_message:
            self.glitchyController.serial_tx(tx_message)
        else:
            messagebox.showerror(title="Serial Warning", message="Field empty or formatted incorrectly.")

    def serial_receive_test(self, widget_id):
        """
        Currently this function is blocking so the whole app freezes while waiting to RX data.

        Should probably start a thread for the receive function.
        """
        rx_message = None
        message_num = None
        rx_timeout = self.v_serial_rx_test_timeout.get()
        if rx_timeout != '':
            rx_timeout = float(rx_timeout)
        else:
            rx_timeout = None  # Wait FOREVER!
        self.v_serial_rx_test_status.set("")

        if widget_id == 'btn_ser_receive1':
            rx_message = self.v_serial_rxmsg1.get()
            message_num = 1
        elif widget_id == 'btn_ser_receive2':
            rx_message = self.v_serial_rxmsg2.get()
            message_num = 2
        elif widget_id == 'btn_ser_receive3':
            rx_message = self.v_serial_rxmsg3.get()
            message_num = 3
        elif widget_id == 'btn_ser_receive4':
            rx_message = self.v_serial_rxmsg4.get()
            message_num = 4
        elif widget_id == 'btn_ser_receive_stop':
            # Set flag here that stops the serial receive thread
            self.glitchyController.serial_rx_stop()
        else:
            print("Don't know how we got here...")

        if rx_message:
            # Returns -1 for no match upon timeout, 0 or greater for match location in string received
            value = self.glitchyController.serial_rx_match(rx_message, timeout=rx_timeout, size=None)
            if value > -1:
                self.v_serial_rx_test_status.set(f"RX Message {message_num} found!")
            else:
                self.v_serial_rx_test_status.set(f"RX Message {message_num} not found before timeout.")
            return

    def cw_configure(self):
        """ Reconfigure entire chipwhisperer each time this button is clicked

        Get values from ChipWhisperer tab (Settings) and configure chipwhisperer
        """

        # Get values from GUI interface
        source = self.v_cw_source.get()
        speed = float(self.v_cw_speed.get()) * 1e6
        mosfet = self.v_cw_mosfet.get()
        # Configure chipwhisperer
        try:
            self.glitchyController.cw.configure(speed, source, mosfet)
        except Exception as e:
            if e.__class__.__name__ == 'OSError':
                messagebox.showerror(title="Error", message="ChipWhisperer not detected.")
            if e.__class__.__name__ == 'USBErrorBusy':
                messagebox.showerror(title="Error", message="ChipWhisperer already connected to another program. :(")
            return
        self.run_button['state'] = 'normal'
        self.glitch_button['state'] = 'normal'
        self.io_button['state'] = 'normal'
        self.print_settings_button['state'] = 'normal'

    def cw_io(self):
        self.glitchyController.cw.trigger(trigger_type="High, Low, HiZ")

    def cw_print_settings(self):
        self.glitchyController.cw.print_settings()

    def cw_glitch(self):
        """ Called when the Glitch button is pressed.

            Takes setting values and starts a new thread so long delays don't freeze the program
        """

        def cw_glitch_helper():
            self.glitch_button['state'] = 'disabled'
            self.io_button['state'] = 'disabled'
            if trigger_time:
                self.v_cw_glitchstatus.set("Waiting for Trigger")
            else:
                self.v_cw_glitchstatus.set("Glitching")

            if self.glitchyController.cw.glitch(trigger_time, timeout, glitch_width):
                self.v_cw_glitchstatus.set("Glitched!")
            else:
                self.v_cw_glitchstatus.set("Timed Out")
            self.glitch_button['state'] = 'normal'
            self.io_button['state'] = 'normal'

        trigger_time = self.v_cw_cyclesaftertrigger.get()
        if trigger_time == '':
            trigger_time = 0
        else:
            trigger_time = int(trigger_time)
        timeout = float(self.v_cw_glitchtimeout.get())

        glitch_width = int(self.v_cw_glitchcycles.get())
        glitch_thread = Thread(target=cw_glitch_helper)
        glitch_thread.start()

    # Automated Glitch Routines
    def glitch_run(self):
        # Code here prepares variables for automated_glitch()
        # by placing everything in the data model
        self.update_data_model()
        # Code here starts an automated_glitch thread
        glitching_routine = Thread(target=self.glitchyController.automated_glitch)
        glitching_routine.daemon = True
        glitching_routine.start()

        # Code here changes state of buttons
        self.run_button['state'] = 'disabled'
        self.pause_button['state'] = 'normal'
        self.stop_button['state'] = 'normal'
        # End of glitch_run

    def glitch_pause(self):
        # Code here signals to automated_glitch() to pause
        self.update_data_model()
        self.glitchyController.glitcher_pause = not self.glitchyController.glitcher_pause
        pass

    def glitch_stop(self):
        # Code here signals to automated_glitch() to stop and clean up
        self.glitchyController.glitcher_stop = True
        self.run_button['state'] = 'normal'
        self.pause_button['state'] = 'disabled'
        self.stop_button['state'] = 'disabled'
        pass

    def debug_connect(self):
        messagebox.showinfo(title="Coming Soon",
                            message="This feature isn't implemented yet, it's next on the list though!")
        pass

    def debug_disconnect(self):
        pass

    def browse_debug_config(self, widget_id):
        if widget_id == "Adaptor_Config":
            file = askopenfile(title="Open Adaptor Config", mode='r', filetypes=[('Config Files', '*.cfg')])
            if file:
                filepath = os.path.abspath(file.name)
                self.v_debug_adaptor.set(str(filepath))
            else:
                return
        elif widget_id == "Target_Config":
            file = askopenfile(title="Open Target Config", mode='r', filetypes=[('Config Files', '*.cfg')])
            if file:
                filepath = os.path.abspath(file.name)
                self.v_debug_target.set(str(filepath))
            else:
                return

