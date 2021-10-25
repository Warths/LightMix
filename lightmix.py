from machine import Pin, PWM
from math import floor
import time
from event import Event
from wandering import WanderingCoefficient


class LightMix:
    def __init__(self):
        """
        Dynamic color mixer
        Programmed throught events
        Manage timed color-change event queue and push them throught the PCA9685.
        """
        self.time_offset = 0
        self.pin_indexes = {
            "r": PWM(Pin(17), freq=78125, duty=0),  # 17
            "g": PWM(Pin(16), freq=78125, duty=0),  # 16
            "b": PWM(Pin(22), freq=78125, duty=0),  # 22
            "w": PWM(Pin(21), freq=78125, duty=0)  # 21
        }

        self.values = {"r": 0, "g": 0, "b": 0, "w": 0}
        self.masters = {"r": 100, "g": 100, "b": 100, "w": 60}
        self.event = None
        self.queue = ""
        self.wanderer = WanderingCoefficient(1000, 1000, 100, 100, 100, 100)

    def set_time_offset(self, client_time):
        """
        Saves client time to handle timed events in sync with client
        :client_time: int
        """
        self.time_offset = client_time - time.ticks_ms()

    def update(self, *args):
        """
        Manages the event queue and wanderer coefficient
        """
        t = time.ticks_ms() + self.time_offset

        if not self.event:
            self.load_new_event()

        if self.event:
            status = self.event.get_status(t)
            # Status 0, Scheduled but not started. Do nothing
            # Status 1, initiating event
            if status == 1:
                # Init event (taking previous colors, current time etc)
                print("Init event {}".format(self.event))
                self.event.initiate(self.values)
            elif status == 2:
                self.compute_event(t)
            # Status 3, ending event
            elif status == 3:
                self.end_event()

        self.update_pwm()

    def load_new_event(self):
        """
        Charge a new event if there is an event in the queue
        """
        if len(self.queue) > 0:
            # Getting new event
            new_event = self.queue.split("#", 1)[0]
            self.queue = self.queue.split("#", 1)[1]
            # Parsing new event from the new_event string
            self.event = self.event_from_string(new_event)

    def end_event(self):
        """
        Set all values to current event target RGBW
        """
        for k in self.values:
            if self.event.rgbwt_target:
                self.values[k] = self.event.rgbwt_target[k]
        print("[LightMix] End event.")
        self.event = None

    def compute_event(self, t):
        """
        Set all values according to the completion rate of the current event
        :t: Int, Current time
        """
        for k in self.values:
            self.values[k] = self.event.apply_ease(k, t)

    def update_pwm(self):
        """
        Update PCA9685 channels, taking wanderer into account
        """
        c = self.wanderer.coefficient

        for k, v in self.values.items():
            self.values[k] = min(max(0, v), 1023)
            duty = int(self.values[k] * (c / 100) * self.masters[k] / 100)
            self.pin_indexes[k].duty(max(5, duty) if duty > 1 else 0)

        # print(self.values)

    def event_from_string(self, parameters):
        """
        Event = "t=500&cs=ffffff&ce=ffffff&d=300"
        COLORS SCHEMES :
        1 x 8bit = White value
        2 x 8bit = Hue + Saturation // TODO
        3 x 8bit = RGB + auto W
        4 x 8bit = RGBW

        t (time)
        cs (colors at start)
        ce (colors at end)
        d (duration)
        k (keylight)
        Returns: List of tuples. Key of value may be empty
        """

        formatted_parameters = []
        # Splitting parameters into fragments
        fragments = parameters.split("&")
        # Adding fragments to the returned list
        for frag in fragments:
            key_value = frag.split("=", 1)
            # Parameters doesn't have value
            if len(key_value) == 1:
                formatted_parameters.append((key_value[0], ''))
            # Parameters has value
            else:
                formatted_parameters.append((key_value[0], key_value[1]))

        params = {k: v for k, v in formatted_parameters}

        # Appling all modifiers
        for color in ['cs', 'ce']:
            if color in params:
                # Sanityzing input
                params[color] = self.sanitize_rgbw(params[color])

                # Applying keylight
                if "k" in params:
                    params[color] = self.apply_keylight(params[color], float(params["k"]))

            # Building event dict
            params[color] = {
                "r": self.convert_to_10_bit(int("0x" + params[color][0:2])) if color in params else None,
                "g": self.convert_to_10_bit(int("0x" + params[color][2:4])) if color in params else None,
                "b": self.convert_to_10_bit(int("0x" + params[color][4:6])) if color in params else None,
                "w": self.convert_to_10_bit(int("0x" + params[color][6:8])) if color in params else None,
            }

        # Computing starting time
        start_time = int(params["t"]) if 't' in params else self.time_offset + time.ticks_ms()

        # Defining duration
        if "d" in params:
            duration = int(params["d"])
        else:
            duration = 1

        return Event(start_time, duration, params["cs"], params["ce"])

    def convert_to_10_bit(self, value):
        return value * 4 + floor(value / 4)

    def sanitize_rgbw(self, value):
        # Truncating
        while len(value) > 8:
            value = value[:-1]

        # Case 1x 8bit (white)
        if len(value) == 2:
            value = "000000" + value

        # Case 2x 8bit (Hue/Saturation)
        elif len(value) == 4:
            pass  # TODO Implement Hue Saturation support

        if len(value) == 6:
            # Auto White
            w = "00"
            if value[0:2] == value[2:4] and value[2:4] == value[4:6]:
                w = value[0:2]
                value = "000000"
            value = value + w

        return value

    def sanitize_rgbw(self, value):
        # Truncating
        while len(value) > 8:
            value = value[:-1]

        # Case 1x 8bit (white)
        if len(value) == 2:
            value = "000000" + value

        # Case 2x 8bit (Hue/Saturation)
        elif len(value) == 4:
            pass  # TODO Implement Hue Saturation support

        if len(value) == 6:
            # Auto White
            w = "00"
            if value[0:2] == value[2:4] and value[2:4] == value[4:6]:
                w = value[0:2]
                value = "000000"
            value = value + w

        return value

    def apply_keylight(self, value, keylight):
        value = {
            "r": int("0x{}".format(value[0:2]), 16),
            "g": int("0x{}".format(value[2:4]), 16),
            "b": int("0x{}".format(value[4:6]), 16),
            "w": int("0x{}".format(value[6:8]), 16)
        }

        keylight_amount = int((value["r"] + value["g"] + value["b"]) / 3 * keylight)
        value["w"] = min(255, value["w"] + keylight_amount)

        value = {
            "r": hex(value["r"])[2:],
            "g": hex(value["g"])[2:],
            "b": hex(value["b"])[2:],
            "w": hex(value["w"])[2:]
        }

        value = "{}{}{}{}".format(
            value["r"] if len(value["r"]) == 2 else "0" + value["r"],
            value["g"] if len(value["g"]) == 2 else "0" + value["g"],
            value["b"] if len(value["b"]) == 2 else "0" + value["b"],
            value["w"] if len(value["w"]) == 2 else "0" + value["w"]
        )

        return value
