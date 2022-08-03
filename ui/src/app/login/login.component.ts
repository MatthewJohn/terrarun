import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { AccountService } from '../account.service';

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
    private router: Router
  ) {}

  onSubmit(): void {
    this.accountService.login(
      this.loginForm.value.username,
      this.loginForm.value.password
    ).then((token) => {
      console.log('logged in');
      localStorage.setItem('authToken', token);
      this.router.navigateByUrl('/');
    }).catch(() => {
      console.log('Login failure');
    });
  }

  ngOnInit(): void {
  }

}
