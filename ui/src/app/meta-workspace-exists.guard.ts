import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { MetaWorkspaceService } from './meta-workspace.service';
import { StateService } from './state.service';

@Injectable({
  providedIn: 'root'
})
export class MetaWorkspaceExistsGuard implements CanActivate {
  constructor(private stateService: StateService, private router: Router, private metaWorkspaceService: MetaWorkspaceService) { }

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
      return new Promise<boolean>((resolve, reject) => {
        this.metaWorkspaceService.getDetailsByName(route.paramMap.get('organisationName') || '',
                                                   route.paramMap.get('metaWorkspaceName') || '').subscribe({
          next: (data) => {
            this.stateService.currentMetaWorkspace.next({id: data.data.id, name: data.data.attributes.name});
            this.stateService.currentRun.next({id: null});
            resolve(true);
          },
          error: (err) => {
            this.stateService.currentMetaWorkspace.next({id: null, name: null});
            this.stateService.currentRun.next({id: null});
            resolve(false);
          }
        });
    });
  }
  
}
