import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';

@Component({
  selector: 'app-new',
  templateUrl: './new.component.html',
  styleUrls: ['./new.component.scss']
})
export class NewComponent implements OnInit {

  createVcsIntegrationForm = this.formBuilder.group({
    name: '',
    provider: ''
  });

  constructor(
    private formBuilder: FormBuilder,
  ) {
  }

  ngOnInit(): void {
  }

  onSetBasicDetails() {
    console.log("Called onSetBasicDetails")
  }

}
