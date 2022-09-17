import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class TaskService {

  constructor(private http: HttpClient,
    private accountService: AccountService) { }

  getTasksByOrganisation(organisationName: string): Observable<any> {
    return this.http.get<any>(`https://${window.location.hostname}:5000/api/v2/organizations/${organisationName}/tasks`,
      { headers: this.accountService.getAuthHeader() });
  }

  validateNewTaskName(organisationName: string, name: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `https://${window.location.hostname}:5000/api/terrarun/v1/organisation/${organisationName}/task-name-validate`,
        { 'name': name },
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

  create(organisationName: string, name: string, description: string, url: string, hmacKey: string, enabled: boolean): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `https://${window.location.hostname}:5000/api/v2/organizations/${organisationName}/tasks`,
        {
          data: {
            type: 'tasks', attributes: {
              'name': name,
              'description': description,
              'url': url,
              'category': 'tasks',
              'hmac-key': hmacKey,
              'enabled': enabled
            }
          }
        },
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

  updateAttributes(taskId: string, name: string, description: string, url: string, hmacKey: string, enabled: boolean): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.patch<any>(
        `https://${window.location.hostname}:5000/api/v2/tasks/${taskId}`,
        {
          data: {
            type: 'tasks', attributes: {
              'name': name,
              'description': description,
              'url': url,
              'category': 'tasks',
              'hmac-key': hmacKey,
              'enabled': enabled
            }
          }
        },
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

  getTaskDetailsById(taskId: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `https://${window.location.hostname}:5000/api/v2/tasks/${taskId}`,
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
