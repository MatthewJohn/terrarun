import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AccountService } from '../account.service';

@Injectable({
  providedIn: 'root'
})
export class LifecycleEnvironmentService {

  constructor(
    private http: HttpClient,
    private accountService: AccountService
  ) { }

  delete(lifecycleEnvironmentId: string): Promise<null> {
    return new Promise((resolve, reject) => {
      this.http.delete<any>(
        `/api/v2/lifecycle-environments/${lifecycleEnvironmentId}`,
        {
          headers: this.accountService.getAuthHeader()
        }).subscribe({
          next: () => {
            resolve(null);
          },
          error: (err) => {
            reject(err);
          }
        });
    });
  }
}
