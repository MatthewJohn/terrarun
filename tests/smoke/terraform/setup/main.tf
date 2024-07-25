terraform {
  required_providers {
    tfe = {
      version = "~> 0.57.0"
    }
  }
}

provider "tfe" {
  hostname = "localhost"
}

resource "tfe_organization" "test" {
  name  = "smoke-test-org"
  email = "smoke-test-org@company.com"
}

