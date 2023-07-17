import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProjectWorkspaceSettingsComponent } from './project-workspace-settings.component';

describe('ProjectWorkspaceSettingsComponent', () => {
  let component: ProjectWorkspaceSettingsComponent;
  let fixture: ComponentFixture<ProjectWorkspaceSettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ProjectWorkspaceSettingsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ProjectWorkspaceSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
