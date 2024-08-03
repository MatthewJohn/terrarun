terraform {
  cloud {
    organization = "smoke-test-org"
    hostname = "terrarun"

    workspaces {
      name = "smoketest-dev"
    }
  }
}

variable "input_version" {
  type = string
}

resource "null_resource" "test" {
  for_each = toset([var.input_version])
}

output "test_output" {
  value = "test_value-${var.input_version}"
}