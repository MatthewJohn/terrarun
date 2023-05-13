import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AccountService } from '../account.service';
import { DataList } from '../interfaces/data';
import { ResponseObject } from '../interfaces/response';
import { TerraformVersion } from '../interfaces/terraform-version';

@Injectable({
  providedIn: 'root'
})
export class TerraformVersionService {

  constructor(
    private http: HttpClient,
    private accountService: AccountService
  ) { }

  getVersions(): Promise<ResponseObject<TerraformVersion>[]> {
    return new Promise((resolve, reject) => {
      this.http.get<any>(
        `/api/v2/tool-versions`,
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: DataList<ResponseObject<TerraformVersion>>) => {
          resolve(data.data);
        },
        error: () => {
          reject();
        }
      });
    });
  }
}