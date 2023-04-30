import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class RunService {

  constructor(private http: HttpClient,
    private accountService: AccountService) { }

  getDetailsById(runId: string): Observable<any> {
    return this.http.get<any>(
      `/api/v2/runs/${runId}`,
      { headers: this.accountService.getAuthHeader() }
    );
  }

  getAuditEventsByRunId(runId: string): Observable<any> {
    return this.http.get<any>(
      `/api/v2/runs/${runId}/relationships/audit-events`,
      { headers: this.accountService.getAuthHeader() }
    );
  }

  applyRun(runId: string): Observable<any> {
    return this.http.post<any>(
      `/api/v2/runs/${runId}/actions/apply`,
      {},
      { headers: this.accountService.getAuthHeader() }
    )
  }
  cancelRun(runId: string): Observable<any> {
    return this.http.post<any>(
      `/api/v2/runs/${runId}/actions/cancel`,
      {},
      { headers: this.accountService.getAuthHeader() }
    )
  }
}
