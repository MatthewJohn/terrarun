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
    var token = this.accountService.login(
      this.loginForm.value.username,
      this.loginForm.value.password
    );
    if (token) {
      localStorage.setItem('authToken', token);
      this.router.navigateByUrl('/');
    }
    this.loginForm.reset();
  }

  ngOnInit(): void {
  }

}
