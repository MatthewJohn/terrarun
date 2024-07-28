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
  set attributes(value: WorkspaceAttributes | ProjectAttributes | null) {
    this.inputAttributes = value;
    if (value && "setting-overwrites" in value && "queue-all-runs" in value['setting-overwrites']) {
      this.overrides['queue-all-runs'] = value['setting-overwrites']["queue-all-runs"];
    }
  }
  inputAttributes: WorkspaceAttributes | ProjectAttributes | null = null;

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

      // If overrides are present and overrides were present,
      // update the overrides value, to be used to emitted as update.
      if (this.overrides['queue-all-runs'] !== undefined && this.overrides['queue-all-runs'] !== null) {
        this.overrides['queue-all-runs'] = this.inputAttributes['queue-all-runs'];
      }

      this.emitChange();
    }
  }

  emitChange(): void {
    if (this.inputAttributes) {
      if ("setting-overwrites" in this.inputAttributes) {
        // Emit override changes
        let updates: WorkspaceUpdateAttributes = {
          "queue-all-runs": this.overrides['queue-all-runs'],
          "vcs-repo": undefined,
          "file-triggers-enabled": undefined,
          "trigger-patterns": undefined,
          "trigger-prefixes": undefined
        };
        this.attributesChange.emit(updates);
      } else {
        this.attributesChange.emit(this.inputAttributes);
      }
    }
  }

  overrideQueueAllRuns() {
    if (this.inputAttributes && "setting-overwrites" in this.inputAttributes) {
      this.overrides['queue-all-runs'] = this.inputAttributes['queue-all-runs'];
      this.emitChange();
    }
  }
  unOverrideQueueAllRuns() {
    if (this.inputAttributes && "setting-overwrites" in this.inputAttributes) {
      // Emit update change to set override back to null
      this.overrides['queue-all-runs'] = null;
      this.emitChange();

      // Revert value to project value
      if (this.projectAttributes) {
        this.inputAttributes['queue-all-runs'] = this.projectAttributes['queue-all-runs'];
      }
    }
  }
}
