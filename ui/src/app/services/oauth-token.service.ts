import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AccountService } from '../account.service';
import { ResponseObject, ResponseObjectWithRelationships } from '../interfaces/response';
import { OauthClient } from '../interfaces/oauth-client';
import { DataItem, DataList } from '../interfaces/data';
import { AuthorisedRepo, AuthorisedRepoRelationships } from '../interfaces/authorised-repo';

@Injectable({
  providedIn: 'root'
})
export class OauthTokenService {

  constructor(private http: HttpClient,
              private accountService: AccountService) { }

  getAuthorisedRepos(oauthTokenId: string): Promise<ResponseObjectWithRelationships<AuthorisedRepo, AuthorisedRepoRelationships>[]> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `/api/v2/oauth-tokens/${oauthTokenId}/authorized-repos`,
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: DataList<ResponseObjectWithRelationships<AuthorisedRepo, AuthorisedRepoRelationships>>) => {
          resolve(data.data);
        },
        error: () => {
          reject();
        }
      });
    });
  }
}