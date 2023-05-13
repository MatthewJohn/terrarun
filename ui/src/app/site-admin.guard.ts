import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { StateService } from './state.service';

@Injectable({
  providedIn: 'root'
})
export class SiteAdminGuard implements CanActivate {

  constructor(private stateService: StateService, private router: Router) { }

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    return new Promise((resolve, reject) => {
      this.stateService.authenticationState.subscribe((data) => {
        console.log(data);
        if (data.siteAdmin === true) {
          resolve(true);
        } else if (data.siteAdmin === false) {
          this.router.navigateByUrl('/');
          resolve(false);
        }
      })
    });
  }
  
}
