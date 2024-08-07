# Test importing
variable "project_import_api_id" {
  type        = string
  description = "Api-id of project that should be imported."
}

import {
  id = var.project_import_api_id
  to = tfe_project.test_import
}

resource "tfe_project" "test_import" {
  organization = tfe_organization.test_create.name
  name         = "test-import-updated"
  description  = "This is an added description."
}

resource "tfe_project" "test_create" {
  organization = tfe_organization.test_create.name
  name         = "test-create"
  description  = "This is a project description"
}

resource "tfe_project" "test_create_no_description" {
  organization = tfe_organization.test_create.name
  name         = "test-create-no_description"
}