import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { AccountService } from '../account.service';
import { AppState } from '../app.state';
import { LoginAction } from '../reducers/authentication.reducer';
import { LogIn } from '../../store/actions/authentication.actions';

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
    private store: Store<AppState>
  ) {}

  onSubmit(): void {
    let username = this.loginForm.value.username
    this.store.dispatch(new LogIn({username: this.loginForm.value.username, password: this.loginForm.value.password}))
    // this.accountService.login(
    //   username,
    //   this.loginForm.value.password
    // ).then((data) => {
    //   console.log('logged in');
    //   this.store.dispatch(new LogIn({loggedIn: true, userId: data.relationships['created-by'].data.id, username: username}))
      // localStorage.setItem('authToken', data.attributes.token);
      this.router.navigateByUrl('/');
    // }).catch(() => {
    //   console.log('Login failure');
    //});
  }

  ngOnInit(): void {
  }

}
