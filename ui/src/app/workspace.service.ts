import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AccountService } from './account.service';
import { ConfigurationVersionAttributes, ConfigurationVersionRelationships } from './interfaces/configuration-version';
import { DataItem, DataList, DataListWithIncluded } from './interfaces/data';
import { IngressAttributeAttribues } from './interfaces/ingress-attribute';
import { ResponseObject, ResponseObjectWithRelationships, TypedResponseObject, TypedResponseObjectWithRelationships } from './interfaces/response';
import { RunAttributes, RunRelationships } from './interfaces/run';
import { WorkspaceAttributes, WorkspaceRelationships } from './interfaces/workspace';

@Injectable({
  providedIn: 'root'
})
export class WorkspaceService {

  constructor(private http: HttpClient,
              private accountService: AccountService) { }

  validateNewWorkspaceName(organisationName: string, name: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `/api/terrarun/v1/organisation/${organisationName}/workspace-name-validate`,
        { 'name': name },
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data) => {
          resolve(data.data);
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
        `/api/v2/organizations/${organisationName}/workspaces`,
        { data: { type: 'workspaces', attributes: {'name': name, 'description': description }}},
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

  getDetailsByName(organisationName: string, workspaceName: string): Observable<any> {
    return this.http.get<any>(
      `/api/v2/organizations/${organisationName}/workspaces/${workspaceName}`,
      { headers: this.accountService.getAuthHeader() }
    );
  }

  getDetailsById(workspaceId: string): Observable<DataItem<ResponseObjectWithRelationships<WorkspaceAttributes, WorkspaceRelationships>>> {
    return this.http.get<DataItem<ResponseObjectWithRelationships<WorkspaceAttributes, WorkspaceRelationships>>>(
      `/api/v2/workspaces/${workspaceId}`,
      { headers: this.accountService.getAuthHeader() }
    );
  }

  getConfigurationVersionByCommit(workspaceId: string, commitSha: string): Observable<DataList<ResponseObjectWithRelationships<ConfigurationVersionAttributes, ConfigurationVersionRelationships>>> {
    return this.http.get<DataList<ResponseObjectWithRelationships<ConfigurationVersionAttributes, ConfigurationVersionRelationships>>>(
      `/api/v2/workspaces/${workspaceId}/configuration-versions?filter[commit]=${commitSha}&page[size]=1`,
      { headers: this.accountService.getAuthHeader() }
    );
  }


  getRuns(workspaceId: string): Observable<DataListWithIncluded<ResponseObjectWithRelationships<RunAttributes, RunRelationships>, TypedResponseObject<"ingress-attributes", IngressAttributeAttribues>|TypedResponseObjectWithRelationships<"configuration-versions", ConfigurationVersionAttributes, ConfigurationVersionRelationships>>> {
    return this.http.get<DataListWithIncluded<ResponseObjectWithRelationships<RunAttributes, RunRelationships>, TypedResponseObject<"ingress-attributes", IngressAttributeAttribues>|TypedResponseObjectWithRelationships<"configuration-versions", ConfigurationVersionAttributes, ConfigurationVersionRelationships>>>(
      `/api/v2/workspaces/${workspaceId}/runs?include=configuration_version,configuration_version.ingress_attributes`,
      { headers: this.accountService.getAuthHeader() }
    );
  }

  update(workspaceId: string, attributes: any): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.patch<any>(
        `/api/v2/workspaces/${workspaceId}`,
        { data: { type: 'workspaces', 'attributes': attributes } },
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: any) => {
          resolve(data);
        },
        error: () => {
          reject();
        }
      });
    });
  }
}
