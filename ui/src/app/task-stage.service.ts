import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class TaskStageService {

  constructor(private http: HttpClient,
    private accountService: AccountService) { }

  getTaskStageDetailsById(taskStageId: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `https://${window.location.hostname}:5000/api/v2/task-stages/${taskStageId}`,
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
