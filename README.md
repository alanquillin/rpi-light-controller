# RPi Light Controller

A simple app for controlling zones of lights using a RaspberryPi.  Originally designed to run my Christmas lights on a schedule, I decided to make it a little more generic.  Using a single RaspberryPi and a set of power relays, you can run up to 29 different zones of lights *(assuming ALL 29 GPIO pins can be used, I have not tested them all)*.  Each zone can be controlled individually by either a timer, or manually.  


## Running on a Raspberry Pi

### Prerequisites

- [RaspberryPi 2+](https://www.raspberrypi.org/) *(this may work on earlier versions, but I have not tested it)*
- One or more power relay(s).  This can be anything you want, but needs to be able to be triggered by the RPis GPIO pin output. Examples: [this](https://www.sparkfun.com/products/13815) or [this](https://www.amazon.com/dp/B07CZL2SKN/ref=sspa_dk_detail_1)

For instructions on connecting your RaspberryPi and relays, there are several instructions online ([here](https://www.electronicshub.org/control-a-relay-using-raspberry-pi/) for example.  *Full disclosure, I have NO idea who authored this, just found it as an example and thought it was easy enough for anyone to follow.*)

### Install Docker and docker-compose

``` bash
$ curl -sSL https://raw.githubusercontent.com/alanquillin/rpi-light-controller/main/deploy/rpi/bootstrap.sh | bash
```

### Copy the docker-compose.yml

``` bash
$ mkdir rpi-light-controller

$ cd rpi-light-controller

$ curl -sSL https://raw.githubusercontent.com/alanquillin/rpi-light-controller/main/deploy/rpi/docker-compose.yml > docker-compose.yml

$ curl -sSL https://raw.githubusercontent.com/alanquillin/rpi-light-controller/main/deploy/rpi/docker-rpi.env > docker-rpi.env
```

Update the `docker-rpi.env` file to change any of the DB values if you want.  Or if you are running an external PostgreSQL data, you will need to replace the DB creds

### Run the application

``` bash
$ docker-compose up -d
```

to view the logs, run the following:

``` bash
$ docker-compose logs -f
```

This runs the UI as a web service on port 80.  If you plan to access it on the RPi only, then you can access it using the web browser and going to `http://localhost`.  This does not require the RPi to be connected to a network unless you want to access it from an another system such as your PC or phone.  In that case, you will need to make sure your RPi is connected to the same network, allowing you to access it from your device's web browser at `http://<IP address of RPi>`

To get the IP address of the RPi, from the RPIs command line, use the following, replacing `<DEVICE>` with `eth0` if it is connected via an ethernet cable, or `wlan0` if connect to WIFI:
``` bash
$ ip addr show <DEVICE> | grep -Po 'inet \K[\d.]+
```