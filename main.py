from lightmix import LightMix
from event import Event
from machine import Timer
import time
import requests
import sys
from file_io import read, write

# Declaring important objects
lightmix = LightMix()
lightmix_clock = Timer(0)

write("ssid", "YourSSIDHere")
write("pass", "YourPASSHere")

# Network items
server = requests.WebServer()
station = network.WLAN(network.STA_IF)
access_point = network.WLAN(network.AP_IF)

# Renaming endpoint, adding password
wifi_id = hash(station.config("mac"))

default_name = "LightMixMkI{}#{}".format("I" if sys.platform == "esp32" else "", wifi_id)
write("default_name", default_name)
name = read("ap_ssid")
if name in [None, ""]:
    name = default_name

ap_pass = read("ap_pass")
if ap_pass in [None, ""]:
    ap_pass = "admin"


# access_point.config(essid=name, password=ap_pass, authmode=network.AUTH_WPA_WPA2_PSK)

@server.route("/calibrate")
def calibrate(request):
    """
    A calibration can be performed by a master/client to
    ensure the synchronisation beetween multiple devices

    http params:
      current_time - positive integer

    :params: request
    :return: HTTP Response
    """

    print("Calibration request...")
    # Setting new time offset
    lightmix.set_time_offset(int(request.params_dict()["current_time"]))
    # Composing HTTP Response
    content = {
        "success": True,
        "message": 'Time offset set at {}'.format(lightmix.time_offset)
    }
    # Returning Response
    return requests.Response(code=200, content=content)


@server.route("/addevent")
def addevent(request):
    """
    Event adding HTTP endpoint

    http params:
      cs (optionnal) - starting color ; hex value from 8bits to 32bits
      ce (optionnal) - ending color ; hex value from 8bits to 32bits
      t (optionnal)  - timestamp to schedule event execution ; positive int
      d (optionnal)  - duration in millisecond of the event ; positive int
      k (optionnal)  - keylight coefficient ; add a white tint to global color

      Multiple collections of parameters can be added, with "&&" separator. They will
      be considered as seperate event, and will be added to the queue in order

    :request: Http Request Object
    :return: Http Response
    """
    print("Adding event")
    events = request.raw_params.split("&&")
    for element in events:
        try:
            lightmix.queue += element + '#'
        except MemoryError:
            pass

    return requests.Response(code=202, content={"success": True, "message": None})


@server.route("/wandering")
def wandering(request):
    """
    Wandering Endpoint

    http params:
      min_ms      : minimum slope duration ; positive int
      max_ms      : maximum slope duration ; positive int
      idle_min_ms : minimum idle duration ; positive int
      idle_max_ms : maximum idle duration ; positive int
      min_c       : minimum coefficient ; int beetween 0 and 100
      max_c       : maximum coefficient ; int beetween 0 and 100

    Wandering is an endpoint that randomise the power output over time.
    This can be used to set a master value (maximum power output)

    :request: Http Request
    :return: Http Response
    """
    try:
        # BUG : max/min time identical ?
        parameters = request.params_dict()

        # Validating parameters
        min_ms = int(parameters["min_ms"])
        max_ms = int(parameters["max_ms"])

        idle_min_ms = int(parameters["idle_min_ms"])
        idle_max_ms = int(parameters["idle_max_ms"])

        # Checking that time arent negatives
        if any(value < 0 for value in [min_ms, max_ms, idle_min_ms, idle_max_ms]):
            raise ValueError

        min_c = int(parameters["min_c"])
        max_c = int(parameters["max_c"])

        # Checking that coefficient is beetween 0 and 100
        if any(value < 0 or value > 100 for value in [min_c, max_c]):
            raise ValueError

            # Setting values to the lightmix Wanderer object
        lightmix.wanderer.min_ms = min_ms
        lightmix.wanderer.max_ms = max_ms

        lightmix.wanderer.idle_min_ms = idle_min_ms
        lightmix.wanderer.idle_max_ms = idle_max_ms

        lightmix.wanderer.min_c = min_c
        lightmix.wanderer.max_c = max_c

        # Returning Response
        return requests.Response(code=200, content={"success": True, "message": "Wanderer updated"})
    # Failure
    except:
        return requests.Response(code=200, content={"success": False, "message": "Wanderer not updated"})


@server.route("/delall")
def delall(request):
    """
    Removes every event

    :request: Http Request
    :return: Http Response
    """
    # Emptying queue and current event
    lightmix.event = None
    lightmix.queue = ""
    # Returning Response
    return requests.Response(code=200, content={"success": True, "message": "Cleaned."})


def wifi_connect():
    """
    Tries to connect to a wifi hotspot using conf files
    """
    SSID = read("ssid")
    PASS = read("pass")
    station.active(True)
    try:
        station.connect(SSID, PASS)
    except:
        print("[Wifi] SSID or PASS seems invalid.")
        return

    tries = 10
    while not station.isconnected():
        print("[Wifi] Connecting..[{} second(s) remaining..]".format(tries))
        time.sleep(1)
        tries -= 1
        if tries == 0:
            print("[Wifi] Aborting.")
            break


def init_wifi():
    """
    Init Wifi. If there's no way to connect to an endpoint, it will open an HotSpot
    To allow config from outside
    """
    wifi_connect()
    if station.isconnected():
        print("[Wifi] Connected.")
        print("[Wifi] Machine IP is : {}".format(station.ifconfig()[0]))
    else:
        print("[Wifi] Couldn't connected. Opening HotSpot")
        print("[Wifi] Machine IP is : {}".format(access_point.ifconfig()))
        access_point.active(True)


init_wifi()

if sys.platform == "esp8266":
    lightmix_clock.init(period=20, mode=Timer.PERIODIC, callback=lightmix.update)
server.run()

# Calculating tick rate
tick_rate = 50
tick_duration = int(1000 / tick_rate)

while True:
    t = time.ticks_ms()
    # Performing update, clearing queue if failure
    try:
        lightmix.update()
    except Exception as e:
        sys.print_exception(e)
        print("Clearing queue")
        lightmix.event = None
        lightmix.queue = ""
    # Calculating wait time according to tick rate
    time.sleep_ms(tick_duration - (time.ticks_ms() - t))
