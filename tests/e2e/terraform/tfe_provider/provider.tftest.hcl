provider "tfe" {
  hostname = "terrarun"
}

variables {
  terraform_version_for_api_import    = "1.5.5"
  terraform_version_for_string_import = "1.6.6"
}

run "setup" {
  module {
    source = "./setup"
  }
}

run "test" {
  variables {
    terraform_version_api_id = run.setup.import_api_id
  }

  ################################
  # Organizations                #
  ################################

  # Check that list data source works
  assert {
    # Compare as sets to ignore order
    # Default created in initial_setup.py. smoke-test-org created in run_tests.sh
    condition     = toset(data.tfe_organizations.test.names) == toset(["default", "smoke-test-org", "test-read", "test-import"])
    error_message = "Organisation list incorrect: ${jsonencode(data.tfe_organizations.test.names)}."
  }

  # Check that item data source returns correct item
  assert {
    # Compare as sets to ignore order
    condition     = data.tfe_organization.test.id == run.setup.organization_read_id
    error_message = "Read item id does not match: ${data.tfe_organization.test.id} != ${run.setup.organization_read_id}."
  }
  assert {
    # Compare as sets to ignore order
    condition     = data.tfe_organization.test.name == "test-read"
    error_message = "Read item name does not match expected."
  }
  assert {
    # Compare as sets to ignore order
    condition     = data.tfe_organization.test.email == "test-read@company.com"
    error_message = "Read item email does not match expected."
  }

  # Verify correct org was imported and modifications were applied
  assert {
    condition     = tfe_organization.test_import.id == run.setup.organization_import_id
    error_message = "Wrong organization was imported."
  }
  assert {
    condition     = tfe_organization.test_import.name == "test-import-updated"
    error_message = "Org name should have been updated."
  }
  assert {
    condition     = tfe_organization.test_import.email == "test-import-updated@company.com"
    error_message = "Org email should have been updated."
  }

  # Check that a new org was correctly created with expected params
  assert {
    condition     = tfe_organization.test_create.name == "test-create"
    error_message = "Failed to set parameter name for new organisation"
  }
  assert {
    condition     = tfe_organization.test_create.email == "test-create@company.com"
    error_message = "Failed to set parameter email for new organisation"
  }
  assert {
    condition     = tfe_organization.test_create.session_timeout_minutes == 120
    error_message = "Failed to set parameter session_timeout_minutes for new organisation"
  }
  assert {
    condition     = tfe_organization.test_create.session_remember_minutes == 240
    error_message = "Failed to set parameter session_remember_minutes for new organisation"
  }
  assert {
    condition     = tfe_organization.test_create.collaborator_auth_policy == "password"
    error_message = "Failed to set parameter collaborator_auth_policy for new organisation"
  }
  assert {
    condition     = tfe_organization.test_create.owners_team_saml_role_id == "terrarun-admin"
    error_message = "Failed to set parameter owners_team_saml_role_id for new organisation"
  }
  assert {
    condition     = tfe_organization.test_create.cost_estimation_enabled == true
    error_message = "Failed to set parameter cost_estimation_enabled for new organisation"
  }
  assert {
    condition     = tfe_organization.test_create.send_passing_statuses_for_untriggered_speculative_plans == true
    error_message = "Failed to set parameter send_passing_statuses_for_untriggered_speculative_plans for new organisation"
  }
  assert {
    condition     = tfe_organization.test_create.aggregated_commit_status_enabled == true
    error_message = "Failed to set parameter aggregated_commit_status_enabled for new organisation"
  }
  assert {
    condition     = tfe_organization.test_create.assessments_enforced == true
    error_message = "Failed to set parameter assessments_enforced for new organisation"
  }
  assert {
    condition     = !tfe_organization.test_create.allow_force_delete_workspaces
    error_message = "Failed to set parameter allow_force_delete_workspaces for new organisation"
  }

  ##################################
  # Organizations Default Settings #
  ##################################

  assert {
    condition     = tfe_organization_default_settings.test_create.organization == "test-create"
    error_message = "Set settings for wrong organisation ${tfe_organization_default_settings.test_create.organization}."
  }
  assert {
    condition     = tfe_organization_default_settings.test_create.default_execution_mode == "local"
    error_message = "Expected: local. Actual: ${tfe_organization_default_settings.test_create.default_execution_mode}."
  }
  assert {
    condition     = tfe_organization_default_settings.test_create.default_agent_pool_id == null
    error_message = "Expected: null. Actual: ${jsonencode(tfe_organization_default_settings.test_create.default_agent_pool_id)}."
  }
  assert {
    condition     = tfe_organization_default_settings.test_import.organization == tfe_organization.test_import.name
    error_message = "Set settings for wrong organisation ${tfe_organization_default_settings.test_import.organization}."
  }
  assert {
    condition     = tfe_organization_default_settings.test_import.default_execution_mode == "agent"
    error_message = "Expected: agent. Actual: ${tfe_organization_default_settings.test_import.default_execution_mode}."
  }
  assert {
    condition     = tfe_organization_default_settings.test_import.default_agent_pool_id == "abcd"
    error_message = "Expected: abcd. Actual: ${jsonencode(tfe_organization_default_settings.test_import.default_agent_pool_id)}."
  }

  ################################
  # Terraform Versions           #
  ################################

  # Verify that imported by api id was modified as expected
  assert {
    condition     = tfe_terraform_version.imported_by_api_id.version == var.terraform_version_for_api_import
    error_message = "Version does not match."
  }
  assert {
    condition     = tfe_terraform_version.imported_by_api_id.url == "https://releases.hashicorp.com/terraform/${var.terraform_version_for_api_import}/terraform_${var.terraform_version_for_api_import}_linux_amd64.zip"
    error_message = "url does not match."
  }
  assert {
    condition     = tfe_terraform_version.imported_by_api_id.sha == "e75ac73deb69a6b3aa667cb0b8b731aee79e2904"
    error_message = "sha does not match."
  }
  assert {
    condition     = tfe_terraform_version.imported_by_api_id.deprecated
    error_message = "deprecated should be true."
  }
  assert {
    condition     = tfe_terraform_version.imported_by_api_id.deprecated_reason == "This is an older version"
    error_message = "deprecated-reason does not match."
  }
  assert {
    # Terraform provider cannot create official versions, because it url is required.
    condition     = !tfe_terraform_version.imported_by_api_id.official
    error_message = "official should be false."
  }
  assert {
    condition     = tfe_terraform_version.imported_by_api_id.enabled
    error_message = "enabled should be true."
  }
  assert {
    condition     = !tfe_terraform_version.imported_by_api_id.beta
    error_message = "beta should be false."
  }

  # Verify that imported by version string was modified as expected
  assert {
    condition     = tfe_terraform_version.imported_by_version.version == var.terraform_version_for_string_import
    error_message = "Version does not match."
  }
  assert {
    condition     = tfe_terraform_version.imported_by_version.url == "https://releases.hashicorp.com/terraform/${var.terraform_version_for_string_import}/terraform_${var.terraform_version_for_string_import}_linux_amd64.zip"
    error_message = "url does not match."
  }
  assert {
    condition     = tfe_terraform_version.imported_by_version.sha == "e75ac73deb69a6b3aa667cb0b8b731aee79e2904"
    error_message = "sha does not match."
  }
  assert {
    condition     = !tfe_terraform_version.imported_by_version.deprecated
    error_message = "deprecated should be false."
  }
  assert {
    condition     = tfe_terraform_version.imported_by_version.deprecated_reason == ""
    error_message = "deprecated-reason should be empty."
  }
  assert {
    # Terraform provider cannot create official versions, because it url is required.
    condition     = !tfe_terraform_version.imported_by_version.official
    error_message = "official should be false."
  }
  assert {
    condition     = !tfe_terraform_version.imported_by_version.enabled
    error_message = "enabled should be false."
  }
  assert {
    condition     = !tfe_terraform_version.imported_by_version.beta
    error_message = "beta should be false."
  }
}
