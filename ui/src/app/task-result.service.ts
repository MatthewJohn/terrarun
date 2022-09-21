import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class TaskResultService {

  constructor(private http: HttpClient,
    private accountService: AccountService) { }

  getTaskResultDetailsById(taskResultId: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `https://${window.location.hostname}:5000/api/v2/task-results/${taskResultId}`,
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
