import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AccountService } from '../account.service';
import { AdminTerraformVersion } from '../interfaces/admin-terraform-version';
import { DataItem, DataList } from '../interfaces/data';
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

  create(attributes: AdminTerraformVersion): Promise<ResponseObject<AdminTerraformVersion>> {
    return new Promise((resolve, reject) => {
      this.http.post<any>(
        `/api/v2/admin/terraform-versions`,
        {'type': 'terraform-versions', 'attributes': attributes},
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: DataItem<ResponseObject<AdminTerraformVersion>>) => {
          resolve(data.data);
        },
        error: (err) => {
          reject(err);
        }
      });
    });
  }

  update(toolId: string, attributes: AdminTerraformVersion): Promise<ResponseObject<AdminTerraformVersion>> {
    return new Promise((resolve, reject) => {
      this.http.patch<any>(
        `/api/v2/admin/terraform-versions/${toolId}`,
        {'type': 'terraform-versions', 'id': toolId, 'attributes': attributes},
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: DataItem<ResponseObject<AdminTerraformVersion>>) => {
          resolve(data.data);
        },
        error: (err) => {
          reject(err);
        }
      });
    });
  }

  delete(toolId: string): Promise<null> {
    return new Promise((resolve, reject) => {
      this.http.delete<any>(
        `/api/v2/admin/terraform-versions/${toolId}`,
        { headers: this.accountService.getAuthHeader() }
      ).subscribe({
        next: (data: DataItem<ResponseObject<AdminTerraformVersion>>) => {
          resolve(null);
        },
        error: (err) => {
          reject(err);
        }
      });
    });
  }
}
