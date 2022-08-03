import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, Observer } from 'rxjs';
import { AccountService } from './account.service';


export interface AuthenticationStateType {
    authenticated: boolean | null;
    id: string | null;
    username: string | null;
};

@Injectable({
  providedIn: 'root'
})
export class StateService {

    authenticationState: BehaviorSubject<AuthenticationStateType> = new BehaviorSubject<AuthenticationStateType>({authenticated: null, id: null, username: null});

    constructor() {
        console.log("Created state object");
        this.authenticationState.subscribe((data) => {
            console.log("Authentication state updated...");
            console.log(data);
        })
    }

    getAuthenticationObserver(): Observer<any> {      
        return this.authenticationState;
    }

}
