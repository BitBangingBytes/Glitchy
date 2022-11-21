import logging
logger = logging.getLogger(__name__)


class Events:

    def __init__(self):
        self.pre_event_1 = None
        self.pre_event_2 = None
        self.pre_event_3 = None
        self.pre_option_1 = None
        self.pre_option_2 = None
        self.pre_option_3 = None
        self.pre_delay_1 = None
        self.pre_delay_3 = None
        self.pre_delay_2 = None
        self.post_event_1 = None
        self.post_event_2 = None
        self.post_event_3 = None
        self.post_option_1 = None
        self.post_option_2 = None
        self.post_option_3 = None
        self.post_delay_1 = None
        self.post_delay_2 = None
        self.post_delay_3 = None

    def pre_event1_trigger(self, event=None):
        self.triggering_events_handler(event_number=1)
        return

    def pre_event2_trigger(self, event=None):
        self.triggering_events_handler(event_number=2)
        return

    def pre_event3_trigger(self, event=None):
        self.triggering_events_handler(event_number=3)
        return

    def post_event1_trigger(self, event=None):
        self.post_glitch_handler(event_number=1)
        return

    def post_event2_trigger(self, event=None):
        self.post_glitch_handler(event_number=2)
        return

    def post_event3_trigger(self, event=None):
        self.post_glitch_handler(event_number=3)
        return

    def triggering_events_handler(self, event_number):
        event = {1: self.pre_event_1, 2: self.pre_event_2, 3: self.pre_event_3}
        option = {1: self.pre_option_1, 2: self.pre_option_2, 3: self.pre_option_3}
        delay = {1: self.pre_delay_1, 2: self.pre_delay_2, 3: self.pre_delay_3}

        if event_number < 3:
            event[event_number + 1]['state'] = 'readonly'
        match event[event_number].get():
            case 'Power':
                logger.info(f'Power selected for Event {event_number}')
                option[event_number]['state'] = 'readonly'
                option[event_number].set('')
                option[event_number].config(values=['Toggle CH1', 'Toggle CH2', 'Toggle CH1 & CH2'])
                delay[event_number]['state'] = 'normal'
            case 'I/O':
                logger.info(f'I/O selected for Event {event_number}')
                option[event_number]['state'] = 'readonly'
                option[event_number].set('')
                option[event_number].config(values=['High, Low, HiZ', 'Low, High, HiZ',
                                                    'High, Momentary Low', 'Low, Momentary High'])
                delay[event_number]['state'] = 'normal'
            case 'Serial':
                logger.info(f'Serial selected for Event {event_number}')
                option[event_number]['state'] = 'readonly'
                option[event_number].set('')
                option[event_number].config(values=['Send Message 1', 'Send Message 2',
                                                    'Send Message 3', 'Send Message 4'])
                delay[event_number]['state'] = 'normal'
            case _:
                logger.info(f'Nothing selected for Event {event_number}, clear option and delay')
                option[event_number].set('')
                option[event_number]['state'] = 'disabled'
                delay[event_number].delete(0, 'end')
                delay[event_number]['state'] = 'disabled'

    def post_glitch_handler(self, event_number):
        event = {1: self.post_event_1, 2: self.post_event_2, 3: self.post_event_3}
        option = {1: self.post_option_1, 2: self.post_option_2, 3: self.post_option_3}
        delay = {1: self.post_delay_1, 2: self.post_delay_2, 3: self.post_delay_3}

        if event_number < 3:
            event[event_number + 1]['state'] = 'readonly'
        match event[event_number].get():
            case 'Debugger':
                logger.info(f'Debugger selected for Event {event_number}')
                option[event_number]['state'] = 'readonly'
                option[event_number].set('')
                option[event_number].config(values=['Attempt Connection', 'Run Command'])
                delay[event_number]['state'] = 'normal'
            case 'I/O':
                logger.info(f'I/O selected for Event {event_number}')
                option[event_number]['state'] = 'readonly'
                option[event_number].set('')
                option[event_number].config(values=['High, Low, HiZ', 'Low, High, HiZ',
                                                    'High, Momentary Low', 'Low, Momentary High'])
                delay[event_number]['state'] = 'normal'
            case 'Serial':
                logger.info(f'Serial selected for Event {event_number}')
                option[event_number]['state'] = 'readonly'
                option[event_number].set('')
                option[event_number].config(values=['Match Message 1', 'Match Message 2',
                                                    'Match Message 3', 'Match Message 4',
                                                    'Serial Flood'])
                delay[event_number]['state'] = 'normal'
            case _:
                logger.info(f'Nothing selected for Event {event_number}, clear option and delay')
                option[event_number].set('')
                option[event_number]['state'] = 'disabled'
                delay[event_number].delete(0, 'end')
                delay[event_number]['state'] = 'disabled'
