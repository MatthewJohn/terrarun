import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { LifecycleService } from '../services/lifecycle.service';
import { StateService } from '../state.service';

@Injectable({
  providedIn: 'root'
})
export class LifecycleExistsGuard implements CanActivate {
  constructor(private stateService: StateService, private router: Router, private lifecycleService: LifecycleService) { }

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    return new Promise<boolean>((resolve, reject) => {
      this.lifecycleService.getByName(
        route.paramMap.get('organisationName') || '',
        route.paramMap.get('lifecycleName') || ''
      ).then((data) => {
        this.stateService.currentLifecycle.next({ id: data.id, name: data.attributes.name });
        resolve(true);
      }).catch((err) => {
        this.stateService.currentWorkspace.next({ id: null, name: null });
        this.stateService.currentRun.next({ id: null });
        resolve(false);
      });
    });
  }
}
