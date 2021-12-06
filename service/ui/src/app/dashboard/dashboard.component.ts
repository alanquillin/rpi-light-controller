import { MatSnackBar } from '@angular/material/snack-bar';

import { Component } from '@angular/core';
import { DataService } from './../data.service';
import { Zone } from './../models/models';

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
  selectedZoneOriginal: Zone | undefined;  // used for resetting incase the binding succeeds up a service update fails (i.e. the web server is down)
  loading = true;
  programs = ["timer", "manual", "off"]
  editingZoneInfo = false;
  editingZonePin = false;
  editingZoneSchedule = false;
  editTimer = false;

  displayError(errMsg: string) {
    this._snackBar.open("Error: " + errMsg, "Close");
  }

  getZones() {
    return this.dataService.getZones();
  }

  getZone(id: number) {
    return this.dataService.getZone(id);
  }

  setSelectZone(zone: Zone | undefined) {
    this.selectedZone = zone;
    this.selectedZoneOriginal = zone;
  }

  resetSelectZone() {
    this.selectedZone = this.selectedZoneOriginal;
  }

  refreshZones(next?: () => void, onError?: () => void) {
    this.getZones().subscribe((zones: any) => {
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

  refreshSelectedZone(id: number, next?: () => void, onError?: () => void) {
    console.log("refreshing selected zone data")
    this.getZone(id).subscribe((zone: any) => {
      if (zone) {
        console.log("yay zone found")
        this.setSelectZone(zone);
      }
      if (next) {
        console.log("calling next function")
        next();
      }
    }, (err: any) => {
      this.displayError("There was an error trying to retrieve data for Zone " + id);
      if (onError) {
        onError();
      }
    });
  }

  ngOnInit() {
    this.loading = true;
    this.refreshZones(() => {
      this.loading = false;
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

  selectZone(zone: Zone | undefined) {
    this.selectedZone = zone;
  }

  deleteZone() {
    if (this.selectedZone && this.selectedZone.id) {
      if(confirm("Are you sure you want to delete Zone " + this.selectedZone.id + " (" + this.selectedZone.description + ")")) {
        this.dataService.deleteZone(this.selectedZone.id).subscribe(() => {
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
      this.refreshSelectedZone(this.selectedZone.id, () => {
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
      this.refreshSelectedZone(this.selectedZone.id, () => {
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
      this.refreshSelectedZone(this.selectedZone.id, () => {
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
}

