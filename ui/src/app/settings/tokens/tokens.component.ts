import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AccountService } from 'src/app/account.service';
import { UserService } from 'src/app/user.service';
import { FormBuilder } from '@angular/forms';
import { StateService } from 'src/app/state.service';

@Component({
  selector: 'app-tokens',
  templateUrl: './tokens.component.html',
  styleUrls: ['./tokens.component.scss']
})
export class TokensComponent implements OnInit {

  tokens: any = [];
  createdToken: any = null;
  userId: string | null = null;

  createTokenForm = this.formBuilder.group({
    description: ''
  });

  constructor(private formBuilder: FormBuilder,
              private stateService: StateService,
              private userService: UserService) { }

  ngOnInit(): void {
    this.stateService.authenticationState.subscribe((data) => {
      if (data.id) {
        this.userId = data.id;
        this.userService.getUserTokens(data.id).then((tokens) => {
          this.tokens = tokens;
        });
      }
    });
  }

  onCreateTokenFormSubmit(): void {
    if (this.userId) {
      this.userService.createUserToken(this.userId,
                                        this.createTokenForm.value.description).then((token) => {
        this.createdToken = token;
      });
    }
  }
}
