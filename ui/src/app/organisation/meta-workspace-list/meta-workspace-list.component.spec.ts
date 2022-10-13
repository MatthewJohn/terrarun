import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';

import { MetaWorkspaceListComponent } from './meta-workspace-list.component';

describe('MetaWorkspaceListComponent', () => {
  let component: MetaWorkspaceListComponent;
  let fixture: ComponentFixture<MetaWorkspaceListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MetaWorkspaceListComponent ],
      imports: [ HttpClientTestingModule, RouterTestingModule, ReactiveFormsModule ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MetaWorkspaceListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
