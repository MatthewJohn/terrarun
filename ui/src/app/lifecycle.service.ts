import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class LifecycleService {

  constructor(private http: HttpClient,
              private accountService: AccountService) { }

  getOrganisationLifecycles(organisationName: string): Observable<any> {
    return this.http.get<any>(
      `/api/v2/organizations/${organisationName}/lifecycles`,
      { headers: this.accountService.getAuthHeader() }).pipe(map((response) => response.data));
  }
}
