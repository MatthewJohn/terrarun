import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';
import { ProjectService } from 'src/app/project.service';
import { StateService } from 'src/app/state.service';
import { WorkspaceService } from 'src/app/workspace.service';

@Component({
  selector: 'app-overview',
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.scss']
})
export class OverviewComponent implements OnInit {

  currentProject: Observable<any>;
  workspaceList: string[];
  workspaces: Map<string, Observable<any>>;

  constructor(
    private stateService: StateService,
    private projectService: ProjectService,
    private workspaceService: WorkspaceService,
    private router: Router
  ) {
    this.currentProject = stateService.currentProject;
    this.workspaceList = [];
    this.workspaces = new Map<string, Observable<any>>();

    this.stateService.currentOrganisation.subscribe((currentOrganisation) => {
      this.stateService.currentProject.subscribe((currentProject) => {
        // Get list of environments from project details
        if (currentOrganisation.name && currentProject.name) {
          this.projectService.getDetailsByName(currentOrganisation.name, currentProject.name).subscribe((projectDetails) => {

            let workspaces = projectDetails.data.relationships.workspaces.data;

            // Sort workspaces by order
            workspaces.sort((a: any, b: any) => {
              return a.order > b.order;
            });

            // Obtain workspace details and place into workspaces
            for (let workspace of workspaces) {
              this.workspaceList.push(workspace.id);
              this.workspaces.set(workspace.id, this.workspaceService.getDetailsById(workspace.id));
              // this.workspaceService.getDetailsById(workspace.id).subscribe((workspaceDetails) => {
              //   this.workspaces.set(workspaceDetails.data.id, workspaceDetails);
              // });
            }
          })
        }
      })
    })
  }

  onWorkspaceClick(workspaceId: string): void {
    console.log('Redirecting to: ', `/${this.stateService.currentOrganisation.value?.name}/${workspaceId}`);
    this.router.navigateByUrl(`/${this.stateService.currentOrganisation.value?.name}/${workspaceId}`)
  }

  ngOnInit(): void {
  }

}
