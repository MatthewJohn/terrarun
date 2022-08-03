import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
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

}


// 