import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class ApplyService {

  constructor(private http: HttpClient,
    private accountService: AccountService) { }

  getDetailsById(applyId: string): Observable<any> {
    return this.http.get<any>(
      `/api/v2/applies/${applyId}`,
      { headers: this.accountService.getAuthHeader() }
    );
  }

  getLog(applyLogUrl: string): Observable<string> {
    return this.http.get(applyLogUrl,
      { headers: {'Content-Type': 'text/html', ...this.accountService.getAuthHeader()},
        responseType: 'text' });
  }
}
