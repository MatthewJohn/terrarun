variable "tfe_token" {
  type        = string
  description = "Token to authorize to terrarun instance."
}

variable "terraform_version_for_string_import" {
  type        = string
  description = "Version to create for importing by string"
}

variable "terraform_version_for_api_import" {
  type        = string
  description = "Version to create for importing by string"
}

resource "tfe_terraform_version" "version_for_import_by_version" {
  # This cannot be changed in terrarun and will be ignored
  version = var.terraform_version_for_string_import
  url     = "https://releases.hashicorp.com/terraform/${var.terraform_version_for_string_import}/terraform_${var.terraform_version_for_string_import}_linux_amd64.zip"
  sha     = "incorrect"
}

resource "null_resource" "version_for_import_by_api_id" {
  triggers = {
    # Save it so we can use it for destroying
    tfe_token = var.tfe_token
  }

  provisioner "local-exec" {
    when    = create
    command = <<-EOF
      set -eu
      DATA=$(curl \
        -s --fail --show-error \
        -H "authorization: Bearer ${self.triggers.tfe_token}" \
        -H "content-type: application/json" \
        -X POST \
        --data '{"data": {"type": "terraform-versions", "attributes": {"version": "${var.terraform_version_for_api_import}"}}}' \
        "https://terrarun/api/v2/admin/terraform-versions?token=${self.triggers.tfe_token}")
      echo $DATA | jq -jr .data.id > version_for_import_by_api_id.id
    EOF
  }

  # This might have been already removed.
  provisioner "local-exec" {
    when    = destroy
    command = <<-EOF
      set -eu
      curl \
        -s --show-error \
        -H "authorization: Bearer ${self.triggers.tfe_token}" \
        -H "content-type: application/json" \
        -X DELETE \
        "https://terrarun/api/v2/admin/terraform-versions/$(cat version_for_import_by_api_id.id)"
      rm version_for_import_by_api_id.id
    EOF
  }
}

data "local_file" "api_id" {
  depends_on = [null_resource.version_for_import_by_api_id]

  filename = "version_for_import_by_api_id.id"
}

output "import_api_id" {
  value = data.local_file.api_id.content
}
