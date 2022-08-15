import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class PlanService {

  constructor(private http: HttpClient,
    private accountService: AccountService) { }

  getDetailsById(planId: string): Observable<any> {
    return this.http.get<any>(
      `https://${window.location.hostname}:5000/api/v2/plans/${planId}`,
      { headers: this.accountService.getAuthHeader() }
    );
  }

  getLog(planLogUrl: string): Observable<string> {
    return this.http.get(planLogUrl,
      { headers: {'Content-Type': 'text/html', ...this.accountService.getAuthHeader()},
        responseType: 'text' });
  }
}
