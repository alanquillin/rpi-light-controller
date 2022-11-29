// since these will often be python API driven snake_case names
/* eslint-disable @typescript-eslint/naming-convention */
// this check reports that some of these types shadow their own definitions
/* eslint-disable no-shadow */

import { isNilOrEmpty } from '../utils/helpers'

export class Base {
  constructor(from?: any) {
    if(!isNilOrEmpty(from)) {
      this.from(from);
    }
  }

  from(from: any) {
    Object.assign(this, from);
  }
}
export class Zone extends Base {
  id!: number;
  description!: string;
  program!: string;
  state: string | undefined;
  expectedState: string | undefined;
  pinNum!: number;
  on: string | undefined;
  off: string | undefined;
}

export class Device extends Base {
  id!: number;
  description: string | undefined;
  manufacturerId!: string;
  manufacturer!: string;
  model!: string;
  supportsStatusCheck!: boolean;
  status!: string;
}

export class ZoneDevices extends Base {
  deviceId!: number;
  pinNums!: number[];
}

export class DeviceZones extends Base {
  zoneId!: number;
  pinNums!: number[];
}

export class DeviceToZoneMap extends Base {
  zoneId!: number;
  deviceId!: number;
  pinNum!: number;
}