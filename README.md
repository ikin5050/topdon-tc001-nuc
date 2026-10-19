Trigger a non-uniformity correction / flat-field correction on a Topdon TC001 thermal camera connected to a Raspberry Pi over USB.

The TC001 normally runs a NUC on its own schedule, dictated by a measured internal temperature change or every roughly 90 seconds. This script reproduces the USB control that trigger that calibration, so you can force one on demand. This was reverse engineered by analysing the USB packets from computer to camera when triggering a NUC through the TopView app (available from https://community.topdon.com/detail?id=580&type=1).

This script assumes a single TC001 is plugged in.

Requirements
------------
On Raspberry Pi OS, the simplest way to get pyusb (and libusb with it) is:

    sudo apt install python3-usb

Permissions
-----------
Run with sudo, or add a udev rule so normal users can access the camera.
Create /etc/udev/rules.d/99-topdon-tc001.rules containing:

    SUBSYSTEM=="usb", ATTR{idVendor}=="0bda", ATTR{idProduct}=="5830", MODE="0666"

then run `sudo udevadm control --reload-rules` and replug the camera.

Notes
-----
The camera's video interface is owned by the `uvcvideo` kernel driver.
The script temporarily detaches that driver to send the command, then
reattaches it. While it is detached, any application currently streaming
from the camera may lose its feed.


Usage
-----
    python3 usb_trigger.py
-----