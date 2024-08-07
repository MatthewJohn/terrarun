terraform {
  required_providers {
    tfe = {
      version = "~> 0.57.0"
    }
  }
}

provider "tfe" {
  hostname = "terrarun"
}

variable "tfe_token" {

}

resource "tfe_organization" "test" {
  name  = "smoke-test-org"
  email = "smoke-test-org@company.com"
}

module "test_lifecycle" {
  source = "../../modules/curl_create"

  tfe_token  = var.tfe_token
  path       = "/api/v2/organizations/${tfe_organization.test.name}/lifecycles"
  type       = "lifecycles"
remove_by_name = true
  attributes = {
    "name" : "smoke-test-lifecycle",
  }
}

locals {
  version = "1.9.3"
}

resource "tfe_terraform_version" "test" {
  version = local.version
  url     = "https://releases.hashicorp.com/terraform/${local.version}/terraform_${local.version}_linux_amd64.zip"
  sha     = "e75ac73deb69a6b3aa667cb0b8b731aee79e2904"
}

module "test_project" {
  source = "../../modules/curl_create"

  tfe_token   = var.tfe_token
  path        = "/api/v2/organizations/${tfe_organization.test.name}/projects"
  remove_path = "/api/v2/projects"

  type = "projects"
  attributes = {
    "name"      = "smoke-test-project",
    "lifecycle" = module.test_lifecycle.api_id,
    "description":"Smoke Test Project",
    "terraform-version": tfe_terraform_version.test.version
  }
}
