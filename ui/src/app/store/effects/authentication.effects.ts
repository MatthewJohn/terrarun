import { Injectable } from '@angular/core';
import { Action } from '@ngrx/store';
import { Router } from '@angular/router';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import 'rxjs/add/observable/of';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/switchMap';
import 'rxjs/add/operator/catch';
import { tap } from 'rxjs/operators';
import { of } from 'rxjs';
import { AccountService } from '../../account.service';
import { Observable } from 'rxjs';
import { AuthenticationActionTypes } from '../actions/authentication.actions';



@Injectable()
export class AuthenticationEffects {

  constructor(
    private actions$: Actions,
    private accountService: AccountService,
    private router: Router,
  ) {
  }

  userLogin$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthenticationActionTypes.LOGIN),
      exhaustMap(action =>
        this.appService.login(action.user).pipe(
          map(response => userActions.loginSuccess(response)),
          catchError((error: any) => of(userActions.loginFailure(error))))
      )
    )
  );
  
}
