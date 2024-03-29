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

  getTaskStageDetailsById(taskStageId: string): Observable<any> {
    return this.http.get<any>(
        `/api/v2/task-stages/${taskStageId}`,
        { headers: this.accountService.getAuthHeader() }
      );
  }
}
