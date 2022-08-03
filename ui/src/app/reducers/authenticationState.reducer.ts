
import { Action, createAction, createReducer, on, props } from '@ngrx/store';
import { AuthenticationState } from '../login/authenticationState.model';


export const initialState: AuthenticationState = {loggedIn: false, userId: null, username: null};

export const LoginAction = createAction('[ authentication ] Login', props<AuthenticationState>());
export const LogoutAction = createAction('[ authentication ] Logout');

const _authenticationReducer = createReducer(
  initialState,
  on(LoginAction, (state, payload) => { return payload;}),
  on(LogoutAction, (state) => { return initialState;})
);

export function authenticationReducer(state: any, action: Action) {
  return _authenticationReducer(state, action);
}