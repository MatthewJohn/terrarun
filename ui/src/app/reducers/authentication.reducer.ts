
import { Action, createAction, createFeatureSelector, createReducer, createSelector, on, props, State } from '@ngrx/store';
import { AuthenticationState } from '../login/authenticationState.model';
import { AuthenticationActionTypes } from '../store/actions/authentication.actions';


export const initialState: AuthenticationState = {loggedIn: false, userId: null, username: null};

export const LoginAction = createAction('[ authentication ] Login', props<AuthenticationState>());
export const LogoutAction = createAction('[ authentication ] Logout');

export function reducer(state = initialState, action: any): State {
  switch (action.type) {
    case AuthenticationActionTypes.LOGIN_SUCCESS: {
      return {
        ...state,
        isAuthenticated: true,
        user: {
          token: action.payload.token,
          email: action.payload.email
        },
        errorMessage: null
      };
    }
    default: {
      return state;
    }
  }
}
