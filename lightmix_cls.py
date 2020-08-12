


import time
from rgbw_channel import RGBWChannel
from event import Event

class LightMix:
  def __init__(self, rPin, gPin, bPin, wwPin, cwPin, channels=1):
    self.pins = {"r": rPin, "g": gPin, "b": bPin, "ww": wwPin, "cw": cwPin}
    self.time_offset = 0
    self.channels = []
    self.initialization(channels)
    
  def initialization(self, channel_amount):
    for i in range(0, channel_amount):
      if i == 0:
        channel = RGBWChannel(i, 
          r=1024, 
          g=1024, 
          b=1024, 
          w=2024, 
          temp=5000, 
          master=100
        )
        channel.events.append(Event(channel, 1000, 2000, rgbwt_target={"r": 0, "g": 0, "b": 0, "w": 0}))
      else:
        channel = RGBWChannel(i, temp=5000)
      self.channels.append(channel)
      

  def set_time_offset(self, client_time):
    self.time_offset = client_time - time.ticks_ms() 
    
    
  def update(self, timer):
    t = time.ticks_ms() + self.time_offset
    values = {"r": [],  "g": [], "b": [], "ww": [], "cw": []}
    
    for channel in self.channels:
      channel.update(t)
      colors = channel.get_colors()
      for k, v in colors.items():
        values[k].append(v)
        
    
    # checking which modification required
    to_change = {}
    for k, v in values.items():
      val = sum(values[k])
      if self.pins[k].duty() != min(max(0, val), 1023):
        to_change[k] = val
   
    
    for k, v in to_change.items():
      self.pins[k].duty(v)
        
    self.log(to_change)
        
        
  def log(self, values):
    something_changed = False
    str_changes = {}
    for k, v in values.items():
      something_changed = True
      str_changes[k] = values[k]
      
    for k, v in self.pins.items():
      if k not in str_changes:
        str_changes[k] = self.pins[k].duty()




