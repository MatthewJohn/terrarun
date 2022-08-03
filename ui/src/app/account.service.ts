import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AccountService {

  constructor(private http: HttpClient) {
  }

  login(username: string, password: string): Observable<any> {
      return this.http.post<any>(
        `https://${window.location.hostname}:5000/api/terrarun/v1/authenticate`,
        { 'username': username, 'password': password }
      );
  }

  getAuthHeader(): {Authorization: string} | {} {
    let authToken = localStorage.getItem('authToken');
    if (authToken) {
      return {
        Authorization: `Bearer ${authToken}`
      };
    }
    return {};
  }

  getAccountDetails(): Observable<any> {
    // @TODO: Cache these results
    return this.http.get<any>(
      `https://${window.location.hostname}:5000/api/v2/account/details`,
      { headers: this.getAuthHeader() }
    );
  }
}
