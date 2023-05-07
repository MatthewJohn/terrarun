import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VcsSelectionComponent } from './vcs-selection.component';

describe('VcsSelectionComponent', () => {
  let component: VcsSelectionComponent;
  let fixture: ComponentFixture<VcsSelectionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VcsSelectionComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(VcsSelectionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
