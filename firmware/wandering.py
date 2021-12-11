import time
import urandom


class WanderingCoefficient:
    def __init__(self, min_ms, max_ms, idle_min_ms, idle_max_ms, min_c, max_c=100):
        """
        WanderingCoefficient create a randomized coefficient that wander over time.
        durations are in milliseconds and coefficient in % (0-100)
        :min_ms: minimum slope duration
        :max_ms: maximum slope duration
        :idle_min_ms: minimum idle duration
        :idle_max_ms: maximum idle duration
        :min_c: minimum coefficient
        :max_c: maximum coefficient
        """
        self.min_ms = min_ms
        self.max_ms = max_ms

        self.idle_min_ms = idle_min_ms
        self.idle_max_ms = idle_max_ms

        self.min_c = min_c
        self.max_c = max_c

        self.idle = False

        self._previous_time_target = time.ticks_ms()
        self._previous_coef_target = 100

        # Getting random wandering time and coef
        self._current_time_target = self.generate_time_target()
        self._current_coef_target = self.generate_coef_target()

    def refresh_targets(self):
        """
        Toggle wandering state (idle/slope) and generate new coefs/times
        """
        # Storing previous values for easing purpose
        self._previous_time_target = self._current_time_target
        self._previous_coef_target = self._current_coef_target
        # Toggling state
        if self.idle:
            # Generating new coef and time
            self._current_time_target = self.generate_time_target()
            self._current_coef_target = self.generate_coef_target()
            self.idle = False
        else:
            # Generating new idle time
            self._current_time_target = self.generate_idle_time()
            self.idle = True

    def generate_idle_time(self):
        """
        generate a random value beetween specified idle time range
        """
        return time.ticks_ms() + self.randint(self.idle_min_ms, self.idle_max_ms)

    def generate_time_target(self):
        """
        generate a random value beetween specified slope time range
        """
        return time.ticks_ms() + self.randint(self.min_ms, self.max_ms + 1)

    def generate_coef_target(self):
        """
        generate a random value beetween specified coefficient range
        """
        return self.randint(self.min_c, self.max_c + 1)

    @property
    def coefficient(self):
        """
        Return a coefficient and ensure that the targets gets updated when required
        """
        if self.target_expired:
            self.refresh_targets()
        return self._previous_coef_target + (
                    self._current_coef_target - self._previous_coef_target) * self.easeInOutQuad(self.completion)

    @property
    def target_expired(self):
        """
        checks if current time target has expired
        NOTE: 86400000 is the number of ms in a day.
              This allows avoiding integer overflow
              Which can happen after a few days of runtime.
        :return: Boolean
        """
        print(self.expires_in)
        return not 0 < self.expires_in < 86400000

    @property
    def expires_in(self):
        """
        Return the numbers of MS before target expiration.
        """
        return self._current_time_target - time.ticks_ms()

    @property
    def completion(self):
        """
        Return the completion rate of the current target
        """
        duration = self._current_time_target - self._previous_time_target
        current_time = time.ticks_ms() - self._previous_time_target
        return current_time / duration

    def easeInOutQuad(self, t):
        """
        Mathematical function to get a smooth slope
        """
        return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t

    @staticmethod
    def randint(min_v, max_v):
        """
        Return a random number beetween specified range
        """
        r = urandom.getrandbits(32)
        try:
            m = r % (max_v - min_v)
        except ZeroDivisionError:
            m = 0
        randint = m + min_v
        return randint

