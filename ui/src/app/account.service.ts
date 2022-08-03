import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { StateService } from './state.service';

@Injectable({
  providedIn: 'root'
})
export class AccountService {

  constructor(private http: HttpClient,
              private stateService: StateService) {
  }

  login(username: string, password: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `https://${window.location.hostname}:5000/api/terrarun/v1/authenticate`,
        { 'username': username, 'password': password },
        { observe: 'response' }
      ).subscribe({
        next: (response) => {
          if (response.status == 200) {
            localStorage.setItem('authToken', response.body.data.attributes.token);

            // Perform get account details, which will send notification
            // for new logged in state
            this.getAccountDetails();

            resolve();
            return;
          }
          this.logout();
          reject();
          return;
        },
        error: () => {
          this.logout();
          reject();
        }
      });
    });
  }

  logout(): void {
    // Notify about logout
    this.stateService.getAuthenticationObserver().next({
      authenticated: false,
      username: null,
      id: null
    });
    localStorage.removeItem('authToken');
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

  getAccountDetails(): void {
    this.http.get<any>(
      `https://${window.location.hostname}:5000/api/v2/account/details`,
      { headers: this.getAuthHeader() }
    )
    .subscribe({
      next: response => {
        console.log("putting into observer");
        this.stateService.getAuthenticationObserver().next({
          authenticated: true,
          username: response.data.username,
          id: response.data.id
        })
      },
      error: () => {
        this.stateService.getAuthenticationObserver().next({
          authenticated: false,
          username: null,
          id: null
        })
      }
    });
  }
}
