import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private http: HttpClient) {
  }

  getUserTokens(userId: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `https://${window.location.hostname}:5000/api/v2/users/${userId}/authentication-tokens`
      )
      .subscribe({
        next: data => resolve(data.data),
        error: () => reject()
      });
    });
  }
}
