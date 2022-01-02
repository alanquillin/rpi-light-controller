// since these will often be python API driven snake_case names
/* eslint-disable @typescript-eslint/naming-convention */

import { Injectable } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../environments/environment';
import {
  Device,
  DeviceZones,
  ZoneDevices,
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
    //   this.baseUrl = '/api/v1';
    // }

    this.host = '';
    this.baseUrl = '/api/v1';
  }

  getError(error: any) {
    let message = '';
    if (error.error instanceof ErrorEvent) {
        // handle client-side errors
        message = `Error: ${error.error.message}`;
    } else {
        // handle server-side errors
        message = `Error Code: ${error.status}\nMessage: ${error.message}`;
    }
    console.log(message);
    return throwError(message);
  }

  getZones(): Observable<Zone[]> {
    const url = `${this.baseUrl}/zones`;
    return this.http.get<Zone[]>(url).pipe(catchError(this.getError));
  }

  getZone(zoneId: number): Observable<Zone> {
    const url = `${this.baseUrl}/zones/${zoneId}`;
    return this.http.get<Zone>(url).pipe(catchError(this.getError));
  }

  getZoneDevices(zoneId: number): Observable<ZoneDevices[]> {
    const url = `${this.baseUrl}/zones/${zoneId}/devices`;
    return this.http.get<ZoneDevices[]>(url).pipe(catchError(this.getError));
  }

  deleteZone(zoneId: number): Observable<any> {
    const url = `${this.baseUrl}/zones/${zoneId}`;
    return this.http.delete<any>(url).pipe(catchError(this.getError));
  }

  turnZoneOn(zoneId: number): Observable<Zone> {
    const url = `${this.baseUrl}/zones/${zoneId}/on`;
    return this.http.post<Zone>(url, {}).pipe(catchError(this.getError));
  }

  turnZoneOff(zoneId: number): Observable<Zone> {
    const url = `${this.baseUrl}/zones/${zoneId}/off`;
    return this.http.post<Zone>(url, {}).pipe(catchError(this.getError));
  }

  updateZone(zoneId: number, data: any): Observable<Zone> {
    const url = `${this.baseUrl}/zones/${zoneId}`;
    return this.http.patch<Zone>(url, data).pipe(catchError(this.getError));
  }

  addZone(zone: Zone): Observable<Zone> {
    const url = `${this.baseUrl}/zones`;
    return this.http.post<Zone>(url, zone).pipe(catchError(this.getError));
  }

  getDevices(includeStatus: boolean = false): Observable<Device[]> {
    const url = `${this.baseUrl}/devices`;
    return this.http.get<Device[]>(url).pipe(catchError(this.getError));
  }

  getDevice(deviceId: number): Observable<Device> {
    const url = `${this.baseUrl}/devices/${deviceId}`;
    return this.http.get<Device>(url).pipe(catchError(this.getError));
  }

  getDevicesZones(deviceId: number): Observable<DeviceZones[]> {
    const url = `${this.baseUrl}/devices/${deviceId}/zones`;
    return this.http.get<DeviceZones[]>(url).pipe(catchError(this.getError));
  }

  deleteDeviceZoneMapping(deviceId: number, zoneId: number, pinNum: number): Observable<any> {
    const url = `${this.baseUrl}/devices/${deviceId}/zones/${zoneId}/pins/${pinNum}`;
    return this.http.delete<any>(url).pipe(catchError(this.getError));
  }

  addDeviceZoneMapping(zoneId: number, deviceId: number, pinNum: number): Observable<any> {
    const url = `${this.baseUrl}/zones/${zoneId}/devices`;
    return this.http.post<any>(url, {deviceId: deviceId, pinNum: pinNum}).pipe(catchError(this.getError));
  }
}
