import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

@Component({
  selector: 'execution-mode-select',
  templateUrl: './execution-mode-select.component.html',
  styleUrls: ['./execution-mode-select.component.scss']
})
export class ExecutionModeSelectComponent implements OnInit {

  @Input()
  value: string = "";

  @Input()
  allowInheritanceFrom: string = "";

  @Input()
  title: string = "Execution mode";

  @Output()
  valueChange = new EventEmitter<string>();

  constructor() { }

  ngOnInit(): void {
  }

}
