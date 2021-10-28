# LightMix 
LightMix is an open-source ESP32 D1 Mini Firmware and Hardware created for over-ip light control. Initially created as open source Elgato KeyLight, it evolved so it can buffer animations provided the correct backend. 

It is also running at high frequency PWM (78.125kHz), making it flicker-free

## Demo
7 of those panels are in production on [Warths's Twitch channel](https://www.twitch.tv/warths). They can be seen on any VOD, but the 7 can be seen used at the same time on [this clip](https://clips.twitch.tv/WittyBrainyKittenVoteNay-GMUXylfDUYEBWy2h).

In this demo, we can see almost every functionnality of the panels : 
- Panel Array synchronisation
- In-sync buffered animation
- Non-buffered animation
- In-sync (variable) attenuation
- Easying from a color to another color


## Build your LightMix
### Firmware
Building the firware of a LightMix is pretty simple.

- Flash your ***ESP32 D1 Mini*** with [MicroPython 1.13](/misc/micropython/)
- upload the [firmware](/firmware/) to your board. 
- Fill the credentials.py file
-  done.

### Hardware
**Building the board :**
Gerber files are provided [here](/misc/pcb%20gerber/). You can order a blank board on any PCB-making service or manufacture it yourself. 

1. You'll need a few components : 
	- x1 [ESP32 D1 Mini](https://amzn.to/3GvT8Uq)
	- x1 [Buck converter](https://amzn.to/3vVKObC)
	- x4 [IRLB8721PBF](https://fr.farnell.com/infineon/irlb8721pbf/mosfet-n-ch-30v-62a-to220/dp/1740783)
	- x2 [5 pin 2.54mm JST connector](https://amzn.to/3BqkS9t)
	- x1 [2 pin 2.54mm JST connector](https://amzn.to/3BqkS9t)

2. Place the components according to the gerber file
3. Be extra careful on the direction of your transistor and pin header. Figure it out using a multimeter. 
	- U1+ should face toward the inside of the board
	- U4+ U5+ positive should face towards the outside of the board
	
4. You now need a way to provide 12v DC to U1. 
5. Without the ESP32 plugged in, configure the buck converter to 3.3v using a multimeter.
6. It should work. You need to plug a panel or a strip to either U4 or U5.


**Building the panel/strip:**
Only vague instruction will be given here. You can either put a 5-pin JST connector to your 12V RGBW, RGB or UV led strip, or build a led matrix.

To build panels, I recommend :
- Using [large A4 blank PCB boards](https://amzn.to/3mouqgY) 
- Engrave 5 tracks in a ZigZag pattern
- Stick Led Strip sections so it connects correctly to the tracks

## How to use
### Initial config
Just provide a Wifi SSID and PASS in the `credentials.py` to make your board ready to go. 

The board will log its own IP through serial. This IP should never change, so configure your DHCP to make the IP static.


> Note: LightMix will create files for you credentials and use the file values if they exists. If you made a mistake or to start fresh, delete the "flash" folder. This is for a future implementation, even though it doesn't make sense right now.

### Endpoints
Lightmix is controled by GET Http requests. There is a few endpoints :
#### /calibrate
This endpoint takes a parameter "current_time", with a millisecond timestamp as value. You can use this endpoint to tell LightMix your backend time, to sync it to this backend.

Example: 
`http://{ip}/calibrate?current_time=1635456056950`

>Note: There is no reason that the LightMix clock and your Backend clock runs at the same speed. They should be pretty close, but will likely drift over a few hours . So use this frequently.

#### /addevent
This endpoint is the main endpoint, allowing you to change the color of your panel. Its content is feeded through a loop, updated 50 times a second, to make smooth animations. On boot, its default color is black.

All parameters are optionnal, but there is 5 different:
- cs "color start". 
	- describe the color when starting an event. Is replaced by current color if not provided
- ce "color end". 
	- describe the color when ending an event. Is replaced by current color if not provided
- t "time". 
	- describe when the event should start according to machine time (including `/calibrate` endpoint offset) in milliseconds. Becomes the current time if not provided.
- d "duration". 
	- describe the duration of the event, in milliseconds
- k "keylight". 
	- This allows to add white the mix. 1 will add as much white as there is other colors. (ex: 255 on all RGB channels will add 255 on W channel). Default is 0
> Note : Colors can be provided in 8 bit (grayscale), 24bits or 32bits HEX format (without "#"). 
> Note² :  "current color" for missing parameters is not the current color at the time of the addevent request, but the current color at the time of execution of the event. 

Example: 
`http://{ip}/addevent?ce=ff&d=1000`
This will make you panel white, from its current color, in 1 second

`http://{ip}/addevent?cs=ff0000&ce=ff&d=1000`
This will immediately change the panel to red, then go to white, in 1 second

`http://{ip}/addevent?ce=ff0000&d=1000&k=1`
This will change the panel color to red, with a keylight weight of 1, making it RGBW ff000056

If you use the "t" parameter, you can chain events using "&&" separator :
`http://{ip}/addevent?t=5000ce=ff&d=1000&&t=10000ce=00&d=1000`
This will rise to white on t=5000, in 1 second, then go to black at t=10000, in 0 second.

#### /delall
This endpoint remove all currently queued events. If you buffer a lot of events to make animations, this is useful for emergency animation stop.

Usage: 
`http://{ip}/delall`

#### /wandering

This endpoint helps to configure random or fixed attenuations. This can be useful to dim your LightMix without changing the hex colors in your requests. This also allows to make strobe / organic animations.

- min_ms : Minimal animation duration in MS. 
	- The wandering is slowly drifting from an attenuation to another one. This is the minimum amount of time for this animation
- max_ms : Maximum animation duration in MS. 
	- The wandering is slowly drifting from an attenuation to another one. This is the maximum amount of time for this animation
-  idle_min_ms : Minimum waiting time beetwen animations.
	-  Idle time is waiting time beetween animations. This allows to lock the attenuation for a random amount of time
 -  idle_max_ms : Maximum waiting time beetwen animations.
	-  Idle time is waiting time beetween animations. This allows to lock the attenuation for a random amount of time
- min_c : Minimum coefficient.
	- Minimum coefficient represent the dimmer attenuation percentage. 
- max_c : Maximum coefficient.
	- Maximum coefficient represent the brightest attenuation percentage

> Note: if min_c and max_c are equals, this locks the Lightmix at this attenuation, without using other parameters.
