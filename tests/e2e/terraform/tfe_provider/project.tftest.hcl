provider "tfe" {
  hostname = "terrarun"
}

variables {
  terraform_version_for_api_import    = "1.5.5"
  terraform_version_for_string_import = "1.6.6"
}

run "setup" {
  module {
    source = "./modules/setup"
  }

  plan_options {
    target = [module.test_import_setup]
  }

  assert {
    condition     = output.project_import_api_id != null
    error_message = "Need project api id for importing."
  }
}

run "test" {
  variables {
    terraform_version_api_id = run.setup.import_api_id
    project_import_api_id    = run.setup.project_import_api_id
  }

  plan_options {
    target = [
      tfe_project.test_create,
      tfe_project.test_create_no_description,
      tfe_project.test_import,
    ]
  }
}
