import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { ProjectAttributes } from 'src/app/interfaces/project';
import { WorkspaceAttributes } from 'src/app/interfaces/workspace';

@Component({
  selector: 'project-workspace-settings',
  templateUrl: './project-workspace-settings.component.html',
  styleUrls: ['./project-workspace-settings.component.scss']
})
export class ProjectWorkspaceSettingsComponent implements OnInit {

  @Input()
  attributes: WorkspaceAttributes | ProjectAttributes | null = null;

  @Output()
  attributesChange = new EventEmitter();

  constructor() { }

  ngOnInit(): void {
  }

  onQueueAllRunsChange(value: boolean) {
    if (this.attributes) {
      this.attributes['queue-all-runs'] = value;
      this.attributesChange.emit(this.attributes);
    }
  }
}
