import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

@Component({
  selector: 'execution-mode-select',
  templateUrl: './execution-mode-select.component.html',
  styleUrls: ['./execution-mode-select.component.scss']
})
export class ExecutionModeSelectComponent implements OnInit {

  @Input()
  value: string | null = null;

  @Input()
  allowInheritanceFrom: string = "";

  @Input()
  title: string = "Execution mode";

  @Output()
  valueChange = new EventEmitter<string|null>();

  constructor() { }

  ngOnInit(): void {
  }

  onChange(value: string) {
    let newValue: string|null = value;
    // Convert "none" string value to null value
    if (value == "none") {
      newValue = null;
    }
    this.valueChange.emit(newValue);
  }
}
