import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExecutionModeSelectComponent } from './execution-mode-select.component';

describe('ExecutionModeSelectComponent', () => {
  let component: ExecutionModeSelectComponent;
  let fixture: ComponentFixture<ExecutionModeSelectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExecutionModeSelectComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExecutionModeSelectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
