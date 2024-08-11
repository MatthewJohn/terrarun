run "test_plan" {
  command = plan
  variables {
  }
}

run "test" {
  assert {
    # Ensure output contains correct value
    condition     = output.test_output == "test_value-Until cmd vars fixed"
    error_message = "Unexpected test output: ${jsonencode(output.test_output)}."
  }
}