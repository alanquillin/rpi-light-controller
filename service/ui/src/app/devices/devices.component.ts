import { Component } from '@angular/core';
import { DataService } from './../data.service';
import { Router } from '@angular/router';

import { Device } from './../models/models';

@Component({
  selector: 'devices',
  templateUrl: './devices.component.html',
  styleUrls: ['./devices.component.scss']
})
export class DevicesComponent {
  title = 'Manage Devices';

  displayedColumns: string[] = ['description', 'manufacturer', 'model', 'manufacturerId', 'actions'];
  isLoading = false;

  constructor(private dataService: DataService, private router: Router) {}

  devices: Device[] = [];

  refresh() {
    this.isLoading = true;
    this.dataService.getDevices().subscribe((devices: Device[]) => {
      this.devices = devices;
      this.isLoading = false;
    });
  }

  ngOnInit() {
    this.refresh();    
  }

  deleteDevice(id: number) {
    return;
  }
}

