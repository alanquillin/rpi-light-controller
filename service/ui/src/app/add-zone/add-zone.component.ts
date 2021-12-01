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

  addZoneFormGroup: FormGroup = new FormGroup({
    description: new FormControl('', [Validators.required]),
    on: new FormControl('', [Validators.required]),
    off: new FormControl('', [Validators.required]),
    pinNum: new FormControl('', [Validators.required]),
    program: new FormControl('', [Validators.required]),
  });

  zone: Zone = new Zone;
  constructor(private dataService: DataService, private router: Router) {}

  ngOnInit() {
      this.zone.state = "off";
  }

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

