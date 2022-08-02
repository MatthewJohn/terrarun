import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { OrganisationService } from 'src/app/organisation.service';

@Component({
  selector: 'app-create',
  templateUrl: './create.component.html',
  styleUrls: ['./create.component.scss']
})
export class CreateComponent implements OnInit {

  nameValid: boolean = false;
  form = this.formBuilder.group({
    name: ''
  });

  constructor(private formBuilder: FormBuilder, private organisationService: OrganisationService) { }

  validateName(): void {
    this.organisationService.validateNewOrganisationName(this.form.value.name).then((validationResult) => {
      console.log(validationResult);
      this.nameValid = validationResult.valid;
    });
  }

  onCreate(): void {

  }

  ngOnInit(): void {
  }

}
