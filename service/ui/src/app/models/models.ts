// since these will often be python API driven snake_case names
/* eslint-disable @typescript-eslint/naming-convention */
// this check reports that some of these types shadow their own definitions
/* eslint-disable no-shadow */

export class Zone {
  id!: number;
  description!: string;
  program!: string;
  state: string | undefined;
  expectedState: string | undefined;
  pinNum!: number;
  on: string | undefined;
  off: string | undefined;
}

export class Device {
  id!: number;
  description: string | undefined;
  manufacturerId!: string;
  manufacturer!: string;
  model!: string;
}

export class ZoneDevices {
  deviceId!: number;
  pinNums!: number[];
}

export class DeviceZones {
  zoneId!: number;
  pinNums!: number[];
}

export class DeviceToZoneMap {
  zoneId!: number;
  deviceId!: number;
  pinNum!: number;
}