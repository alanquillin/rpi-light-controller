import { Component, OnInit } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { Router  , ActivatedRoute, RouterOutlet } from '@angular/router';
import {map} from 'rxjs/operators';

import { ConfigService } from './_services/config.service';
import { toBoolean } from './utils/helpers';

import * as _ from 'lodash';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  titleDefault: string = "RPI Light Controller";
  title: string = this.titleDefault;
  hideHeader: boolean = false;
  hideFooter: boolean = false;
  routeData: any;

  constructor(private configService: ConfigService, private titleService: Title) {}

  setConfig(data: any): void {
    this.title = _.get(data, "title", 'RPI Light Controller');
    this.hideHeader = toBoolean(_.get(data, "hideHeader", false));
    this.hideFooter = toBoolean(_.get(data, "hideFooter", false));

    this.titleService.setTitle(this.title);
  }

  onActivate(outlet: RouterOutlet): void {
    outlet.activatedRoute.data.pipe(map(data => {
      this.routeData = data;
      this.setConfig(data);
    })).toPromise().then();
  }

  ngOnInit(): void {
    this.configService.updated.subscribe((data: any) => {
      this.setConfig(_.merge(this.routeData, data));
    })
  }
}

