#!/usr/bin/env python3

import sys
import time

import usb.core
import usb.util

# The TC001 enumerates with Realtek's vendor ID (the USB bridge chip it uses).
VENDOR_ID = 0x0BDA
PRODUCT_ID = 0x5830
INTERFACE = 0

BM_REQUEST_TYPE = 0x41
B_REQUEST = 0x45
W_VALUE = 0x0078
W_INDEX = 0x1D00

TIMEOUT_MS = 1000

# Pause between the two packets, matching the captured traffic.
ARM_TO_SHUTTER_DELAY_S = 0.05

# Sent first: prepares the camera for the shutter command.
ARM_PAYLOAD = bytes([0x0C, 0x41, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00])

# Sent second: closes the shutter and runs the NUC.
SHUTTER_PAYLOAD = bytes([0x0D, 0xC1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])


def send(cam, payload):
    """Send one vendor control transfer. Returns the number of bytes written."""
    return cam.ctrl_transfer(
        BM_REQUEST_TYPE, B_REQUEST, W_VALUE, W_INDEX, payload, timeout=TIMEOUT_MS
    )


def main():
    cam = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if cam is None:
        print("TC001 camera not found. Is it plugged in?", file=sys.stderr)
        return 1

    detached = False
    try:
        # Take the interface away from uvcvideo so we can talk to it directly.
        if cam.is_kernel_driver_active(INTERFACE):
            cam.detach_kernel_driver(INTERFACE)
            detached = True

        usb.util.claim_interface(cam, INTERFACE)

        # Send the two-packet sequence that triggers the NUC.
        sent_arm = send(cam, ARM_PAYLOAD)
        time.sleep(ARM_TO_SHUTTER_DELAY_S)
        sent_shutter = send(cam, SHUTTER_PAYLOAD)

        print(f"Triggered NUC (sent {sent_arm} + {sent_shutter} bytes)")
        return 0

    except usb.core.USBError as e:
        hint = " (try sudo or the udev rule in the script header)" if e.errno == 13 else ""
        print(f"Failed to trigger NUC: {e}{hint}", file=sys.stderr)
        return 1

    finally:
        # Always hand the camera back to the kernel so video keeps working.
        usb.util.release_interface(cam, INTERFACE)
        if detached:
            try:
                cam.attach_kernel_driver(INTERFACE)
            except usb.core.USBError as e:
                print(
                    f"Warning: could not reattach kernel driver: {e}. "
                    "Replug the camera to restore video.",
                    file=sys.stderr,
                )
        usb.util.dispose_resources(cam)


if __name__ == "__main__":
    sys.exit(main())