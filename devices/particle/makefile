FIRWARE_VERSION ?= 2.2.0
PLATFORM_TARGETS = compile flash
PLATFORM ?= $(filter-out $(PLATFORM_TARGETS),$(MAKECMDGOALS))
PLATFORMS = photon p core c electron e p1 argon boron bsom

SAVE_DIR ?= ./builds/$(FIRWARE_VERSION)/$(PLATFORM)
SAVE_PATH ?= $(SAVE_DIR)/rpi-lts-ctl.bin

.PHONY: depends compile flash clean $(PLATFORMS)

depends:
	particle library copy HttpClient && \
	particle library copy ArduinoJson

compile: depends
ifeq ("$(PLATFORM)","")
	$(error Please provide a device platform to compile for)
endif
ifeq ($(filter $(PLATFORM),$(PLATFORMS)),)
	$(error Invalid platform '$(PLATFORM)'.  Must be one of: $(PLATFORMS))
endif
ifeq ("$(wildcard $(SAVE_DIR))","")
	$(shell mkdir -p $(SAVE_DIR))
endif
	particle compile $(PLATFORM) --target $(FIRWARE_VERSION) --saveTo $(SAVE_PATH) $(EXTRA_ARGS) $(EXTRA_COMPILE_ARGS) .

flash: compile
	particle flash --target $(FIRWARE_VERSION) $(EXTRA_ARGS) $(EXTRA_FLASH_ARGS) $(DEVICE_ID) $(SAVE_PATH)

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