import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class OrganisationService {

  constructor(private http: HttpClient, private accountService: AccountService) { }

  validateNewOrganisationName(name: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `/api/terrarun/v1/organisation/create/name-validation`,
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

  create(name: string, email: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `/api/v2/organizations`,
        { data: { type: 'organizations', attributes: {'name': name, 'email': email }}},
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

  update(organisationName: string, name: string, email: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.patch<any>(
        `/api/v2/organizations/${organisationName}`,
        { data: { type: 'organizations', attributes: {'name': name, 'email': email }}},
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

  getAll(): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `/api/v2/organizations`,
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

  getOrganisationDetails(organisationName: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `/api/v2/organizations/${organisationName}`,
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

  getOrganisationOauthClients(organisationName: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `/api/v2/organizations/${organisationName}/oauth-clients`,
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

  getAllWorkspaces(organisationName: string): Observable<any> {
    return this.http.get<any>(`/api/v2/organizations/${organisationName}/workspaces`,
                              { headers: this.accountService.getAuthHeader() }).pipe(map((response) => response.data));

  }

  getAllProjects(organisationName: string): Observable<any> {
    return this.http.get<any>(`/api/v2/organizations/${organisationName}/projects`,
                              { headers: this.accountService.getAuthHeader() }).pipe(map((response) => response.data));

  }
}
