


class Event:
  def __init__(self, channel, start,  duration=1000, 
               rgbwt_start  = {"r": None, "g": None, "b": None, "w": None, "t": None, "m": None},
               rgbwt_target = {"r": None, "g": None, "b": None, "w": None, "t": None, "m": None}
               ):
    """
    Color change Event. Will calculate colors and ease them for a RGBWChannel object
    
    :channel: RGBWChannel object targeted.
    :start: Int | Starting point. (in milliseconds since bootup)
    :duration: Int | duration in milliseconds
    
    Next value can contains None. None will be replaced by current RGBW value at event start. 
    :rgbwt_start:  Dict | Starting Red, green, blue, white and temperature 
    :rgbwt_target: Dict | Targeted Red, green, blue, white and temperature 
    
    :easing: Class Method | Easing function (math provided by https://github.com/danro/jquery-easing/blob/master/jquery.easing.js
    
    """
    
    self.channel = channel
    self.start = start
    self.duration = duration
    self.active = False
    self.rgbwt_start = {"r": None, "g": None, "b": None, "w": None, "t": None, "m": None}
    self.rgbwt_target = {"r": None, "g": None, "b": None, "w": None, "t": None, "m": None}
    self.rgbwt_start.update(rgbwt_start)
    self.rgbwt_target.update(rgbwt_target)
    self.easing = self.easeInOutQuad

  
  def initiate(self):
    for key in self.channel.values:
      self.rgbwt_start[key] = self.channel.values[key] if self.rgbwt_start[key] is None else self.rgbwt_start[key]
      self.rgbwt_target[key] = self.channel.values[key] if self.rgbwt_target[key] is None else self.rgbwt_target[key]
    self.active = True
  
  def get_status(self, t):
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
    if self.duration == 0:
      self.duration = 1
    new_value = self.rgbwt_start[key] + (self.rgbwt_target[key]  - self.rgbwt_start[key]) * self.easing((t - self.start) / self.duration)
  
    if new_value is None:
      print("{} is none !".format(key))
      
    return new_value
  
  # Easing functions   
  def easeInOutQuad(self, t):
    return 2*t*t if t < 0.5 else -1+(4-2*t)*t
    
  """
  easeInOutCubic: t => t<.5 ? 4*t*t*t : (t-1)*(2*t-2)*(2*t-2)+1,
  // accelerating from zero velocity 
  easeInQuart: t => t*t*t*t,
  // decelerating to zero velocity 
  easeOutQuart: t => 1-(--t)*t*t*t,
  // acceleration until halfway, then deceleration
  easeInOutQuart: t => t<.5 ? 8*t*t*t*t : 1-8*(--t)*t*t*t,
  // accelerating from zero velocity
  easeInQuint: t => t*t*t*t*t,
  // decelerating to zero velocity
  easeOutQuint: t => 1+(--t)*t*t*t*t,
  // acceleration until halfway, then deceleration 
  easeInOutQuint: t => t<.5 ? 16*t*t*t*t*t : 1+16*(--t)*t*t*t*t
  """
  # End easing




