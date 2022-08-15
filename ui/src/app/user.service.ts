import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private http: HttpClient, private accountService: AccountService) {
  }

  getUserDetailsById(userId: string): Observable<any> {
    return this.http.get<any>(
      `https://${window.location.hostname}:5000/api/v2/users/${userId}`,
      { headers: this.accountService.getAuthHeader() }
    );
  }

  getUserTokens(userId: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `https://${window.location.hostname}:5000/api/v2/users/${userId}/authentication-tokens`,
        { headers: this.accountService.getAuthHeader() }
      )
      .subscribe({
        next: data => resolve(data.data),
        error: () => reject()
      });
    });
  }

  createUserToken(userId: string, description: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `https://${window.location.hostname}:5000/api/v2/users/${userId}/authentication-tokens`,
        { data: {type: 'authentication-tokens', attributes: {'description': description}}},
        { headers: this.accountService.getAuthHeader() }
      )
      .subscribe({
        next: data => resolve(data.data),
        error: () => reject()
      });
    });
  }
}
