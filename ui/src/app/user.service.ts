import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  authTokens: any[] = [];
  userId: string;

  constructor(userId: string, private http: HttpClient) {
    this.userId = userId;
  }

  getUserTokens(): any {
    this.http.get<any>(
      `https://${window.location.host}:5001/api/v2/users/${this.userId}/authentication-tokens`,
      { observe: 'response' }
    )
    .subscribe(response => {
      this.authTokens = response.body.data;
    });
  }
}
