import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AccountService } from '../account.service';
import { DataItem, DataList } from '../interfaces/data';
import { LifecycleAttributes } from '../interfaces/lifecycle-attributes';
import { LifecycleEnvironmentGroupAttributes, LifecycleEnvironmentGroupRelationships } from '../interfaces/lifecycle-environment-group-attributes';
import { ResponseObject, ResponseObjectWithRelationships } from '../interfaces/response';

@Injectable({
  providedIn: 'root'
})
export class LifecycleService {

  constructor(
    private http: HttpClient,
    private accountService: AccountService
  ) { }

  getLifecycles(organisationName: string): Promise<ResponseObject<LifecycleAttributes>[]> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `/api/v2/organizations/${organisationName}/lifecycles`,
        { headers: this.accountService.getAuthHeader()
      }).subscribe({
        next: (data: DataList<ResponseObject<LifecycleAttributes>>) => {
          resolve(data.data);
        },
        error: (err) => {
          reject(err);
        }
      });
    });
  }

  getByName(organisationName: string, lifecycleName: string): Promise<ResponseObject<LifecycleAttributes>> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `/api/v2/organizations/${organisationName}/lifecycles/${lifecycleName}`,
        { headers: this.accountService.getAuthHeader()
      }).subscribe({
        next: (data: DataItem<ResponseObject<LifecycleAttributes>>) => {
          resolve(data.data);
        },
        error: (err) => {
          reject(err);
        }
      });
    });
  }

  updateAttributes(lifecycleId: string, attributes: LifecycleAttributes): Promise<ResponseObject<LifecycleAttributes>> {
    return new Promise((resolve, reject) => {
      this.http.patch<any>(
        `/api/v2/lifecycles/${lifecycleId}`,
        { data: { id: lifecycleId, type: 'lifecycles', 'attributes': attributes } },
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: DataItem<ResponseObject<LifecycleAttributes>>) => {
          resolve(data.data);
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
        `/api/terrarun/v1/organisation/${organisationName}/lifecycle-name-validate`,
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

  create(organisationName: string, attributes: LifecycleAttributes): Promise<ResponseObject<LifecycleAttributes>> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `/api/v2/organizations/${organisationName}/lifecycles`,
        { data: { type: 'lifecycles', "attributes": attributes}},
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: ResponseObject<LifecycleAttributes>) => {
          resolve(data);
        },
        error: (err) => {
          reject(err);
        }
      });
    });
  }

  getLifecycleEnvironmentGroups(lifecycleId: string): Promise<ResponseObjectWithRelationships<LifecycleEnvironmentGroupAttributes, LifecycleEnvironmentGroupRelationships>[]> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `/api/v2/lifecycles/${lifecycleId}/lifecycle-environment-groups`,
        { headers: this.accountService.getAuthHeader()
      }).subscribe({
        next: (data: DataList<ResponseObjectWithRelationships<LifecycleEnvironmentGroupAttributes, LifecycleEnvironmentGroupRelationships>>) => {
          resolve(data.data);
        },
        error: (err) => {
          reject(err);
        }
      });
    });
  }

  createLifecycleEnvironmentGroup(lifecycleId: string): Promise<ResponseObjectWithRelationships<LifecycleEnvironmentGroupAttributes, LifecycleEnvironmentGroupRelationships>> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `/api/v2/lifecycles/${lifecycleId}/lifecycle-environment-groups`,
        { headers: this.accountService.getAuthHeader()
      }).subscribe({
        next: (data: DataItem<ResponseObjectWithRelationships<LifecycleEnvironmentGroupAttributes, LifecycleEnvironmentGroupRelationships>>) => {
          resolve(data.data);
        },
        error: (err) => {
          reject(err);
        }
      });
    });
  }
}
