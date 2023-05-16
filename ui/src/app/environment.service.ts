import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { AccountService } from './account.service';
import { DataList } from './interfaces/data';
import { EnvironmentAttributes } from './interfaces/environment';
import { ResponseObject } from './interfaces/response';

@Injectable({
  providedIn: 'root'
})
export class EnvironmentService {

  constructor(private http: HttpClient,
    private accountService: AccountService) { }

  getOrganisationEnvironments(organisationName: string): Promise<ResponseObject<EnvironmentAttributes>[]> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `/api/v2/organizations/${organisationName}/environments`,
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: DataList<ResponseObject<EnvironmentAttributes>>) => {
          resolve(data.data);
        },
        error: () => {
          reject();
        }
      });
    })
  }

  updateAttributes(environmentId: string, attributes: {[key: string]: string}): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.patch<any>(
        `/api/v2/environments/${environmentId}`,
        { data: { type: 'environments', 'attributes': attributes } },
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: any) => {
          resolve(data);
        },
        error: () => {
          reject();
        }
      });
    })
  }

  validateNewName(organisationName: string, name: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `/api/terrarun/v1/organisation/${organisationName}/environment-name-validate`,
        { 'name': name },
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data) => {
          resolve(data);
        },
        error: () => {
          reject();
        }
      });
    });
  }

  create(organisationName: string, name: string, description: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `/api/v2/organizations/${organisationName}/environments`,
        { data: { type: 'environments', attributes: {'name': name, 'description': description }}},
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data) => {
          resolve(data);
        },
        error: () => {
          reject();
        }
      });
    });
  }
}
