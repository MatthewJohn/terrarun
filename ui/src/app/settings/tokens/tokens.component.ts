import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AccountService } from 'src/app/account.service';
import { UserService } from 'src/app/user.service';
import { FormBuilder } from '@angular/forms';

@Component({
  selector: 'app-tokens',
  templateUrl: './tokens.component.html',
  styleUrls: ['./tokens.component.scss']
})
export class TokensComponent implements OnInit {

  tokens: any = [];
  createdToken: any = null;

  createTokenForm = this.formBuilder.group({
    description: ''
  });

  constructor(private formBuilder: FormBuilder,
              private accountService: AccountService,
              private userService: UserService) { }

  ngOnInit(): void {
    this.accountService.getAccountDetails().then((accountDetails) => {
      this.userService.getUserTokens(accountDetails.id).then((tokens) => {
        this.tokens = tokens;
      });
    });
  }

  onCreateTokenFormSubmit(): void {
    this.accountService.getAccountDetails().then((accountDetails) => {
      this.userService.createUserToken(accountDetails.id,
                                       this.createTokenForm.value.description).then((token) => {
        this.createdToken = token;
      });
    });
  }
}
