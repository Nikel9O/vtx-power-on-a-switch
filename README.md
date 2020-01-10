# vtx-power-on-a-switch

This project uses a circuit-python board ([Adafruit Trinket M0](https://www.adafruit.com/product/3500)) wired to a Flight controller running Betaflight in order to enable vtx power control on a switch.

## Compatibility: 
* tested on a TBS Smart Audio (v2.1) Vtx.
* tested on BetaFlight 4.1 .
* Should work on any servo-capable betaflight version.
* Should work on SA v 2.0 by only changing the power table (untested).
* IRC Tramp protocol partially implemented but untested.

## Why this project:
I was surprised by the lack of interest on such a simple but game-changing feature [#3094](https://github.com/betaflight/betaflight/issues/3094) from BF devs.
So i decided to extend my quadcopter capabilities on my own.
 
## How it works:
Betaflight servo output is read by the trinket M0 which changes VTX power accordingly.

## How to set it up:
### Board setup:
1. [Update/Install circuit python](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython) on your board.
1. Download [code.py](https://raw.githubusercontent.com/Nikel9O/vtx-power-on-a-switch/master/code.py) and edit the power table to your needs (default values are for Unify Pro 5G8 HV Race 2).
1. Drop your code.py file in the root of your CircuitPython board.
### Betaflight setup
1. Enable Servo Tilt in the configuration tab.
1. Remap a betaflight resource to SERVO 1 (i used the LED_STRIP 1 as it usually have a dedicated timer).
1. Setup a servo and its AUX channel in the servo tab (expert mode enabled) .
### Soldering
![connection diagram](/connection.png)
1. solder together RX and TX on the Trinket M0 and connect them to the VTX smart audio wire.
1. solder Trinket M0 battery pad to a 5v output on the FC, solder Trinket M0 ground to a ground on the FC.
1. Solder Trinket pin "~1" (also labeled as "Aout") to the LED pad on the Flight controller.

*Tip*: put connectors on Trinket M0 "~1" pin, the VTX smart audio wire and the flight controller smart audio pin to use BF vtx_control when not flying (ie. changing vtx channel)

## Credits:
* The idea of soldering together TX and RX pins came from [NightHawk32](https://github.com/NightHawk32/SmartAudio-testing)
* TBS smart audio protocol specs come from: [TBS](https://www.team-blacksheep.com/tbs_smartaudio_rev09.pdf)
* IRC Tramp protocol specs are from: [Betaflight source code](https://github.com/betaflight/betaflight/)
