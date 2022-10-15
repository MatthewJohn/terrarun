import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { ProjectService } from './project.service';
import { StateService } from './state.service';

@Injectable({
  providedIn: 'root'
})
export class ProjectExistsGuard implements CanActivate {
  constructor(private stateService: StateService, private router: Router, private projectService: ProjectService) { }

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
      return new Promise<boolean>((resolve, reject) => {
        let organisationName = route.paramMap.get('organisationName') || '';
        let workspaceName = route.paramMap.get('workspaceName');

        let projectObserable: Observable<any>;
        if (workspaceName) {
          projectObserable = this.projectService.getDetailsByOrganisationNameAndWorkspaceName(organisationName, workspaceName)
        } else {
          projectObserable = this.projectService.getDetailsByName(
            organisationName,
            route.paramMap.get('projectName') || ''
          );
        }
        projectObserable.subscribe({
          next: (data) => {
            this.stateService.currentProject.next({id: data.data.id, name: data.data.attributes.name});
            this.stateService.currentRun.next({id: null});
            resolve(true);
          },
          error: (err) => {
            this.stateService.currentProject.next({id: null, name: null});
            this.stateService.currentRun.next({id: null});
            resolve(false);
          }
        });
    });
  }
}
