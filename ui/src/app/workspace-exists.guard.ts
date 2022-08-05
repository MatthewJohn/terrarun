import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { StateService } from './state.service';
import { WorkspaceService } from './workspace.service';

@Injectable({
  providedIn: 'root'
})
export class WorkspaceExistsGuard implements CanActivate {
  constructor(private stateService: StateService, private router: Router, private workspaceService: WorkspaceService) { }

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
      return new Promise<boolean>((resolve, reject) => {
        this.workspaceService.getDetailsByName(route.paramMap.get('organisationName') || '',
                                               route.paramMap.get('workspaceName') || '').subscribe({
          next: (data) => {
            console.log("workspace fouind!");
            this.stateService.currentWorkspace.next({id: data.id, name: data.attributes.name});
            resolve(true);
          },
          error: (err) => {
            this.stateService.currentOrganisation.next({id: null, name: null});
            resolve(false);
          }
        });
    });
  }
  
}
