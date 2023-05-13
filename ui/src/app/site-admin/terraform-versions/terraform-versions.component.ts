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

  // Set to false
  showEditForm: boolean = false;
  editTool: ResponseObject<AdminTerraformVersion> | null = null;

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

  onRowClick(toolId: string) {
    let toolData = this.terraformVersions.filter((value) => value.id === toolId);
    if (toolData.length !== 1) {
      return;
    }
    this.showEditForm = true;
    this.editTool = toolData[0];
  }

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.loadingData = true;
    this.terraformVersions = [];
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

  onCreateSubmit(attributes: AdminTerraformVersion) {
    this.adminTerraformVersionService.create(attributes).then(() => {
      this.loadData();
    });
  }

  onEditSubmit(attributes: AdminTerraformVersion) {
    // If edit tool is set, update item in service
    if (this.editTool) {
      this.adminTerraformVersionService.update(this.editTool.id, attributes).then(() => {
        this.loadData();
      });
      // Hide edit form
      this.editTool = null;
      this.showEditForm = false;
    }
  }
  onEditCancel() {
    // Unset edit tool
    this.editTool = null;
    this.showEditForm = false;
  }
  onEditDelete(toolId: string) {
    this.adminTerraformVersionService.delete(toolId).then(() => {
      this.loadData();
    });
    this.editTool = null;
    this.showEditForm = false;
  }
}
