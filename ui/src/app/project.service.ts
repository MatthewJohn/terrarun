import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class ProjectService {

  constructor(private http: HttpClient,
              private accountService: AccountService) { }

  validateNewName(organisationName: string, name: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `/api/terrarun/v1/organisation/${organisationName}/project-name-validate`,
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

  create(organisationName: string, name: string, description: string, lifecycle: number): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `/api/v2/organizations/${organisationName}/projects`,
        { data: { type: 'projects', attributes: {'name': name, 'description': description, 'lifecycle': lifecycle}}},
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

  getDetailsByName(organisationName: string, name: string): Observable<any> {
    return this.http.get<any>(
      `/api/v2/organizations/${organisationName}/projects/${name}`,
      { headers: this.accountService.getAuthHeader() }
    );
  }

  getDetailsByOrganisationNameAndWorkspaceName(organisationName: string, workspaceName: string): Observable<any> {
    return this.http.get<any>(
      `/api/v2/organizations/${organisationName}/workspaces/${workspaceName}/relationships/projects`,
      { headers: this.accountService.getAuthHeader() }
    );
  }

  update(projectId: string, attributes: any): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.patch<any>(
        `/api/v2/projects/${projectId}`,
        { data: { type: 'projects', 'attributes': attributes } },
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: any) => {
          resolve(data.data);
        },
        error: () => {
          reject();
        }
      });
    });
  }
}
