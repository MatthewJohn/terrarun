import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class WorkspaceTaskService {

  constructor(private http: HttpClient,
    private accountService: AccountService) { }

  getWorkspaceTasksByWorkspace(workspaceId: string): Observable<any> {
    return this.http.get<any>(`https://${window.location.hostname}:5000/api/v2/workspaces/${workspaceId}/tasks`,
      { headers: this.accountService.getAuthHeader() });
  }

  associateTask(workspaceId: string, taskId: string, stage: string, enforcementLevel: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `https://${window.location.hostname}:5000/api/v2/workspaces/${workspaceId}/tasks`,
        {
          data: {
            type: 'workspace-tasks',
            attributes: {
              'enforcement-level': enforcementLevel,
              'stage': stage
            },
            relationships: {
              task: {
                data: {
                  id: taskId,
                  type: 'tasks'
                }
              }
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
}