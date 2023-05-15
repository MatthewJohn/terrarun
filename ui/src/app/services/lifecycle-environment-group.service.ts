import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AccountService } from '../account.service';
import { DataList } from '../interfaces/data';
import { LifecycleEnvironmentAttributes, LifecycleEnvironmentRelationships } from '../interfaces/lifecycle-environment-attributes';
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
        { headers: this.accountService.getAuthHeader()
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
}
