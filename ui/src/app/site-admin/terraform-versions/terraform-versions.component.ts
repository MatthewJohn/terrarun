import { Component, OnInit } from '@angular/core';
import { NbDialogService } from '@nebular/theme';
import { Subject } from 'rxjs';
import { ErrorDialogueComponent } from 'src/app/components/error-dialogue/error-dialogue.component';
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

  editToolLoading: boolean = false;
  createToolLoading: boolean = false;

  resetCreateForm: Subject<void> = new Subject<void>();
  resetEditForm: Subject<void> = new Subject<void>();

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
    private adminTerraformVersionService: AdminTerraformVersionService,
    private dialogService: NbDialogService
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
    this.createToolLoading = true;
    this.adminTerraformVersionService.create(attributes).then(() => {
      // Reset new form and reload table data
      this.createToolLoading = false;
      this.resetCreateForm.next();
      this.loadData();
    }).catch((err) => {
      this.createToolLoading = false;
      this.dialogService.open(ErrorDialogueComponent, {
        context: {title: err.error.errors?.[0].title, data: err.error.errors?.[0].detail}
      });
    });;
  }

  onEditSubmit(attributes: AdminTerraformVersion) {
    // If edit tool is set, update item in service
    if (this.editTool) {
      this.editToolLoading = true;
      this.adminTerraformVersionService.update(this.editTool.id, attributes).then(() => {
        // Hide edit form
        this.editTool = null;
        this.showEditForm = false;
        this.resetEditForm.next();
        this.editToolLoading = false;

        // Reload table data
        this.loadData();
      }).catch((err) => {
        this.editToolLoading = false;
        this.dialogService.open(ErrorDialogueComponent, {
          context: {title: err.error.errors?.[0].title, data: err.error.errors?.[0].detail}
        });
      });
    }
  }
  onEditCancel() {
    // Unset edit tool
    this.editTool = null;
    this.showEditForm = false;
  }
  onEditDelete(toolId: string) {
    this.editToolLoading = true;
    this.adminTerraformVersionService.delete(toolId).then(() => {
      // Unset edit tool and reset form
      this.editTool = null;
      this.showEditForm = false;
      this.resetCreateForm.next();
      this.editToolLoading = false;

      // Reload table data
      this.loadData();
    }).catch((err) => {
      this.editToolLoading = false;
      this.dialogService.open(ErrorDialogueComponent, {
        context: {title: err.error.errors?.[0].title, data: err.error.errors?.[0].detail}
      });
    });
  }
}
