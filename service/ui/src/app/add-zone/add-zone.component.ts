import { Component } from '@angular/core';
import { DataService } from './../data.service';
import { Router } from '@angular/router';
import { FormGroup, Validators, FormControl } from '@angular/forms';

import { Zone } from './../models/models';

@Component({
  selector: 'add-zone',
  templateUrl: './add-zone.component.html',
  styleUrls: ['./add-zone.component.scss']
})
export class AddZoneComponent {
  title = 'Add Zone';
  programs = ["timer", "manual", "off"]
  processing = false

  timeValidators =[Validators.required, Validators.pattern("^([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$"), Validators.minLength(8), Validators.maxLength(8)]

  addZoneFormGroup: FormGroup = new FormGroup({
    description: new FormControl('', [Validators.required]),
    on: new FormControl('', this.timeValidators),
    off: new FormControl('', this.timeValidators),
    pinNum: new FormControl('', [Validators.required]),
    program: new FormControl('', [Validators.required]),
  });

  zone: Zone = new Zone;
  constructor(private dataService: DataService, private router: Router) {}

  ngOnInit() {}

  submit(): void {
    if (this.zone) {
        this.dataService.addZone(this.zone).subscribe(() => {
            this.router.navigate(["/"], {});
        });
    }
  }

  get addZoneForm() {
    return this.addZoneFormGroup.controls;
  }
}

