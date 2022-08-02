import { Component, OnInit } from '@angular/core';
import { OrganisationService } from 'src/app/organisation.service';

@Component({
  selector: 'app-create',
  templateUrl: './create.component.html',
  styleUrls: ['./create.component.scss']
})
export class CreateComponent implements OnInit {

  nameValid: boolean = false;

  constructor(private organisationService: OrganisationService) { }

  validateName(): void {
    // this.organisationService.validateNewOrganisationName()
    this.nameValid = true;
  }

  onCreate(): void {

  }

  ngOnInit(): void {
  }

}
