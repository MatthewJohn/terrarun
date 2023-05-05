import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { OrganisationStateType, StateService } from 'src/app/state.service';

@Component({
  selector: 'app-overview',
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.scss']
})
export class OverviewComponent implements OnInit {


  currentOrganisation: OrganisationStateType | null = null;

  constructor(
    private state: StateService,
    private router: Router,
    private route: ActivatedRoute) {

      this.state.currentOrganisation.subscribe((organisationData) => {
        this.currentOrganisation = organisationData;
      });
  }

  ngOnInit(): void {
  }

  handleNewVcsClick() {
    if ((this.currentOrganisation)) {
      this.router.navigateByUrl(`/${this.currentOrganisation.id}/settings/version-control/new`)
    }
  }
}
