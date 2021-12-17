FIRMWARE_VERSION ?= 2.2.0
PLATFORM_TARGETS = compile flash
PLATFORM ?= $(filter-out $(PLATFORM_TARGETS),$(MAKECMDGOALS))
PLATFORMS = photon p core c electron e p1 argon boron bsom

SAVE_DIR ?= ./builds/$(FIRMWARE_VERSION)/$(PLATFORM)
SAVE_PATH ?= $(SAVE_DIR)/rpi-lts-ctl.bin

.PHONY: depends config compile flash clean $(PLATFORMS)

depends:
	particle library copy HttpClient && \
	particle library copy ArduinoJson

config:
ifneq ($(shell grep "<__IP_Address__>" "src/rpi-lts-ctl.ino"),)
	@echo "IP Address not set.  What is the IP Address of you RPi Light Service? "; \
    read IP_ADDRESS; if [ ! -z $$IP_ADDRESS ]; then sed -i "" "s/<__IP_Address__>/$$IP_ADDRESS/g" src/rpi-lts-ctl.ino; fi
	
endif

compile: depends config
ifeq ("$(PLATFORM)","")
	$(error Please provide a device platform to compile for)
endif
ifeq ($(filter $(PLATFORM),$(PLATFORMS)),)
	$(error Invalid platform '$(PLATFORM)'.  Must be one of: $(PLATFORMS))
endif
ifeq ("$(wildcard $(SAVE_DIR))","")
	$(shell mkdir -p $(SAVE_DIR))
endif
	particle compile $(PLATFORM) --target $(FIRMWARE_VERSION) --saveTo $(SAVE_PATH) $(EXTRA_ARGS) $(EXTRA_COMPILE_ARGS) .

flash: compile
	particle flash --target $(FIRMWARE_VERSION) $(EXTRA_ARGS) $(EXTRA_FLASH_ARGS) $(DEVICE_ID) $(SAVE_PATH)

test: 
	echo "test" && echo "$%" && echo "$(ARGS)" && echo "$(MAKECMDGOALS)"
clean:
	rm -rf ./builds && \
	rm -rf ./target && \
	rm -rf ./lib && \
	rm src/rpi-lts-ctl.cpp

$(PLATFORMS):
    #EMPTY target to catch if the platform was supplies as a command line arg (i.e. `make compile argon`)
	@echo > /dev/null