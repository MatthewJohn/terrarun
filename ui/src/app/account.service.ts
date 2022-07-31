import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AccountService {

  accountDetails: any = null;
  loggedIn: boolean | null = null;

  constructor(private http: HttpClient) {
  }

  isLoggedIn(): Promise<boolean> {
    return new Promise((resolve, reject) => {
      // If already determined if user is logged
      // in, return this status
      if (this.loggedIn !== null) {
        resolve(this.loggedIn);
      }
      // Otherwise, obtain account details
      // and return logged in status afterwards
      this.getAccountDetails().then(() => {
        resolve(this.loggedIn === null ? false : true);
      }).catch(() => {
        resolve(false);
      });
    });
  }

  login(username: string, password: string): Promise<string> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `https://${window.location.hostname}:5000/api/terrarun/v1/authenticate`,
        { 'username': username, 'password': password },
        { observe: 'response' }
      ).subscribe({
        next: (response) => {
          if (response.status == 200) {
            resolve(response.body.data.attributes.token);
          }
          reject();
        },
        error: () => {
          reject();
        }
      });
    });
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

  getAccountDetails(): Promise<any> {
    // @TODO: Cache these results
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `https://${window.location.hostname}:5000/api/v2/account/details`,
        { headers: this.getAuthHeader() }
      )
      .subscribe({
        next: response => {
          this.loggedIn = true;
          resolve(response);
        },
        error: () => {
          this.loggedIn = false;
          reject();
        }
      });
    });
  }
}
