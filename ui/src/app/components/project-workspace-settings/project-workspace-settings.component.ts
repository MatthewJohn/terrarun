import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { ProjectAttributes } from 'src/app/interfaces/project';
import { WorkspaceAttributes, WorkspaceUpdateAttributes } from 'src/app/interfaces/workspace';

@Component({
  selector: 'project-workspace-settings',
  templateUrl: './project-workspace-settings.component.html',
  styleUrls: ['./project-workspace-settings.component.scss']
})
export class ProjectWorkspaceSettingsComponent implements OnInit {

  @Input()
  set attributes(value: WorkspaceUpdateAttributes | ProjectAttributes | null) {
    this.inputAttributes = value;
    if (value && "overrides" in value) {
      this.overrides['queue-all-runs'] = value.overrides["queue-all-runs"];
    }
  }
  inputAttributes: WorkspaceUpdateAttributes | ProjectAttributes | null = null;

  @Output()
  attributesChange = new EventEmitter();

  overrides: {
    "queue-all-runs": boolean | null | undefined
  } = {
    "queue-all-runs": undefined
  };

  @Input()
  projectAttributes: ProjectAttributes | null = null;

  constructor() { }

  ngOnInit(): void {
  }

  onQueueAllRunsChange(value: boolean) {
    if (this.inputAttributes) {
      this.inputAttributes['queue-all-runs'] = value;

      if ("overrides" in this.inputAttributes && this.overrides['queue-all-runs'] !== undefined) {
        this.inputAttributes.overrides['queue-all-runs'] = this.overrides['queue-all-runs'];
      }

      this.emitChange();
    }
  }

  emitChange(): void {
    this.attributesChange.emit(this.inputAttributes);
  }

  overrideQueueAllRuns() {
    if (this.inputAttributes && "overrides" in this.inputAttributes) {
      this.overrides['queue-all-runs'] = this.inputAttributes['queue-all-runs'];
    }
  }
  unOverrideQueueAllRuns() {
    if (this.inputAttributes && "overrides" in this.inputAttributes) {
      this.overrides['queue-all-runs'] = null;
      if (this.projectAttributes) {
        this.inputAttributes['queue-all-runs'] = this.projectAttributes['queue-all-runs'];
      }
    }
  }
}
