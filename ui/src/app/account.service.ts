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

  isLoggedIn(): boolean {
    // If already determined if user is logged
    // in, return this status
    if (this.loggedIn !== null) {
      return this.loggedIn;
    }
    // Otherwise, obtain account details
    // and return logged in status afterwards
    this.getAccountDetails().then(() => {
      return this.loggedIn;
    });
    // Fallback to false
    return false;
  }
  getAccountDetails(): Promise<any> {
    // @TODO: Cache these results
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `https://${window.location.host}:5001/api/v2/account/details`,
        { observe: 'response' }
      )
      .subscribe(response => {
        if (response.status == 403) {
          this.loggedIn = false;
          reject();
        } else {
          this.loggedIn = true;
          resolve(response.body.data);
        }
      });
    });
  }
}
