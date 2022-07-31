import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AccountService {

  accountDetails = {};
  loggedIn: boolean | null = null;

  constructor(private http: HttpClient) {
  }

  isLoggedIn(): boolean {
    return false; // Switch to `false` to make OnlyLoggedInUsersGuard work
  }
  getAccountDetails(): any {
    this.http.get<any>(
      `https://${window.location.host}:5001/api/v2/account/details`,
      { observe: 'response' }
    )
    .subscribe(response => {
      if (response.status == 403) {
        this.loggedIn = false;
      } else {
        this.accountDetails = response.body;
      }
    });
  }
}
