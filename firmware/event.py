class Event:
  def __init__(self, start, duration=1000,
               rgbwt_start={"r": None, "g": None, "b": None, "w": None},
               rgbwt_target={"r": None, "g": None, "b": None, "w": None}
               ):
    """
    Color change Event. Will calculate colors and ease them for a LightMix object
    
    :start: Int | Starting point. (in milliseconds since bootup)
    :duration: Int | duration in milliseconds
    
    Next value can contains None. None will be replaced by current RGBW value at event start. 
    :rgbwt_start:  Dict | Starting Red, green, blue, white and temperature 
    :rgbwt_target: Dict | Targeted Red, green, blue, white and temperature 
    
    math provided by https://github.com/danro/jquery-easing/blob/master/jquery.easing.js
    
    """

    self.start = start
    self.duration = duration
    self.active = False
    self.rgbwt_start = {"r": None, "g": None, "b": None, "w": None}
    self.rgbwt_target = {"r": None, "g": None, "b": None, "w": None}
    self.rgbwt_start.update(rgbwt_start)
    self.rgbwt_target.update(rgbwt_target)

  def initiate(self, pca_values):
    for key in pca_values:
      self.rgbwt_start[key] = pca_values[key] if self.rgbwt_start[key] is None else self.rgbwt_start[key]
      self.rgbwt_target[key] = pca_values[key] if self.rgbwt_target[key] is None else self.rgbwt_target[key]
    self.active = True
    print("Target:")
    print(self.rgbwt_target)

  def get_status(self, t):
    """
    
    """
    if t < self.start:
      return 0
    elif not self.active:
      return 1
    elif self.active and self.start < t < self.start + self.duration:
      return 2
    else:
      return 3

  def apply_ease(self, key, t):
    """
    
    :key: str | start/target key
    :t:   Int | Current time
    """

    # avoid zero-division. This can be done without changing the behaviour
    # as a duration of 0 and 1 will still be the next update cycle
    if self.duration == 0:
      self.duration = 1

    # Preparing variables used in computing new value
    start = self.rgbwt_start[key]

    completion_rate = (t - self.start) / self.duration
    completion_rate = 0 if completion_rate < 0 else 1 if completion_rate > 1 else completion_rate

    coef = self.easing(completion_rate)
    difference = self.rgbwt_target[key] - self.rgbwt_start[key]

    new_value = start + difference * coef
    return new_value

  def easing(self, t):
    """
    Quadratic In/out easing method
    :t: float beetween 0 and 1. Representing completion of the event
    :return: float beetween 0 and 1. Coefficient of easing
    """
    return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t
