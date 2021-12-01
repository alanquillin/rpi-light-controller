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

  constructor(private dataService: DataService) {}

  zones: Zone[] = [];
  selectedZone: Zone | undefined;
  loading = true;
  programs = ["timer", "manual", "off"]
  editingZoneInfo = false;
  editingZoneSchedule = false;
  editTimer = false;

  getZones() {
    return this.dataService.getZones();
  }

  getZone(id: number) {
    return this.dataService.getZone(id);
  }

  refreshZones(next?: any) {
    this.getZones().subscribe((zones: any) => {
      if (zones) {
        this.zones = zones;
        if(zones.length === 1){
          this.selectedZone = zones[0];
        }
      }
      if (next) {
        next();
      }
    });
  }

  refreshSelectedZone(id: number, next?: any) {
    console.log("refreshing selected zone data")
    this.getZone(id).subscribe((zone: any) => {
      if (zone) {
        console.log("yay zone found")
        this.selectedZone = zone;
      }
      if (next) {
        console.log("calling next function")
        next();
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
          this.selectedZone = zone;
        }
      });
    }
  }

  toggle(event: { checked: any; }) {
    console.log('toggle', event.checked);
    if (this.selectedZone && this.selectedZone.id)  {
      if (event.checked) {
        this.dataService.turnZoneOn(this.selectedZone.id).subscribe((zone: any) => {
          if (zone) {
            this.selectedZone = zone;
          }
        });
      } else {
        this.dataService.turnZoneOff(this.selectedZone.id).subscribe((zone: any) => {
          if (zone) {
            this.selectedZone = zone;
          }
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
          this.selectedZone = undefined;
          this.refreshZones();
        });
      }
    }
  }

  editZoneInfo() {
    this.editingZoneInfo = true;
  }

  saveZoneInfo() {
    console.log("stop editing info");
    if (this.selectedZone && this.selectedZone.id && this.selectedZone.description && this.selectedZone.pinNum)  {
      this.dataService.updateZone(this.selectedZone.id, {description: this.selectedZone.description, pinNum: this.selectedZone.pinNum}).subscribe((zone: any) => {
        if (zone) {
          this.selectedZone = zone;
        }
        this.editingZoneInfo = false;
      });
    }
  }

  cancelZoneInfo() {
    if (this.selectedZone && this.selectedZone.id) {
      this.refreshSelectedZone(this.selectedZone.id, () => {
        this.editingZoneInfo = false;
      });
    } else {
      this.editingZoneInfo = false;
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
          this.selectedZone = zone;
        }
        this.editingZoneSchedule = false;
      });
    }
  }

  cancelZoneSchedule() {
    if (this.selectedZone && this.selectedZone.id) {
      this.refreshSelectedZone(this.selectedZone.id, () => {
        this.editingZoneSchedule = false;
      });
    } else {
      this.editingZoneSchedule = false;
    }
  }
}

