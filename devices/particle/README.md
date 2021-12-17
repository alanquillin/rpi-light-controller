# RPi Light Controller: Remote relays device (Particle.io)

This application is designed to be run on any of the [Particle](https://particle.io) IoT devices (running their DeviceOS).  These devices are capable of controlling one or more 5V relays via their control pins (the number of control pins varies by the platform).  When Mapped to a zone, these devices poll the service API on a interval to check the expected state of the zone and set their control pin(s) accordingly.  The difference with these IoT devices compared to others, is the Particle cloud functionality.  The devices are capable of being trigger remotely by the RPi service when changes happen so they don't have to poll the API as frequently.

## Requirements

- A [Particle device](https://store.particle.io).  Currently only testes with the [WiFi devices](https://store.particle.io/collections/wifi) but there is no reason that tis cannot work with the other device as long as they can connect to the RPi Service.
- A 5V relay.

## Compiling and flashing a device

To flash a device, connect the device via usb and run the following command replacing `<platform>` with the name of the device platform (i.e. photon, argon, boron, etc):

```shell
make flash <platform>
```

This will compile and flash the connected device for the default DeviceOS firmware.  If you want to target a specific firmware (for instance, if you are using an older device like the "spark core"), you can passing the in the `FIRMWARE_VERSION` flag.

```shell
make flash -e FIRMWARE_VERSION=<Firmware version number> <platform>
```
