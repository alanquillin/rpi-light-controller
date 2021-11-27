// since these will often be python API driven snake_case names
/* eslint-disable @typescript-eslint/naming-convention */

import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';
import {
  Zone,
} from './models/models';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class DataService {
  baseUrl: string;
  host: string;

  constructor(public http: HttpClient) {
    // if (!environment.production) {
    //   const schema = environment.apiSchema;
    //   const host = environment.apiHost;
    //   const port = environment.apiPort;
    //   this.host = `${schema}://${host}:${port}`;
    //   this.baseUrl = `${this.host}`;
    // } else {
    //   this.host = '';
    //   this.baseUrl = '';
    // }

    this.host = '';
    this.baseUrl = '';
  }

  getZones(): Observable<Zone[]> {
    const url = `${this.baseUrl}/zones`;
    return this.http.get<Zone[]>(url, {});
  }

  getZone(zoneId: number): Observable<Zone[]> {
    const url = `${this.baseUrl}/zones/${zoneId}`;
    return this.http.get<Zone[]>(url, {});
  }

  turnZoneOn(zoneId: number): Observable<any> {
    const url = `${this.baseUrl}/zones/${zoneId}/on`;
    const result = this.http.post<any>(url, {});
    result.subscribe();
    return result;
  }

  turnZoneOff(zoneId: number): Observable<any> {
    const url = `${this.baseUrl}/zones/${zoneId}/off`;
    const result = this.http.post<any>(url, {});
    result.subscribe();
    return result;
  }

  updateZone(zoneId: number, data: any): Observable<any> {
    const url = `${this.baseUrl}/zones/${zoneId}`;
    const result = this.http.patch<any>(url, data);
    result.subscribe();
    return result;
  }
}
