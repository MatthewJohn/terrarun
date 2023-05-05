import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AccountService } from '../account.service';
import { DataObject } from '../interfaces/data-object';
import { OauthClient } from '../interfaces/oauth-client';
import { ResponseItem } from '../interfaces/response';

@Injectable({
  providedIn: 'root'
})
export class OauthClientService {

  constructor(private http: HttpClient,
              private accountService: AccountService) { }


  create(organisationName: string, name: string, serviceProvider: string, httpUrl: string, apiUrl: string): Promise<DataObject<OauthClient>> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `/api/v2/organizations/${organisationName}/oauth-clients`,
        {
          data: {
            type: 'oauth-clients',
              attributes: {
                'name': name,
                'service-provider': serviceProvider,
                'http-url': httpUrl,
                'api-url': apiUrl
              }
          }
        },
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: ResponseItem<DataObject<OauthClient>>) => {
          resolve(data.data);
        },
        error: () => {
          reject();
        }
      });
    });
  }

  update(oauthClientId: string, attributes: {[key: string]: {value: any}}): Promise<DataObject<OauthClient>> {
    return new Promise((resolve, reject) => {
      this.http.patch<any>(
        `/api/v2/oauth-clients/${oauthClientId}`,
        {
          data: {
            type: 'oauth-clients',
              attributes: attributes
            }
        },
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: ResponseItem<DataObject<OauthClient>>) => {
          resolve(data.data);
        },
        error: () => {
          reject();
        }
      });
    });
  }

  getDetails(oauthClientId: string): Promise<DataObject<OauthClient>> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `/api/v2/oauth-clients/${oauthClientId}`,
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: ResponseItem<DataObject<OauthClient>>) => {
          resolve(data.data);
        },
        error: () => {
          reject();
        }
      });
    });
  }

  authorise(oauthClientId: string) {
    // Obtain authorisation endpoint
    this.getDetails(oauthClientId).then((oauthClientData: DataObject<OauthClient>) => {
      this.http.get<any>(oauthClientData.attributes['connect-path'])
    }).catch(() => {
      throw new Error("Unable to obtain oauth client details");
    })
  }
}