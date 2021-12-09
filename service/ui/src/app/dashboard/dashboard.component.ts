import { MatSnackBar } from '@angular/material/snack-bar';

import { Component } from '@angular/core';
import { DataService } from './../data.service';
import { Device, Zone, ZoneDevices, DeviceToZoneMap } from './../models/models';
import { FormGroup, Validators, FormControl } from '@angular/forms';

@Component({
  selector: 'dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})


export class DashboardComponent {
  title = 'rpi-lts-ctrl';

  constructor(private dataService: DataService, private _snackBar: MatSnackBar) {}
  
  zones: Zone[] = [];
  selectedZone: Zone | undefined;  //used for binding and UX conditionals
  selectedZoneId: number | undefined;
  selectedZoneOriginal: Zone | undefined;  // used for resetting incase the binding succeeds up a service update fails (i.e. the web server is down)
  loading = true;
  programs = ["timer", "manual", "off"]
  editingZoneInfo = false;
  editingZonePin = false;
  editingZoneSchedule = false;
  editTimer = false;
  devices: Device[] = [];

  selectedZoneDevices: ZoneDevices[] = [];

  newDeviceMapping: DeviceToZoneMap = new DeviceToZoneMap;
  addDeviceMappingFormGroup: FormGroup = new FormGroup({
    deviceId: new FormControl('', [Validators.required]),
    pinNum: new FormControl('', [Validators.required]),
  });

  get addDeviceMappingForm() {
    return this.addDeviceMappingFormGroup.controls;
  }

  displayError(errMsg: string) {
    this._snackBar.open("Error: " + errMsg, "Close");
  }

  selectZone(zoneId: number | undefined) {
    this.selectedZoneId = zoneId;
    if (!zoneId) {
      return;
    }
    this.refreshSelectedZone();
  }

  setSelectZone(zone?: Zone) {
    this.selectedZone = zone;
    this.selectedZoneOriginal = zone;
  }

  resetSelectZone() {
    this.selectedZone = this.selectedZoneOriginal;
  }

  getDeviceDescription(deviceId: number){
    let device = this.devices.find(d => d.id === deviceId);

    if (!device) {
      return "UNKNOWN"
    }

    return `${device.description} (${device.manufacturer}: ${device.model})`;
  }

  refreshZones(next?: () => void, onError?: () => void) {
    this.dataService.getZones().subscribe((zones: any) => {
      if (zones) {
        this.zones = zones;
        if(zones.length === 1){
          this.setSelectZone(zones[0]);
        }
      }
      if (next) {
        next();
      }
    }, (err: any) => {
      this.displayError("There was an error trying to retrieve the list of zones");
      if (onError) {
        onError();
      }
    });
  }

  refreshDevices(next?: () => void, onError?: () => void) {
    this.dataService.getDevices().subscribe((devices: any) => {
      if (devices) {
        this.devices = devices;
      }
      if (next) {
        next();
      }
    }, (err: any) => {
      this.displayError("There was an error trying to retrieve the list of devices");
      if (onError) {
        onError();
      }
    });
  }

  refreshSelectedZone(next?: () => void, onError?: () => void) {
    console.log("refreshing selected zone data");
    if (!this.selectedZoneId) {
      return;
    }

    this.dataService.getZone(this.selectedZoneId).subscribe((zone: any) => {
      if (zone) {
        console.log("yay zone found")
        this.setSelectZone(zone);
        this.refreshSelectZoneDevices(next, onError);
      } else if (next) {
        next();
      }
    }, (err: any) => {
      this.displayError("There was an error trying to retrieve data for Zone " + this.selectedZoneId);
      if (onError) {
        onError();
      }
    });
  }

  refreshSelectZoneDevices(next?: () => void, onError?: () => void) {
    if (!this.selectedZoneId) {
      return;
    }
    this.dataService.getZoneDevices(this.selectedZoneId).subscribe((dzs: ZoneDevices[]) => {
      this.selectedZoneDevices = dzs
      if (next) {
        next();
      }
    }, (err: any) => {
      this.selectedZoneDevices = [];
      this.displayError("There was an error trying to retrieve devices for Zone " + this.selectedZoneId);
      if (onError) {
        onError();
      }
    })
  } 

  ngOnInit() {
    this.loading = true;
    this.refreshZones(() => {
      this.refreshDevices(() => {
        this.loading = false;
        this.addDeviceMappingFormGroup.reset();
      });
    });
  }

  programChange(item: { value: string; }) {
    console.log("Selected value: " + item.value);
    if (this.selectedZone && this.selectedZone.id)  {
      this.dataService.updateZone(this.selectedZone.id, {program: item.value}).subscribe((zone: any) => {
        if (zone) {
          this.setSelectZone(zone);
        }
      }, (err: any) => {
        this.displayError("There was an error trying to change the zone program");
        this.resetSelectZone();
      });
    }
  }

  toggle(event: { checked: any; }) {
    console.log('toggle', event.checked);
    if (this.selectedZone && this.selectedZone.id)  {
      if (event.checked) {
        this.dataService.turnZoneOn(this.selectedZone.id).subscribe((zone: any) => {
          if (zone) {
            this.setSelectZone(zone);
          }
        }, (err: any) => {
          this.displayError("There was an error trying to switch the zone on");
          this.resetSelectZone();
        });
      } else {
        this.dataService.turnZoneOff(this.selectedZone.id).subscribe((zone: any) => {
          if (zone) {
            this.setSelectZone(zone);
          }
        }, (err: any) => {
          this.displayError("There was an error trying to switch the zone off");
          this.resetSelectZone();
        });
      }
    }
  }

  deleteZone() {
    if (this.selectedZone && this.selectedZone.id) {
      if(confirm("Are you sure you want to delete Zone " + this.selectedZone.id + " (" + this.selectedZone.description + ")")) {
        this.dataService.deleteZone(this.selectedZone.id).subscribe(() => {
          this.selectedZoneId = undefined;
          this.setSelectZone(undefined);
          this.refreshZones();
        }, (err: any) => {
          this.displayError("There was an error trying to delete the zone");
        });
      }
    }
  }

  editZoneInfo() {
    this.editingZoneInfo = true;
  }

  saveZoneInfo() {
    console.log("stop editing info");
    if (this.selectedZone && this.selectedZone.id && this.selectedZone.description)  {
      this.dataService.updateZone(this.selectedZone.id, {description: this.selectedZone.description}).subscribe((zone: any) => {
        if (zone) {
          this.selectedZone = zone;
        }
        this.editingZoneInfo = false;
      }, (err: any) => {
        this.displayError("There was an error trying to update the zone details");
        this.resetSelectZone();
        this.editingZoneInfo = false;
      });
    } else {
      this.editingZoneInfo = false;
    }
  }

  cancelZoneInfo() {
    if (this.selectedZone && this.selectedZone.id) {
      this.refreshSelectedZone(() => {
        this.resetSelectZone();
        this.editingZoneInfo = false;
      }, () => {
        this.resetSelectZone();
        this.editingZoneInfo = false;
      });
    } else {
      this.editingZoneInfo = false;
    }
  }

  editZonePin() {
    this.editingZonePin = true;
  }

  saveZonePin() {
    console.log("stop editing info");
    if (this.selectedZone && this.selectedZone.id && this.selectedZone.pinNum)  {
      this.dataService.updateZone(this.selectedZone.id, {pinNum: this.selectedZone.pinNum}).subscribe((zone: any) => {
        if (zone) {
          this.selectedZone = zone;
        }
        this.editingZonePin = false;
      }, (err: any) => {
        this.displayError("There was an error trying to update the zone details");
        this.resetSelectZone();
        this.editingZonePin = false;
      });
    } else {
      this.editingZonePin = false;
    }
  }

  cancelZonePin() {
    if (this.selectedZone && this.selectedZone.id) {
      this.refreshSelectedZone(() => {
        this.resetSelectZone();
        this.editingZonePin = false;
      }, () => {
        this.resetSelectZone();
        this.editingZonePin = false;
      });
    } else {
      this.editingZonePin = false;
    }
  }


  editZoneSchedule() {
    this.editingZoneSchedule = true;
  }

  saveZoneSchedule() {
    console.log("stop editing schedule");
    if (this.selectedZone && this.selectedZone.id && this.selectedZone.on && this.selectedZone.off)  {
      this.dataService.updateZone(this.selectedZone.id, {on: this.selectedZone.on, off: this.selectedZone.off}).subscribe((zone: any) => {
        if (zone) {
          this.setSelectZone(zone);
        }
        this.editingZoneSchedule = false;
      }, (err: any) => {
        this.displayError("There was an error trying to update the zone schedule");
        this.resetSelectZone();
        this.editingZoneSchedule = false;
      });
    }
  }

  cancelZoneSchedule() {
    if (this.selectedZone && this.selectedZone.id) {
      this.refreshSelectedZone(() => {
        this.resetSelectZone();
        this.editingZoneSchedule = false;
      }, () => {
        this.resetSelectZone();
        this.editingZoneSchedule = false;
      });
    } else {
      this.editingZoneSchedule = false;
    }
  }

  removeDeviceMapping(deviceId: number, pinNum: number) {
    if(!this.selectedZoneId) {
      return;
    }

    if(confirm(`Are you sure you want to remove "${this.getDeviceDescription(deviceId)}" device for pin ${pinNum}`)) {
      this.dataService.deleteDeviceZoneMapping(deviceId, this.selectedZoneId, pinNum).subscribe(() => {
        this.refreshSelectZoneDevices();
      }, (err: any) => {
        this.displayError("There was an error trying to remove the device from zone");
      });
    }
  }

  addDeviceMap(): void {
    if (!this.newDeviceMapping || !this.newDeviceMapping.deviceId || !this.newDeviceMapping.pinNum) {
      console.log("new device map object is empty... skipping")
      return;
    }

    if (!this.addDeviceMappingFormGroup.valid) {
      console.log("add device form is not valid")
      return;
    }

    if (!this.selectedZoneId) {
      console.log("no selected zone id");
      return;
    }

    this.dataService.addDeviceZoneMapping(this.selectedZoneId, this.newDeviceMapping.deviceId, this.newDeviceMapping.pinNum).subscribe(() => {
        this.addDeviceMappingFormGroup.reset();
        this.refreshSelectZoneDevices();
    }, (err: any) => {
      this.displayError("There was an error trying to add device to zone");
    });
  }
}

