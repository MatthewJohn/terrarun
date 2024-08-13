variable "terraform_version_api_id" {
  type        = string
  description = "Tool id for the terraform-version we should import."
}

variable "terraform_version_for_string_import" {
  type        = string
  description = "Version for the terraform-version we should import."
}

variable "terraform_version_for_api_import" {
  type        = string
  description = "Version for the terraform-version we should import."
}

# Import using tool-id
import {
  id = var.terraform_version_api_id
  to = tfe_terraform_version.imported_by_api_id
}

# Import using version string
import {
  id = var.terraform_version_for_string_import
  to = tfe_terraform_version.imported_by_version
}

# Resources

resource "tfe_terraform_version" "imported_by_api_id" {
  # This cannot be changed in terrarun and will be ignored
  version = "2.0.1"
  url     = "https://releases.hashicorp.com/terraform/${var.terraform_version_for_api_import}/terraform_${var.terraform_version_for_api_import}_linux_amd64.zip"
  sha     = "e75ac73deb69a6b3aa667cb0b8b731aee79e2904"
  # This argument is calculated dynamically in terrarun and will be ignored
  official          = true
  enabled           = true
  beta              = false
  deprecated        = true
  deprecated_reason = "This is an older version"
}

resource "tfe_terraform_version" "imported_by_version" {
  # This cannot be changed in terrarun and will be ignored
  version = "2.0.1"
  url     = "https://releases.hashicorp.com/terraform/${var.terraform_version_for_string_import}/terraform_${var.terraform_version_for_string_import}_linux_amd64.zip"
  sha     = "e75ac73deb69a6b3aa667cb0b8b731aee79e2904"
  # This argument is calculated dynamically in terrarun and will be ignored
  official = false
  enabled  = false
  beta     = true
}
