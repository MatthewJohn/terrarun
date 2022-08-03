import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { map, Observable, switchMap } from 'rxjs';
import { OrganisationService } from 'src/app/organisation.service';

@Component({
  selector: 'app-workspace-list',
  templateUrl: './workspace-list.component.html',
  styleUrls: ['./workspace-list.component.scss']
})
export class WorkspaceListComponent implements OnInit {

  workspaces$: Observable<any>;
  tableColumns: string[] = ['name'];
  organisationId: string | null = null;

  constructor(private organisationService: OrganisationService,
              private router: Router,
              private route: ActivatedRoute) {
    this.workspaces$ = this.route.paramMap.pipe(
      switchMap(params => {
        this.organisationId = params.get('organisationId');
        return this.organisationService.getAllWorkspaces(this.organisationId || "").pipe(
          map((data) => {
            return Array.from({length: data.length},
              (_, n) => ({'data': data[n]}))
          })
        );
      })
    );
  }

  ngOnInit(): void {

  }

  onWorkspaceClick(target: any) {
    this.router.navigateByUrl(`/${this.organisationId}/${target.data.name}`)
  }
}
