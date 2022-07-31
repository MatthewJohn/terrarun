import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private http: HttpClient) {
  }

  getUserTokens(userId: string): any {
    this.http.get<any>(
      `https://${window.location.host}:5001/api/v2/users/${userId}/authentication-tokens`,
      { observe: 'response' }
    )
    .subscribe(response => {
      return response.body.data;
    });
  }
}
