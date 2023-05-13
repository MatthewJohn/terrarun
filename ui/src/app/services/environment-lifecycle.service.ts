import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AccountService } from '../account.service';
import { DataList } from '../interfaces/data';
import { EnvironmentLifecycleAttributes } from '../interfaces/environment-lifecycle-attributes';
import { ResponseObject } from '../interfaces/response';

@Injectable({
  providedIn: 'root'
})
export class EnvironmentLifecycleService {

  constructor(
    private http: HttpClient,
    private accountService: AccountService
  ) { }

  getEnvironmentLifecycles(organisationName: string): Promise<ResponseObject<EnvironmentLifecycleAttributes>[]> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
      `/api/v2/organizations/${organisationName}/environment-lifecycles`,
      { headers: this.accountService.getAuthHeader() }).subscribe({
        next: (data: DataList<ResponseObject<EnvironmentLifecycleAttributes>>) => {
          resolve(data.data);
        },
        error: (err) => {
          reject(err);
        }
      });
    });
  }

  updateAttributes(environmentLifecycleId: string, attributes: {[key: string]: string}): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.patch<any>(
        `/api/v2/environment-lifecycles/${environmentLifecycleId}`,
        { data: { type: 'environment-lifecycles', 'attributes': attributes } },
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: any) => {
          resolve(data);
        },
        error: (err) => {
          reject(err);
        }
      });
    })
  }

  validateNewName(organisationName: string, name: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `/api/terrarun/v1/organisation/${organisationName}/environment-lifecycle-name-validate`,
        { 'name': name },
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data) => {
          resolve(data);
        },
        error: (err) => {
          reject(err);
        }
      });
    });
  }

  create(organisationName: string, attributes: EnvironmentLifecycleAttributes): Promise<ResponseObject<EnvironmentLifecycleAttributes>> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `/api/v2/organizations/${organisationName}/environment-lifecycles`,
        { data: { type: 'environment-lifecycles', "attributes": attributes}},
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: ResponseObject<EnvironmentLifecycleAttributes>) => {
          resolve(data);
        },
        error: (err) => {
          reject(err);
        }
      });
    });
  }
}
