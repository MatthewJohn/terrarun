import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class MetaWorkspaceService {

  constructor(private http: HttpClient,
              private accountService: AccountService) { }

  validateNewName(organisationName: string, name: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `https://${window.location.hostname}:5000/api/terrarun/v1/organisation/${organisationName}/meta-workspace-name-validate`,
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
        `https://${window.location.hostname}:5000/api/v2/organizations/${organisationName}/meta-workspaces`,
        { data: { type: 'meta-workspaces', attributes: {'name': name, 'description': description }}},
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
