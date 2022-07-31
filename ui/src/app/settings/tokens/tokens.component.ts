import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AccountService } from 'src/app/account.service';
import { UserService } from 'src/app/user.service';

@Component({
  selector: 'app-tokens',
  templateUrl: './tokens.component.html',
  styleUrls: ['./tokens.component.scss']
})
export class TokensComponent implements OnInit {

  tokens: any;

  constructor(private http: HttpClient,
              private accountService: AccountService,
              private userService: UserService) { }

  ngOnInit(): void {
    this.accountService.getAccountDetails().then((accountDetails) => {
      this.tokens = this.userService.getUserTokens(accountDetails.id)
    });
  }
}
