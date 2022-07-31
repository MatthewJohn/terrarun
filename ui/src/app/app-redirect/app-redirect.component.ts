import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-app-redirect',
  templateUrl: './app-redirect.component.html',
  styleUrls: ['./app-redirect.component.scss']
})
export class AppRedirectComponent implements OnInit {

  constructor(private router: Router) { }

  ngOnInit(): void {
    let url = this.router.url;
    console.log(url);

    this.router.navigateByUrl(url.replace(/^\/app/, ""));
  }

}
