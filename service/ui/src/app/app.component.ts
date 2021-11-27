import { Component } from '@angular/core';
import { DataService } from './data.service';
import {
  Zone,
} from './models/models';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'rpi-lts-ctrl';

  constructor(private dataService: DataService) {}

  zones: Zone[] = [];
  selectedZone: Zone | undefined;
  loading = true;
  programs = ["timer", "manual", "off"]

  getZones() {
    return this.dataService.getZones();
  }

  getZone(id: number) {
    return this.dataService.getZone(id);
  }

  ngOnInit() {
    this.loading = true;
    this.getZones().subscribe((zones: any) => {
      if (zones) {
        this.zones = zones;
        if(zones.length === 1){
          this.selectedZone = zones[0];
        }
      }
      this.loading = false;
    });
  }

  programChange(item: { value: string; }) {
    console.log("Selected value: " + item.value);
    if (this.selectedZone && this.selectedZone.id)  {
      this.dataService.updateZone(this.selectedZone.id, {program: item.value})
    }
  }

  public toggle(event: { checked: any; }) {
    console.log('toggle', event.checked);
    if (this.selectedZone && this.selectedZone.id)  {
      if (event.checked) {
        this.dataService.turnZoneOn(this.selectedZone.id)
      } else {  
        this.dataService.turnZoneOff(this.selectedZone.id)
      }
    }
  }
}
