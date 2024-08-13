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

variable "organization_name" {
  type = string
  default = "smoke-test-org"
}

variable "project_name" {
  type = string
  default = "smoketestproject"
}

variable "tfe_token" {

}

locals {
  version = "1.9.1"
}


resource "tfe_organization" "test" {
  name  = var.organization_name
  email = "smoke-test-org@company.com"
}

module "test_lifecycle" {
  source = "../modules/curl_create"

  tfe_token  = var.tfe_token
  path       = "/api/v2/organizations/${tfe_organization.test.name}/lifecycles"
  type       = "lifecycles"
  attributes = {
    "name" : "smoke-test-lifecycle",
  }
}

module "test_environment" {
  source = "../modules/curl_create"

  tfe_token  = var.tfe_token
  path       = "/api/v2/organizations/${tfe_organization.test.name}/environments"
  type       = "environments"
  attributes = {
    "name" : "testenv",
  }
}

module "test_lifecycle_environment_group" {
  source = "../modules/curl_create"

  tfe_token  = var.tfe_token
  path       = "/api/v2/lifecycles/${module.test_lifecycle.api_id}/lifecycle-environment-groups"
  remove_path = "/api/v2/lifecycle-environment-groups"
  type       = ""
  attributes = {  }
}

module "test_lifecycle_environment" {
  source = "../modules/curl_create"

  tfe_token  = var.tfe_token
  path       = "/api/v2/lifecycle-environment-groups/${module.test_lifecycle_environment_group.api_id}/lifecycle-environments"
  remove_path = "/api/v2/lifecycle-environment-groups"
  type       = "lifecycle-environments"
  attributes = {  }
  relationships = {
    "environment" = {
      "data" = {
        "type" = "environments",
        "id" = module.test_environment.api_id
      }
    }
  }
}



resource "tfe_terraform_version" "test" {
  version = "${local.version}-smoke-test"
  url     = "https://releases.hashicorp.com/terraform/${local.version}/terraform_${local.version}_linux_amd64.zip"
  sha     = "e75ac73deb69a6b3aa667cb0b8b731aee79e2904"
}

module "test_project" {
  source = "../modules/curl_create"

  tfe_token   = var.tfe_token
  path        = "/api/v2/organizations/${tfe_organization.test.name}/projects"
  remove_path = "/api/v2/projects"

  type = "projects"
  attributes = {
    "name"      = var.project_name
    "lifecycle" = module.test_lifecycle.api_id,
    "description":"Smoke Test Project",
    "terraform-version": tfe_terraform_version.test.version
  }
}
