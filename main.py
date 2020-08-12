



from lightmix_cls import LightMix
from event import Event
import time
import requests

server = requests.WebServer()

lightmix = LightMix(rPin, gPin, bPin, wwPin, cwPin)
lightmix_clock = Timer(0)
  
@server.route("/calibrate")
def calibrate(request):
  params = request.params_dict()
  code=202
  content={
    "success": True,
    "message": None
  }
  # Case multiple parameters
  if len(params) < 1:
    code=400
    content['success'] = False
    content['message'] = 'Missing required parameter : "current_time"'
  elif len(params) > 1:
    code=400
    content['success'] = False
    content['message'] = 'Too many parameters. Only "current_time" allowed'
  # Case no required parameters 
  elif "current_time" not in params:
    code=400
    content['success'] = False
    content['message'] = 'Invalid parameter. Only "current_time" allowed'
  # Case invalid parameter value
  elif not params["current_time"].isdigit():
    code=400
    content['success'] = False
    content['message'] = 'Invalid parameter type for "current_time", expecting Integer'
  # Case valid request
  if code == 202:
    current_time = int(params["current_time"])
    lightmix.set_time_offset(current_time)
    content['success'] = True
    content['message'] = 'Machine time is {}. Time offset set at {}'.format(current_time - lightmix.time_offset, lightmix.time_offset)
  # Response
  return requests.Response(code=code, content=content)

@server.route("/addevent")
def addevent(request):
  """
  Event(self.channels[i], time.ticks_ms() + 2000, duration=1000, rgbwt_target={"r": 512}))
  """
  required_parameters= [
    "channel", 
    "duration"
  ]
  permitted_parameters = [
    # Required
    "channel", 
    "start_at", 
    "duration", 
    # Start anchor
    "r_start",
    "g_start",
    "b_start",
    "w_start",
    "temp_start",
    "master_start",
    # Target anchor
    "r_end",
    "g_end",
    "b_end",
    "w_end",
    "temp_end",
    "master_end"
  ]
  
  params = request.params_dict()
  code=202
  content={
    "success": True,
    "message": None
  }
  
  
  # Case forbidden parameters
  if not all(param in permitted_parameters for param in params):
    
    forbidden_parameters = []
    for param in params:
      if param not in permitted_parameters:
        forbidden_parameters.append(param)
    code = 400
    content["success"] = False
    content["message"] = "Parameter{} not allowed : {}".format("s" if len(forbidden_parameters) > 1 else "", ", ".join(forbidden_parameters))
  
  # Case missing required parameters
  elif not all(param in params for param in required_parameters):  
    missing_parameters = []
    for param in required_parameters:
      if param not in params:
        missing_parameters.append(param)
    code = 400
    content["success"] = False
    content["message"] = "Missing Parameter{} : {}".format("s" if len(missing_parameters) > 1 else "", ", ".join(missing_parameters))
  
  # Case invalid value
  elif not all(params[k].isdigit() for k in params):
    invalid_parameters = []
    for k in params:
      if not params[k].isdigit():
        invalid_parameters.append(k)
    code = 400
    content["success"] = False
    content["message"] = "Invalid type for parameter{} : {}. Expecting integer".format("s" if len(invalid_parameters) > 1 else "", ", ".join(invalid_parameters)) 
    
  else:
    # Converting all params to Int
    for param in params:
      params[param] = int(params[param])
      
    # Building Event
    e = request.raw_params
    if "start_at" not in params:
      e += "&start_at={}".format(2000 + lightmix.time_offset + time.ticks_ms())
    
    lightmix.channels[params["channel"]].queue.append(e)
  return requests.Response(code=code, content=content)

@server.route("/delall")
def delall(request):
  lenght = 0
  
  for channel in lightmix.channels:
    lenght += len(channel.events)
    channel.events = []
    lenght += len(channel.queue)
    channel.queue = []
  return requests.Response(code=200, content={"success": True, "message": "{} events destroyed".format(lenght)})


 
lightmix_clock.init(period=20, mode=Timer.PERIODIC, callback=lightmix.update)


# Init Wifi connection
SSID = "YOUR SSID HERE"
PASS = "YOUR WIFI PASSWORD HERE"

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(SSID, PASS)

tries = 0
while station.isconnected() == False:
  tries += 1
  if tries > 50000:
    break


print(station.ifconfig())

if tries > 50000:
  lightmix_clock.deinit()
  while True:
    rPin.duty(24)
    time.sleep(1)
    rPin.duty(0)
    time.sleep(1)

  
server.run(debug=False)






