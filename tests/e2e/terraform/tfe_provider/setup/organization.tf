resource "tfe_organization" "test_import_setup" {
  name  = "test-import"
  email = "test-import@company.com"

  lifecycle {
    # Terrarun does not allow destroying orgs
    #prevent_destroy = true
  }
}

resource "tfe_organization" "test_read_setup" {
  name  = "test-read"
  email = "test-read@company.com"

  lifecycle {
    # Terrarun does not allow destroying orgs
    #prevent_destroy = true
  }
}

output "organization_import_id" {
  value = tfe_organization.test_import_setup.id
}

output "organization_read_id" {
  value = tfe_organization.test_read_setup.id
}
