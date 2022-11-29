import { MatSnackBar } from '@angular/material/snack-bar';

import { Component, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {

  constructor(private router: Router, private _snackBar: MatSnackBar) {}
  @Input() title: string = "";

  ngOnInit() {
  }

  goto(path: string): void {
    window.location.href = `/${path}`;
  }
}
