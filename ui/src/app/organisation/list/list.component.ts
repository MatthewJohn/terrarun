import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { OrganisationService } from 'src/app/organisation.service';

@Component({
  selector: 'app-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.scss']
})
export class ListComponent implements OnInit {

  organisations: any[] = [];
  tableColumns: string[] = ['name'];

  constructor(private organisationService: OrganisationService,
              private router: Router) { }

  ngOnInit(): void {
    this.organisationService.getAll().then((data) => {
      console.log(data.data);
      this.organisations = [data.data];
      this.organisations = Array.from(
        {length: data.data.length},
        (_, n) => ({'data': data.data[n]})
      );
    });
  }

  onOrganisationClick(target: any) {
    this.router.navigateByUrl(`/${target.data.id}`)
  }
}
