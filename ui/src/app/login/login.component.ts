import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { AccountService } from '../account.service';
import { LoginAction } from '../reducers/authenticationState.reducer';
import { AuthenticationState } from './authenticationState.model';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

  loginForm = this.formBuilder.group({
    username: '',
    password: ''
  });

  constructor(
    private formBuilder: FormBuilder,
    private accountService: AccountService,
    private router: Router,
    private store: Store<AuthenticationState>
  ) {}

  onSubmit(): void {
    let username = this.loginForm.value.username
    this.accountService.login(
      username,
      this.loginForm.value.password
    ).then((data) => {
      console.log('logged in');
      this.store.dispatch(LoginAction({loggedIn: true, userId: data.relationships['created-by'].data.id, username: username}))
      localStorage.setItem('authToken', data.attributes.token);
      this.router.navigateByUrl('/');
    // }).catch(() => {
    //   console.log('Login failure');
    });
  }

  ngOnInit(): void {
  }

}
