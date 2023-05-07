import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ErrorDialogueComponent } from './error-dialogue.component';

describe('ErrorDialogueComponent', () => {
  let component: ErrorDialogueComponent;
  let fixture: ComponentFixture<ErrorDialogueComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ErrorDialogueComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ErrorDialogueComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
