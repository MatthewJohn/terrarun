import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, Observer } from 'rxjs';
import { AccountService } from './account.service';


export interface AuthenticationStateType {
    authenticated: boolean | null;
    id: string | null;
    username: string | null;
    siteAdmin: boolean | null;
};

export interface OrganisationStateType {
    id: string | null;
    name: string | null;
}

export interface ProjectStateType {
    id: string | null;
    name: string | null;
}

export interface WorkspaceStateType {
    id: string | null;
    name: string | null;
}

export interface RunStateType {
    id: string | null;
}

export interface LifecycleStateType {
    id: string | null;
    name: string | null;
}


@Injectable({
  providedIn: 'root'
})
export class StateService {

    authenticationState: BehaviorSubject<AuthenticationStateType> = new BehaviorSubject<AuthenticationStateType>({authenticated: null, id: null, username: null, siteAdmin: null});
    currentOrganisation: BehaviorSubject<OrganisationStateType> = new BehaviorSubject<OrganisationStateType>({id: null, name: null});
    currentProject: BehaviorSubject<ProjectStateType> = new BehaviorSubject<ProjectStateType>({id: null, name: null});
    currentWorkspace: BehaviorSubject<WorkspaceStateType> = new BehaviorSubject<WorkspaceStateType>({id: null, name: null});
    currentRun: BehaviorSubject<RunStateType> = new BehaviorSubject<RunStateType>({id: null});
    currentLifecycle: BehaviorSubject<LifecycleStateType> = new BehaviorSubject<LifecycleStateType>({id: null, name: null});

    constructor() {
        console.log("Created state object");
        this.authenticationState.subscribe((data) => {
            console.log("Authentication state updated...");
            console.log(data);
        });
    }

    getAuthenticationObserver(): Observer<any> {      
        return this.authenticationState;
    }

}
