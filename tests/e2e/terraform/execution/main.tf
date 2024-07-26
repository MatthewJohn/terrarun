terraform {
  cloud {
    organization = "smoke-test-org"
    hostname = "terrarun"

    workspaces {
      name = "smoketest-dev"
    }
  }
}

resource "null_resource" "test" { }
