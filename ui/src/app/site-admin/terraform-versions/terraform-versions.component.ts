import { Component, OnInit } from '@angular/core';
import { AdminTerraformVersion } from 'src/app/interfaces/admin-terraform-version';
import { DataItem } from 'src/app/interfaces/data';
import { ResponseObject } from 'src/app/interfaces/response';
import { AdminTerraformVersionService } from 'src/app/services/admin-terraform-version.service';

@Component({
  selector: 'app-terraform-versions',
  templateUrl: './terraform-versions.component.html',
  styleUrls: ['./terraform-versions.component.scss']
})
export class TerraformVersionsComponent implements OnInit {

  loadingData: boolean = true;
  terraformVersions: ResponseObject<AdminTerraformVersion>[] = [];
  terraformVersionsRowData: DataItem<ResponseObject<AdminTerraformVersion>>[] = [];

  columnNames: {[key: string]: string} = {
    'version': 'Version',
    'url': 'Download Url',
    'checksum-url': 'Checksum URL',
    'sha': 'Checksum SHA',
    'enabled': 'Enabled',
    'deprecated': 'Deprecated',
    'deprecated-message': 'Deprecated warning'
  };
  tableColumns: string[] = ['version', 'url', 'checksum-url', 'sha', 'enabled', 'deprecated', 'deprecated-message'];

  constructor(
    private adminTerraformVersionService: AdminTerraformVersionService
  ) { }

  ngOnInit(): void {
    this.adminTerraformVersionService.getVersions(
    ).then((terraformVersions: ResponseObject<AdminTerraformVersion>[]) => {
      this.terraformVersions = terraformVersions;
      this.terraformVersionsRowData = this.terraformVersions.map((val) => {
        return {
          data: {
            ...val,
            attributes: {
              ...val.attributes,
              'url': val.attributes.url || 'Default URL',
              'checksum-url': val.attributes['checksum-url'] || 'Default Checksum URL',
              'sha': val.attributes.sha || 'Obtained from Checksum URL',
            }
          }
        };
      });
      this.loadingData = false;
    })
  }
}
