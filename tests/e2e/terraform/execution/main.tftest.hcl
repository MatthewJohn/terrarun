run "setup" {
  module {
    source = "./setup"
  }
}

run "test_plan" {
  command = plan
  variables {
  }
}

run "test" {
  assert {
    # Ensure output contains correct value
    condition     = test_output == "test_value"
    error_message = "Unexpected test output: ${jsonencode(test_output)}."
  }
}