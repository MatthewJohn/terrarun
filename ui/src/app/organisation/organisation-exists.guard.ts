import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, CanActivateChild, CanDeactivate, CanLoad, Route, Router, RouterStateSnapshot, UrlSegment, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { OrganisationService } from '../organisation.service';
import { StateService } from '../state.service';

@Injectable({
  providedIn: 'root'
})
export class OrganisationExistsGuard implements CanActivate {

  constructor(private stateService: StateService, private router: Router, private organisationService: OrganisationService) { }

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
      return new Promise<boolean>((resolve, reject) => {
        this.organisationService.getOrganisationDetails(route.paramMap.get('organisationId') || '').then((data) => {
          this.stateService.currentOrganisation.next({id: data.id, name: data.attributes.name});
          resolve(true);
        }).catch(() => {
          reject();
        });
    });
  }
}
