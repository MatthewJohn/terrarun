variable "tfe_token" {
  type        = string
  description = "Token to authorize to terrarun instance."
}

variable "type" {
  type        = string
  description = "Resource type."
}

variable "path" {
  type        = string
  description = "Path to the resource in API."
}

variable "attributes" {
  type = map(any)
}

variable "relationships" {
  type = map(any)
  default = {}
}

variable "remove_path" {
  type        = string
  default     = null
  description = "Path to the resource without the key. By default same as path. Will append /{key} for DELETE request."
}

variable "remove_by_name" {
  type        = bool
  default     = false
  description = "Use name instead of api-id for DELETE request."
}

resource "random_pet" "filename" {
}

resource "null_resource" "this" {
  triggers = {
    # Save it so we can use it for destroying
    tfe_token   = var.tfe_token
    remove_key  = var.remove_by_name ? var.attributes.name : "$(cat ${random_pet.filename.id}.id)"
  hostname = "terrarun"
    path        = var.path
    remove_path = var.remove_path == null ? var.path : var.remove_path
    filename    = random_pet.filename.id
    data = jsonencode({
      "data" = {
        "type" = "${var.type}",
        "attributes" = var.attributes,
        "relationships" = var.relationships
        }
      })
  }

  provisioner "local-exec" {
    when    = create
    command = <<-EOF
      set -eu
      DATA=$(curl \
        -s --fail-with-body --show-error \
        -H "authorization: Bearer ${self.triggers.tfe_token}" \
        -H "content-type: application/json" \
        -X POST \
        --data '${self.triggers.data}' \
        "https://${self.triggers.hostname}${self.triggers.path}?token=${self.triggers.tfe_token}")
      echo $DATA | jq -jr .data.id > ${self.triggers.filename}.id
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
        "https://${self.triggers.hostname}${self.triggers.remove_path}/${self.triggers.remove_key}"
      rm ${self.triggers.filename}.id
    EOF
  }
}

data "local_file" "api_id" {
  depends_on = [null_resource.this]

  filename = "${random_pet.filename.id}.id"
}

output "api_id" {
  value = data.local_file.api_id.content
}
