import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { lastValueFrom, Observable } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  cachedUserDetailsById: any;

  constructor(private http: HttpClient, private accountService: AccountService) {
    this.cachedUserDetailsById = {};
  }

  getUserDetailsById(userId: string): Observable<any> {
    return this.http.get<any>(
      `/api/v2/users/${userId}`,
      { headers: this.accountService.getAuthHeader() }
    );
  }

  async getUserDetailsByIdSync(userId: string): Promise<any> {
    if (this.cachedUserDetailsById[userId] !== undefined) {
      return this.cachedUserDetailsById[userId];
    }
    var result = await lastValueFrom(this.http.get<any>(
      `/api/v2/users/${userId}`,
      { headers: this.accountService.getAuthHeader() }
    ));
    this.cachedUserDetailsById[userId];
    return result;
  }

  getUserTokens(userId: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `/api/v2/users/${userId}/authentication-tokens`,
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
        `/api/v2/users/${userId}/authentication-tokens`,
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
