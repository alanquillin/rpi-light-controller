FIRWARE_VERSION ?= 2.2.0
PLATFORM ?= photon

SAVE_DIR ?= ./builds/$(FIRWARE_VERSION)/$(PLATFORM)
SAVE_PATH ?= $(SAVE_DIR)/rpi-lts-ctl.bin

.PHONY: depends compile flash clean

depends:
	particle library copy HttpClient && \
	particle library copy ArduinoJson

compile: depends
ifeq ("$(wildcard $(SAVE_DIR))","")
	$(shell mkdir -p $(SAVE_DIR))
endif
	particle compile $(PLATFORM) --target $(FIRWARE_VERSION) --saveTo $(SAVE_PATH) $(EXTRA_ARGS) $(EXTRA_COMPILE_ARGS) .

flash: compile
	particle flash --target $(FIRWARE_VERSION) $(EXTRA_ARGS) $(EXTRA_FLASH_ARGS) $(DEVICE_ID) $(SAVE_PATH)

clean:
	rm -rf ./builds && \
	rm -rf ./target && \
	rm -rf ./lib && \
	rm src/rpi-lts-ctl.cpp