import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, Observer } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class StateService {

    authenticationState: Observable<any>;
    authenticationStateObserver: Observer<any> | null = null;

    constructor() {
        console.log("Created state object");
        this.authenticationState = new Observable<any>((observer) => {
            this.authenticationStateObserver = observer;
        });
        this.authenticationState.subscribe((data) => {
            console.log("Authentication state updated...");
            console.log(data);
        })
    }

    getAuthenticationObserver(): Observer<any> {
        if (this.authenticationStateObserver != null) {
            return this.authenticationStateObserver;
        }
        
        return this.getAuthenticationObserver();
    }

}
