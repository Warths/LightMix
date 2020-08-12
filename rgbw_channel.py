

from event import Event

class RGBWChannel:
  def __init__(self, channel, r=255, g=255, b=255, w=255, temp=4500, master=100):
    """
    :r: Int | Red channel
    :g: Int | Green channel
    :b: Int | Blue channel
    :w: Int | White channel
    :temp: Int | in Kelvins, from 3000k to 7000k
    :master:
    """
    self.channel = channel
    self.values = {'r': r, 'g': g, 'b': b, 'w': w, 't': temp, 'm': master}
    self.queue = []
    self.events = []
    
  def get_colors(self):
    temp = (self.values['t'] - 3000) / 40
    m = self.values["m"] / 100
    return {
      "r":  int(min(max(0, self.values["r"]), 1023) * m),
      "g":  int(min(max(0, self.values["g"]), 1023) * m),
      "b":  int(min(max(0, self.values["b"]), 1023) * m),

      'ww': int(min(max(0, self.values["w"]), 1023) * ((100 - temp) / 100) * m),
      'cw': int(min(max(0, self.values["w"]), 1023) * (temp / 100) * m)
    }
    
  def update(self, time_):
    # at least 1 pending event
    values = {'r': [], 'g': [], 'b': [], 'w': [], 't': [], 'm': []}
    to_remove = []
    # TODO add event up to 3
    if len(self.events) < 1:
      if len(self.queue) > 0:
        self.events.append(self.event_from_string(self.queue.pop(0)))
      
    for i in range(0, len(self.events)):
      # Taking care of oldest event
      event = self.events[i]
      status = event.get_status(time_)
      # Status 0, Scheduled but not started
      if status == 0:
        continue
      # Status 1, initiating event
      if status == 1:
        event.initiate()
      if status == 3:
        for k in self.values:
          values[k].append(event.rgbwt_target[k])
          while None in values[k]:
            values[k].remove(None)
        to_remove.append(i)
      else:
        for k in self.values:
          values[k].append(event.apply_ease(k, time_))
          while None in values[k]:
            values[k].remove(None)
            
    to_remove.reverse()
    for x in to_remove:
      self.events.pop(x)
      
    for k in values:
      if len(values[k]) > 0:
        self.values[k] = sum(values[k]) / len(values[k])


  def event_from_string(self, parameters):
    """
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
    
    params = {k:v for k, v in formatted_parameters} 
    e = Event(
      self,
      int(params["start_at"]),
      duration=int(params["duration"]),
      rgbwt_start={
        "r": int(params["r_start"]) if "r_start" in params else None,
        "g": int(params["g_start"]) if "g_start" in params else None,
        "b": int(params["b_start"]) if "b_start" in params else None,
        "w": int(params["w_start"]) if "w_start" in params else None,
        "t": int(params["temp_start"]) if "temp_start" in params else None,
        "m": int(params["master_start"]) if "master_start" in params else None,
      },
      rgbwt_target={
        "r": int(params["r_end"]) if "r_end" in params else None,
        "g": int(params["g_end"]) if "g_end" in params else None,
        "b": int(params["b_end"]) if "b_end" in params else None,
        "w": int(params["w_end"]) if "w_end" in params else None,
        "t": int(params["temp_end"]) if "temp_end" in params else None,
        "m": int(params["master_end"]) if "master_end" in params else None,
      }
    )

    
    return e 



