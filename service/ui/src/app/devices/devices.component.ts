import { MatSnackBar } from '@angular/material/snack-bar';

import { Component } from '@angular/core';
import { DataService } from '../_services/data.service';
import { Router } from '@angular/router';
import { FormControl, AbstractControl, Validators, FormGroup } from '@angular/forms';

import { Device } from './../models/models';
import { isNilOrEmpty } from '../utils/helpers'

import * as _ from 'lodash';

@Component({
  selector: 'devices',
  templateUrl: './devices.component.html',
  styleUrls: ['./devices.component.scss']
})
export class DevicesComponent {
  title = 'Manage Devices';

  displayedColumns: string[] = ['id', 'description', 'manufacturer', 'model', 'manufacturerId', 'supportsStatusCheck', 'actions'];
  isLoading = false;
  processing = false;
  selectedDevice : Device | undefined;
  modifyDevice : Device = new Device();
  editing = false;
  adding = false; 

  modifyFormGroup: FormGroup = new FormGroup({
    description: new FormControl('', [Validators.required]),
    model: new FormControl('', [Validators.required]),
    manufacturer: new FormControl('', [Validators.required]),
    manufacturerId: new FormControl('', [Validators.required])
  });

  get modifyForm(): { [key: string]: AbstractControl } {
    return this.modifyFormGroup.controls;
  }

  constructor(private dataService: DataService, private router: Router, private _snackBar: MatSnackBar) {}

  devices: Device[] = [];

  refresh(always?:Function, next?: Function, error?: Function) {
    
    this.dataService.getDevices().subscribe({
      next: (devices: Device[]) => {
        this.devices = devices;
      },
      error: (err: any) => {
        this.displayError(err.message);
        if(error){
          error();
        }
        if(always){
          always();
        }
      },
      complete: () => {
        if(next){
          next();
        }
        if(always){
          always();
        }
      }
    });
  }

  ngOnInit() {
    this.isLoading = true;
    this.refresh(() => {this.isLoading = false;});    
  }

  displayError(errMsg: string) {
    this._snackBar.open("Error: " + errMsg, "Close");
  }

  
  add() : void {
    this.modifyFormGroup.reset();
    this.adding = true;
    this.selectedDevice = undefined;
    this.modifyDevice = new Device();
  }
  
  cancelAdd(): void {
    this.adding = false;
  }

  create(): void {
    if(!this.modifyDevice) {
      return;
    }

    let data = {
      description: this.modifyDevice.description,
      manufacturer: this.modifyDevice.manufacturer,
      manufacturerId: this.modifyDevice.manufacturerId,
      model: this.modifyDevice.model
    }

    this.processing = true;
    this.dataService.createDevice(data).subscribe({
      next: (_res: any) => {
        this.refresh(()=> {this.processing = false;}, () => {
          this.adding = false;
        })
      },
      error: (err: any) => {
        this.displayError(err.message);
        this.processing = false;
      }
    })  
  }

  edit(device: Device) : void {
    this.editing = true;
    this.selectedDevice = new Device(device);
    this.modifyDevice = new Device(device);
    this.modifyFormGroup.reset();
  }

  cancelEdit(): void {
    this.editing = false;
  }

  save(): void {
    let data = this.changes();

    if(isNilOrEmpty(data) || !this.modifyDevice){ 
      return;
    }

    this.processing = true;
    this.dataService.updateDevice(this.modifyDevice.id, data).subscribe({
      next: (_res: any) => {
        this.refresh(()=> {this.processing = false;}, () => {
          this.editing = false;
        })
      },
      error: (err: any) => {
        this.displayError(err.message);
        this.processing = false;
      }
    })  
  }

  get hasChanges() : boolean {
    return !isNilOrEmpty(this.changes());
  }

  changes() : any {
    let changes : any = {}
    if(!this.selectedDevice || !this.modifyDevice) {
      return changes;
    }

    let fields : string[] = ["description", "manufacturer", "manufacturerId", "model"]

    for(let f of fields) {
      let expected = _.get(this.selectedDevice, f);
      let actual = _.get(this.modifyDevice, f);

      if(expected !== actual) {
        changes[f] = actual;
      }
    }

    return changes;
  }

  delete(device: Device) {
    if(confirm("Are you sure you want to delete device #" + device.id + " (" + device.description+ ")")) {
      this.dataService.deleteDevice(device.id).subscribe(() => {
        this.refresh();
      }, (err: any) => {
        this.displayError("There was an error trying to delete the device");
      });
    }
  }
}

