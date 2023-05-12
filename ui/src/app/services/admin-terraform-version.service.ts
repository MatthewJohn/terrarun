import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AccountService } from '../account.service';
import { AdminTerraformVersion } from '../interfaces/admin-terraform-version';
import { DataList } from '../interfaces/data';
import { ResponseObject } from '../interfaces/response';

@Injectable({
  providedIn: 'root'
})
export class AdminTerraformVersionService {

  constructor(
    private http: HttpClient,
    private accountService: AccountService
  ) { }

  getVersions(): Promise<ResponseObject<AdminTerraformVersion>[]> {
    return new Promise((resolve, reject) => {
        this.http.get<any>(
          `/api/v2/admin/terraform-versions`,
          { headers: this.accountService.getAuthHeader() }
        ).subscribe({
          next: (data: DataList<ResponseObject<AdminTerraformVersion>>) => {
            resolve(data.data);
          },
          error: () => {
            reject();
          }
        });
      });
  }
}
