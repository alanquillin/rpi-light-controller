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

  constructor(private dataService: DataService, private router: Router) {}

  devices: Device[] = [];

  ngOnInit() {
    this.dataService.getDevices().subscribe((devices: Device[]) => {
      this.devices = devices;
    });
  }
}

