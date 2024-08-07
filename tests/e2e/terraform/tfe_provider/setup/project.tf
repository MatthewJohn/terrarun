module "test_lifecycle" {
  source = "../curl_create"

  tfe_token  = var.tfe_token
  path       = "/api/v2/organizations/${tfe_organization.test_import_setup.name}/lifecycles"
  type       = "lifecycles"
remove_by_name = true
  attributes = {
    "name" : "test-lifecycle",
  }
}


module "test_import_setup" {
  source = "../curl_create"

  tfe_token   = var.tfe_token
  path        = "/api/v2/organizations/${tfe_organization.test_import_setup.name}/projects"
  remove_path = "/api/v2/projects"

  type = "projects"
  attributes = {
    "name"      = "test-import",
    "lifecycle" = module.test_lifecycle.api_id
  }
}


output "project_import_api_id" {
  value = module.test_import_setup.api_id
}

/*
resource "tfe_project" "test_import_setup" {
  organization = tfe_organization.test_import_setup.name
  name         = "test-import"
}

output "project_import_api_id" {
    value = tfe_project.test_import_setup.id
}
*/