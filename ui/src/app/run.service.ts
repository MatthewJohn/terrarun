import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AccountService } from './account.service';
import { RunCreateAttributes } from './interfaces/run-create-attributes';

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

  create(workspaceId: string, runAttributes: RunCreateAttributes, configurationVersionId: string|undefined=undefined): Promise<any> {
    return new Promise((resolve, reject) => {
      let relationships: {[key: string]: {data: {type: string, id: string}}} = {
        "workspace": {"data": {"type": "workspaces","id": workspaceId}},
      };

      if (configurationVersionId) {
        relationships["configuration-version"] = {
          "data": {
            "id": configurationVersionId,
            "type": "configuration-versions"
          }
        }
      }

      this.http.post<any>(`/api/v2/runs`,
      { "data": {
        "type":"runs",
        "attributes": runAttributes,
        "relationships": relationships}},
      { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: any) => {
          resolve(data);
        },
        error: (err) => {
          reject(err);
        }
      });
    })
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
  discardRun(runId: string): Observable<any> {
    return this.http.post<any>(
      `/api/v2/runs/${runId}/actions/discard`,
      {},
      { headers: this.accountService.getAuthHeader() }
    )
  }
}
