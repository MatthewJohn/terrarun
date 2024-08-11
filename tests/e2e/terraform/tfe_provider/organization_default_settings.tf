resource "tfe_organization_default_settings" "test_create" {
  organization           = tfe_organization.test_create.name
  default_execution_mode = "local"
}

resource "tfe_organization_default_settings" "test_import" {
  organization           = tfe_organization.test_import.name
  default_execution_mode = "agent"
  default_agent_pool_id  = "abcd"
}
