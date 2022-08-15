import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { RunService } from './run.service';
import { StateService } from './state.service';

@Injectable({
  providedIn: 'root'
})
export class RunExistsGuard implements CanActivate {
  constructor(
    private stateService: StateService,
    private runService: RunService) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
      return new Promise<boolean>((resolve, reject) => {
        this.stateService.currentOrganisation.subscribe((org) => {
          if (org.id) {
            this.stateService.currentWorkspace.subscribe((workspace) => {
              if (workspace.id) {
                let runId: string | null = route.paramMap.get('runId');
                if (runId) {
                  this.runService.getDetailsById(runId).subscribe({
                    next: (data) => {
                      this.stateService.currentRun.next({id: data.data.id});
                      resolve(true);
                    },
                    error: (err) => {
                      this.stateService.currentRun.next({id: null});
                      resolve(false);
                    }
                  })
                }
              }
            });
          }
        })
    });
  }
  
}
