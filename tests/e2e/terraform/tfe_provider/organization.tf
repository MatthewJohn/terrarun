# Data sources

data "tfe_organizations" "test" {
}

data "tfe_organization" "test" {
  name = "test-read"
}


# Importing

import {
  id = "test-import"
  to = tfe_organization.test_import
}

resource "tfe_organization" "test_import" {
  name  = "test-import-updated"
  email = "test-import-updated@company.com"

  lifecycle {
    # Terrarun does not allow destroying orgs
    #prevent_destroy = true
  }
}

# Creating with all params

resource "tfe_organization" "test_create" {
  name  = "test-create"
  email = "test-create@company.com"

  session_timeout_minutes                                 = 120
  session_remember_minutes                                = 240
  collaborator_auth_policy                                = "password"
  owners_team_saml_role_id                                = "terrarun-admin"
  cost_estimation_enabled                                 = true
  send_passing_statuses_for_untriggered_speculative_plans = true
  aggregated_commit_status_enabled                        = true
  assessments_enforced                                    = true
  allow_force_delete_workspaces                           = true

  lifecycle {
    # Terrarun does not allow destroying orgs
    #prevent_destroy = true
  }
}

