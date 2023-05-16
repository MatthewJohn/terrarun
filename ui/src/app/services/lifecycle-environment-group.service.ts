import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AccountService } from '../account.service';
import { DataItem, DataList } from '../interfaces/data';
import { LifecycleEnvironmentAttributes, LifecycleEnvironmentRelationships } from '../interfaces/lifecycle-environment-attributes';
import { LifecycleEnvironmentGroupAttributes, LifecycleEnvironmentGroupRelationships } from '../interfaces/lifecycle-environment-group-attributes';
import { ResponseObjectWithRelationships } from '../interfaces/response';

@Injectable({
  providedIn: 'root'
})
export class LifecycleEnvironmentGroupService {

  constructor(
    private http: HttpClient,
    private accountService: AccountService
  ) { }

  getLifecycleEnvironments(lifecycleEnvironmentGroupId: string): Promise<ResponseObjectWithRelationships<LifecycleEnvironmentAttributes, LifecycleEnvironmentRelationships>[]> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `/api/v2/lifecycle-environment-groups/${lifecycleEnvironmentGroupId}/lifecycle-environments`,
        {
          headers: this.accountService.getAuthHeader()
        }).subscribe({
          next: (data: DataList<ResponseObjectWithRelationships<LifecycleEnvironmentAttributes, LifecycleEnvironmentRelationships>>) => {
            resolve(data.data);
          },
          error: (err) => {
            reject(err);
          }
        });
    });
  }

  update(lifecycleEnvironmentGroupId: string, attributes: LifecycleEnvironmentGroupAttributes): Promise<ResponseObjectWithRelationships<LifecycleEnvironmentGroupAttributes, LifecycleEnvironmentGroupRelationships>> {
    return new Promise((resolve, reject) => {
      this.http.patch<any>(
        `/api/v2/lifecycle-environment-groups/${lifecycleEnvironmentGroupId}`,
        { data: { type: "lifecycle-environment-groups", id: lifecycleEnvironmentGroupId, "attributes": attributes } },
        {
          headers: this.accountService.getAuthHeader()
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

  delete(lifecycleEnvironmentGroupId: string): Promise<null> {
    return new Promise((resolve, reject) => {
      this.http.delete<any>(
        `/api/v2/lifecycle-environment-groups/${lifecycleEnvironmentGroupId}`,
        {
          headers: this.accountService.getAuthHeader()
        }).subscribe({
          next: () => {
            resolve(null);
          },
          error: (err) => {
            reject(err);
          }
        });
    });
  }

  createLifecycleEnvironment(lifecycleEnvironmentGroupId: string, environmentId: string): Promise<ResponseObjectWithRelationships<LifecycleEnvironmentAttributes, LifecycleEnvironmentRelationships>> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `/api/v2/lifecycle-environment-groups/${lifecycleEnvironmentGroupId}/lifecycle-environments`,
        { data: { "type": "lifecycle-environments", relationships: { "environment": { data: { "type": "environments", "id": environmentId } } } } },
        {
          headers: this.accountService.getAuthHeader()
        }).subscribe({
          next: (data: DataItem<ResponseObjectWithRelationships<LifecycleEnvironmentAttributes, LifecycleEnvironmentRelationships>>) => {
            resolve(data.data);
          },
          error: (err) => {
            reject(err);
          }
        });
    });
  }
}
