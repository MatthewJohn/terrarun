import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class WorkspaceService {

  constructor(private http: HttpClient,
              private accountService: AccountService) { }

  validateNewWorkspaceName(organisationName: string, name: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `https://${window.location.hostname}:5000/api/terrarun/v1/organisation/${organisationName}/workspace-name-validate`,
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
        `https://${window.location.hostname}:5000/api/v2/organizations/${organisationName}/workspaces`,
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
      `https://${window.location.hostname}:5000/api/v2/organizations/${organisationName}/workspaces/${workspaceName}`,
      { headers: this.accountService.getAuthHeader() }
    );
  }

  getDetailsById(workspaceId: string): Observable<any> {
    return this.http.get<any>(
      `https://${window.location.hostname}:5000/api/v2/workspaces/${workspaceId}`,
      { headers: this.accountService.getAuthHeader() }
    );
  }


  getRuns(workspaceId: string): Observable<any> {
    return this.http.get<any>(
        `https://${window.location.hostname}:5000/api/v2/workspaces/${workspaceId}/runs`,
        { headers: this.accountService.getAuthHeader() }
      );
  }
}
